from netsim.netinterface import network_interface


class ServerCommunication:
    netIf: network_interface = None

    def __init__(self):
        self.checkAndCreateInterface()

    def checkAndCreateInterface(self):
        if self.netIf is None:
            self.netIf = network_interface("../netsim/files/", "Z")  # Z is the server's address

    def sendMessageToClient(self, message: bytes):
        self.checkAndCreateInterface()
        self.netIf.send_msg("A", message)

    def receiveMessageFromClient(self) -> str:
        self.checkAndCreateInterface()
        status, msg = self.netIf.receive_msg(True)
        return msg.decode('ascii')

