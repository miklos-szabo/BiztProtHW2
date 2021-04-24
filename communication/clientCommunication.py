from netsim.netinterface import network_interface
from communication.fullMessage import FullMessage
from communication.message import Message
from typing import List


class ClientCommunication:
    netIf: network_interface = None
    ownAddress: str

    def __init__(self, address: str):  # Address is 1 character, A-Y (Z is the server)
        self.ownAddress = address
        self.checkAndCreateInterface()

    def checkAndCreateInterface(self):
        if self.netIf is None:
            self.netIf = network_interface("../netsim/files/", self.ownAddress)

    def sendMessageToServer(self, fullMessage: FullMessage):
        self.checkAndCreateInterface()

        for msg in fullMessage.messages:
            self.netIf.send_msg("Z", msg.toBytes())

    def receiveMessageFromServer(self) -> FullMessage:
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
        for msgNr, num in messagesAndNumbers:   #Checking message order
            if msgNr != num:
                raise Exception("Wrong message order!")

        fullMessage = FullMessage(firstMessage.sessionId, firstMessage.command, firstMessage.origin, firstMessage.username, clientToServer=False)

        for message in receivedMessages:
            fullMessage.file += message.data

        return fullMessage
