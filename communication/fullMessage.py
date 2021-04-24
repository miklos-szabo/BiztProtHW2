import uuid
from communication.message import Message
from typing import List
import math


class FullMessage:
    sessionId: uuid
    username: str
    command: str
    clientAddress: str
    clientToServer: bool
    messagesCount: int
    messages: List[Message]
    file: bytes     # All bytes of the file, also used for listing files
    path: str
    password: bytes      #LGN
    clientKey: bytes     #HDS
    randomString: str    #HDS
    replyStatus: str

    def __init__(self, sessionId: uuid,  command: str, clientAddress: str, username: str = "12345678901234567890123456789012",
                 clientToServer:bool = True, file: bytes = b'', path: str = "/",
                 password: bytes = b'', clientKey: bytes = b'', randomString: str = "", replyStatus: str = ""):
        self.sessionId = sessionId
        self.username = username
        self.command = command
        self.clientAddress = clientAddress
        self.clientToServer = clientToServer
        self.file = file
        self.path = path
        self.password = password
        self.clientKey = clientKey
        self.randomString = randomString
        self.replyStatus = replyStatus
        self.messages = []
        self.messagesCount = 0

    def createMessages(self):
        self.__constructMessagesAsClient() if self.clientToServer else self.__contructMessagesAsServer()
        self.__updateMessagesCount()  # So that all the headers have the right count

    def __constructMessagesAsClient(self):    # Add the base message here, without the signature
        if self.command == "HDS":
            self.__addAsMessage(self.clientKey)
            self.__addAsMessage(self.randomString.encode('ascii'))

        elif self.command == "LGN":
            self.__addAsMessage(self.password)

        elif self.command == "MKD" or self.command == "RMD" or self.command == "CWD":
            self.__addAsMessage(self.path.encode('ascii'))

        elif self.command == "GWD":
            self.__addAsMessage(b'')

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
            for msg in messages:
                allPaths += msg.data
            self.path = allPaths.decode('ascii')

        elif self.command == "UPL":
            self.replyStatus = messages[0].data.decode('ascii')

        elif self.command == "DNL":
            self.path = messages[0].data.decode('ascii')
            wholeFile: bytes = b''
            for msg in messages[1:]:
                wholeFile += msg.data
            self.file = wholeFile

        elif self.command == "RMF":
            self.replyStatus = messages[0].data.decode('ascii')

        else:
            raise Exception("Unknown command type!")

    def __parseAsServer(self, messages: List[Message]):
        if self.command == "HDS":
            self.clientKey = messages[0].data + messages[1].data
            self.randomString = (messages[2].data + messages[3].data).decode('ascii')

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
            for msg in messages[1:]:
                wholeFile += msg.data
            self.file = wholeFile

        elif self.command == "DNL":
            self.path = messages[0].data.decode('ascii')

        elif self.command == "RMF":
            self.path = messages[0].data.decode('ascii')

        else:
            raise Exception("Unknown command type!")


    def addSignatureMessages(self, signature: bytes):
        if self.command != "HDS":
            self.__addAsMessage(signature)
            self.__updateMessagesCount()
