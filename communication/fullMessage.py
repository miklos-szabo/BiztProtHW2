import uuid

from Crypto.PublicKey.RSA import RsaKey

from communication.message import Message
from typing import List
import math
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256


class FullMessage:
    sessionId: uuid
    username: bytes
    command: str
    clientAddress: str
    clientToServer: bool
    messagesCount: int
    messages: List[Message]
    encryptedMessages: List[bytes]
    file: bytes     # All bytes of the file, also used for listing files
    path: str
    password: bytes      #LGN
    clientPublicKey: str     #HDS
    randomString: str    #HDS
    replyStatus: str

    def __init__(self, sessionId: uuid,  command: str, clientAddress: str, username: bytes = b'',
                 clientToServer:bool = True, file: bytes = b'', path: str = "/",
                 password: bytes = b'', clientKey: str = b'', randomString: str = "", replyStatus: str = ""):
        self.sessionId = sessionId
        self.username = username
        self.command = command
        self.clientAddress = clientAddress
        self.clientToServer = clientToServer
        self.file = file
        self.path = path
        self.password = password
        self.clientPublicKey = clientKey
        self.randomString = randomString
        self.replyStatus = replyStatus
        self.messages = []
        self.encryptedMessages = []
        self.messagesCount = 0

    def createMessages(self):
        self.__constructMessagesAsClient() if self.clientToServer else self.__contructMessagesAsServer()
        self.__updateMessagesCount()  # So that all the headers have the right count

    def __constructMessagesAsClient(self):    # Add the base message here, without the signature
        if self.command == "HDS":
            self.__addAsMessage(self.clientPublicKey.encode('ascii'))
            self.__addAsMessage(self.randomString.encode('ascii'))

        elif self.command == "LGN":
            self.__addAsMessage(self.password)

        elif self.command == "MKD" or self.command == "RMD" or self.command == "CWD":
            self.__addAsMessage(self.path.encode('ascii'))

        elif self.command == "GWD":
            self.__addAsMessage(b'empty')

        elif self.command == "LST":
            self.__addAsMessage(self.path.encode('ascii'))

        elif self.command == "UPL":
            self.__addAsMessage(self.path.encode('ascii'))
            self.__addAsMessage(self.file)

        elif self.command == "DNL":
            self.__addAsMessage(self.path.encode('ascii'))

        elif self.command == "RMF":
            self.__addAsMessage(self.path.encode('ascii'))

        else:
            raise Exception("Unknown command type!")



    def __contructMessagesAsServer(self):
        if self.command == "HDS":
            self.__addAsMessage(self.randomString.encode('ascii'))

        elif self.command == "LGN":
            self.__addAsMessage(self.replyStatus.encode('ascii'))

        elif self.command == "MKD" or self.command == "RMD" or self.command == "CWD":
            self.__addAsMessage(self.replyStatus.encode('ascii'))

        elif self.command == "GWD":
            self.__addAsMessage(self.path.encode('ascii'))

        elif self.command == "LST":
            self.__addAsMessage(self.path.encode('ascii'))

        elif self.command == "UPL":
            self.__addAsMessage(self.replyStatus.encode('ascii'))

        elif self.command == "DNL":
            self.__addAsMessage(self.path.encode('ascii'))
            self.__addAsMessage(self.file)

        elif self.command == "RMF":
            self.__addAsMessage(self.replyStatus.encode('ascii'))

        else:
            raise Exception("Unknown command type!")

    def __addAsMessage(self, messageBytes: bytes):
        if len(messageBytes) == 0:  # if the message is empty, add an empty message object - only the header
            self.messages.append(Message(self.sessionId, self.username, self.command, self.clientAddress, 0, self.messagesCount + 1,
                                         b''))
        else:
            for i in range(0, math.ceil(len(messageBytes) / 256)):  # Add a message for every 256 byte
                self.messages.append(Message(self.sessionId, self.username, self.command, self.clientAddress, 0, self.messagesCount + 1,
                                             messageBytes[i * 256: (i + 1) * 256 if (i + 1) * 256 <= len(messageBytes) else len(messageBytes)]))
                self.messagesCount += 1

    # The added message count was wrong when the messages were added, update them here to the right value
    def __updateMessagesCount(self):
        for message in self.messages:
            message.messagesCount = self.messagesCount


    @classmethod
    def fromMessages(cls, messages: List[Message], clientToServer: bool):
        firstMessage = messages[0]
        fullMessage = cls(firstMessage.sessionId, firstMessage.command, firstMessage.origin,
                                  firstMessage.username, clientToServer=clientToServer)
        fullMessage.__parseAsServer(messages) if clientToServer else fullMessage.__parseAsClient(messages)
        return fullMessage


    def __parseAsClient(self, messages: List[Message]):
        if self.command == "HDS":
            self.randomString = (messages[0].data + messages[1].data).decode('ascii')

        elif self.command == "LGN":
            self.replyStatus = messages[0].data.decode('ascii')

        elif self.command == "MKD" or self.command == "RMD" or self.command == "CWD":
            self.replyStatus = messages[0].data.decode('ascii')

        elif self.command == "GWD":
            self.path = messages[0].data.decode('ascii')

        elif self.command == "LST":
            allPaths: bytes = b''
            for msg in messages[:-2]:
                allPaths += msg.data
            self.path = allPaths.decode('ascii')

        elif self.command == "UPL":
            self.replyStatus = messages[0].data.decode('ascii')

        elif self.command == "DNL":
            self.path = messages[0].data.decode('ascii')
            wholeFile: bytes = b''
            for msg in messages[1:-2]:
                wholeFile += msg.data
            self.file = wholeFile

        elif self.command == "RMF":
            self.replyStatus = messages[0].data.decode('ascii')

        else:
            raise Exception("Unknown command type!")

    def __parseAsServer(self, messages: List[Message]):
        if self.command == "HDS":
            self.clientPublicKey = (messages[0].data + messages[1].data + messages[2].data + messages[3].data).decode('ascii')
            self.randomString = (messages[4].data + messages[5].data).decode('ascii')

        elif self.command == "LGN":
            self.password = messages[0].data

        elif self.command == "MKD" or self.command == "RMD" or self.command == "CWD":
            self.path = messages[0].data.decode('ascii')

        elif self.command == "GWD":
            return  # GWD üzenet üres

        elif self.command == "LST":
            self.path = messages[0].data.decode('ascii')

        elif self.command == "UPL":
            self.path = messages[0].data.decode('ascii')
            wholeFile: bytes = b''
            for msg in messages[1:-2]:
                wholeFile += msg.data
            self.file = wholeFile

        elif self.command == "DNL":
            self.path = messages[0].data.decode('ascii')

        elif self.command == "RMF":
            self.path = messages[0].data.decode('ascii')

        else:
            raise Exception("Unknown command type!")


    def addSignatureMessages(self, keyPass: str):
        if self.command == "HDS":
            return

        self.messagesCount += 2         # signature is 2 messages long
        self.__updateMessagesCount()    # messages have to show the higher message count or signature validation fails
        self.messagesCount -= 2         # when adding the signature, the message number would be wrong

        allMessagesAsBytes: bytes = b''
        for message in self.messages:
            allMessagesAsBytes += message.toBytes()

        h = SHA256.new(allMessagesAsBytes)

        if self.clientToServer:
            clientkfile = open('client/client-keypair.pem', 'r')
            clientkeypairStr = clientkfile.read()
            clientkfile.close()
            key = RSA.import_key(clientkeypairStr, passphrase=keyPass)  # Client private key

        else:
            serverkfile = open('server/server-keypair.pem', 'r')
            serverkeypairStr = serverkfile.read()
            serverkfile.close()
            key = RSA.import_key(serverkeypairStr, passphrase=keyPass)  # Server private key

        signer = PKCS1_PSS.new(key)
        signature = signer.sign(h)

        allMessagesCount = self.messagesCount + 2
        for i in range(0, 2):
            self.messages.append(
                Message(self.sessionId, self.username, self.command, self.clientAddress, allMessagesCount, self.messagesCount + 1,
                        signature[i * 256: (i + 1) * 256 if (i + 1) * 256 <= len(signature) else len(signature)]))
            self.messagesCount += 1

        # already updated the other messages with the correct message count (+2)

    def encryptMessages(self):
        if self.clientToServer:
            kfile = open('client/server-publKey.pem', 'r')
            pubkeystr = kfile.read()
            kfile.close()
            otherPublicKey = RSA.import_key(pubkeystr)

        else:
            otherPublicKey = RSA.import_key(self.clientPublicKey)

        cipher = PKCS1_OAEP.new(otherPublicKey)

        for message in self.messages:
            self.encryptedMessages.append(cipher.encrypt(message.toBytes()))

    def __str__(self):
        return f"command: {self.command}\n" \
               f"file: {self.file.decode('ascii')}\n" \
               f"path: {self.path}\n" \
               f"randomstring: {self.randomString}\n" \
               f"replyStatus: {self.replyStatus}\n\n"
