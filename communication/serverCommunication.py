from netsim.netinterface import network_interface
from communication.message import Message
from communication.fullMessage import FullMessage
from typing import List


class ServerCommunication:
    netIf: network_interface = None

    def __init__(self):
        self.checkAndCreateInterface()

    def checkAndCreateInterface(self):
        if self.netIf is None:
            self.netIf = network_interface("../netsim/files/", "Z")  # Z is the server's address

    def sendMessageToClient(self, fullMessage: FullMessage):
        self.checkAndCreateInterface()

        for msg in fullMessage.messages:
            self.netIf.send_msg(fullMessage.clientAddress, msg.toBytes())

    def receiveMessageFromClient(self) -> FullMessage:
        self.checkAndCreateInterface()
        status, msg = self.netIf.receive_msg(True)
        firstMessage = Message.fromBytes(msg)

        # TODO decrypt

        # Receive the other messages
        receivedMessages: List[Message] = [firstMessage]
        for i in range(1, firstMessage.messagesCount):
            status, msg = self.netIf.receive_msg(True)
            receivedMessages.append(Message.fromBytes(msg)) # TODO timeout?

        # Check message order
        messageNumbers = [m.messageNr for m in receivedMessages]
        messagesAndNumbers = zip(messageNumbers, range(1, firstMessage.messagesCount + 1))
        for msgNr, num in messagesAndNumbers:  # Checking message order
            if msgNr != num:
                raise Exception("Wrong message order!")

        fullMessage = FullMessage(firstMessage.sessionId, firstMessage.command, firstMessage.origin,
                                  firstMessage.username, clientToServer=True)

        for message in receivedMessages:
            fullMessage.file += message.data

        return fullMessage

