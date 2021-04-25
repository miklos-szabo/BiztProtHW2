from Crypto.Cipher.PKCS1_OAEP import PKCS1OAEP_Cipher
from Crypto.Hash import SHA256

from netsim.netinterface import network_interface
from communication.message import Message
from communication.fullMessage import FullMessage
from typing import List
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_PSS


class ServerCommunication:
    netIf: network_interface = None
    keyPass: str  # Password for accessing the private key
    deCipher: PKCS1OAEP_Cipher

    def __init__(self, keypass: str):
        self.checkAndCreateInterface()
        self.keyPass = keypass

        kfile = open('../server/server-keypair.pem', 'r')
        keypairstr = kfile.read()
        kfile.close()
        serverPrivateKey = RSA.import_key(keypairstr, passphrase=self.keyPass)
        self.deCipher = PKCS1_OAEP.new(serverPrivateKey)

    def checkAndCreateInterface(self):
        if self.netIf is None:
            self.netIf = network_interface("../netsim/files/", "Z")  # Z is the server's address

    def sendMessageToClient(self, fullMessage: FullMessage):
        self.checkAndCreateInterface()
        fullMessage.createMessages()
        if fullMessage.command != "HDS":
            fullMessage.addSignatureMessages(self.keyPass)
        fullMessage.encryptMessages()

        for msg in fullMessage.encryptedMessages:
            self.netIf.send_msg(fullMessage.clientAddress, msg)

    def receiveMessageFromClient(self) -> FullMessage:
        self.checkAndCreateInterface()
        status, msg = self.netIf.receive_msg(True)
        firstMessage = self.decryptMessageFromClient(msg)

        # Receive the other messages
        receivedMessages: List[Message] = [firstMessage]
        for i in range(1, firstMessage.messagesCount):
            status, msg = self.netIf.receive_msg(True)  # TODO timeout?
            receivedMessages.append(self.decryptMessageFromClient(msg))

        # Check message order
        messageNumbers = [m.messageNr for m in receivedMessages]
        messagesAndNumbers = zip(messageNumbers, range(1, firstMessage.messagesCount + 1))
        for msgNr, num in messagesAndNumbers:  # Checking message order
            if msgNr != num:
                raise Exception("Wrong message order!")

        if firstMessage.command != "HDS":
            self.checkSignature(receivedMessages)

        return FullMessage.fromMessages(receivedMessages, True)

    def decryptMessageFromClient(self, message: bytes) -> Message:
        return Message.fromBytes(self.deCipher.decrypt(message))

    def checkSignature(self, messages: List[Message]):
        if len(messages) < 3:
            raise Exception("Signature check on less than 3 messages")

        signature: bytes = messages[-2].data + messages[-1].data
        allMessagesAsBytes: bytes = b''
        for message in messages[:-2]:
            allMessagesAsBytes += message.toBytes()

        kFile = open('../server/client-publKey.pem', 'r')
        keyStr = kFile.read()
        kFile.close()

        clientPublKey = RSA.import_key(keyStr)

        h = SHA256.new(allMessagesAsBytes)
        verifier = PKCS1_PSS.new(clientPublKey)

        if not verifier.verify(h, signature):
            raise Exception("Signature validation failed!")

