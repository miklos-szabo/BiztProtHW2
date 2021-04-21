from netsim.netinterface import network_interface
from Communication.message import Message


class ServerCommunication:
    netIf: network_interface = None

    def __init__(self):
        self.checkAndCreateInterface()

    def checkAndCreateInterface(self):
        if self.netIf is None:
            self.netIf = network_interface("../netsim/files/", "Z")  # Z is the server's address

    def sendMessageToClient(self, message: Message):
        self.checkAndCreateInterface()
        self.netIf.send_msg("A", message.toBytes())

    def receiveMessageFromClient(self) -> Message:
        self.checkAndCreateInterface()
        status, msg = self.netIf.receive_msg(True)
        return Message.fromBytes(msg)

