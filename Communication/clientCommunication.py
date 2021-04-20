from netsim.netinterface import network_interface


class ClientCommunication:
    netIf: network_interface = None
    ownAddress: str

    def __init__(self, address: str):  # Address is 1 character, A-Y (Z is the server)
        self.ownAddress = address
        self.checkAndCreateInterface()

    def checkAndCreateInterface(self):
        if self.netIf is None:
            self.netIf = network_interface("../netsim/files/", self.ownAddress)

    def sendBytesToServer(self, message: bytes):
        self.checkAndCreateInterface()
        self.netIf.send_msg("Z", message)

    def receiveMessageFromServer(self) -> str:
        self.checkAndCreateInterface()
        status, msg = self.netIf.receive_msg(True)
        return msg.decode('ascii')
