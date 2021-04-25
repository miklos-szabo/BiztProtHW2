from Crypto.Cipher.PKCS1_OAEP import PKCS1OAEP_Cipher
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_PSS

from netsim.netinterface import network_interface
from communication.fullMessage import FullMessage
from communication.message import Message
from typing import List
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class ClientCommunication:
    netIf: network_interface = None
    ownAddress: str
    keyPass: str  # Password for accessing the private key
    deCipher: PKCS1OAEP_Cipher

    def __init__(self, address: str, keypass: str):  # Address is 1 character, A-Y (Z is the server)
        self.ownAddress = address
        self.checkAndCreateInterface()
        self.keyPass = keypass

        kfile = open('../client/client-keypair.pem', 'r')
        keypairstr = kfile.read()
        kfile.close()
        cleintPrivateKey = RSA.import_key(keypairstr, passphrase=self.keyPass)
        self.deCipher = PKCS1_OAEP.new(cleintPrivateKey)

    def checkAndCreateInterface(self):
        if self.netIf is None:
            self.netIf = network_interface("../netsim/files/", self.ownAddress)

    def sendMessageToServer(self, fullMessage: FullMessage):
        self.checkAndCreateInterface()
        fullMessage.createMessages()
        if fullMessage.command != "HDS":
            fullMessage.addSignatureMessages(self.keyPass)
        fullMessage.encryptMessages()

        for msg in fullMessage.encryptedMessages:
            self.netIf.send_msg("Z", msg)

    def receiveMessageFromServer(self) -> FullMessage:
        self.checkAndCreateInterface()
        status, msg = self.netIf.receive_msg(True)
        firstMessage = self.decryptMessageFromServer(msg)

        # Receive the other messages
        receivedMessages: List[Message] = [firstMessage]
        for i in range(1, firstMessage.messagesCount):
            status, msg = self.netIf.receive_msg(True)  # TODO timeout?
            receivedMessages.append(self.decryptMessageFromServer(msg))

        # Check message order
        messageNumbers = [m.messageNr for m in receivedMessages]
        messagesAndNumbers = zip(messageNumbers, range(1, firstMessage.messagesCount + 1))
        for msgNr, num in messagesAndNumbers:   #Checking message order
            if msgNr != num:
                raise Exception("Wrong message order!")

        if firstMessage.command != "HDS":
            self.checkSignature(receivedMessages)

        return FullMessage.fromMessages(receivedMessages, False)

    def decryptMessageFromServer(self, message: bytes) -> Message:
        return Message.fromBytes(self.deCipher.decrypt(message))

    def checkSignature(self, messages: List[Message]):
        if len(messages) < 3:
            raise Exception("Signature check on less than 3 messages")

        signature: bytes = messages[-2].data + messages[-1].data
        allMessagesAsBytes: bytes = b''
        for message in messages[:-2]:
            allMessagesAsBytes += message.toBytes()

        kFile = open('../client/server-publKey.pem', 'r')
        keyStr = kFile.read()
        kFile.close()

        serverPublKey = RSA.import_key(keyStr)

        h = SHA256.new(allMessagesAsBytes)
        verifier = PKCS1_PSS.new(serverPublKey)

        if not verifier.verify(h, signature):
            raise Exception("Signature validation failed!")