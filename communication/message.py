import uuid


class Message:
    sessionId: uuid     # 16 bytes
    username: str       # 32 bytes
    command: str        # 3 bytes
    origin: str         # 1 byte
    messagesCount: int  # 8 bytes
    messageNr: int      # 8 bytes
    data: bytes         # 0-256 bytes

    def __init__(self, sessionId: uuid, username: str, command: str, origin: str, messagesCount: int, messageNr: int, data: bytes):
        self.sessionId = sessionId
        self.username = username
        self.command = command
        self.origin = origin
        self.messagesCount = messagesCount
        self.messageNr = messageNr
        self.data = data

    @classmethod
    def fromBytes(cls, fullData:bytes):
        sessionId = uuid.UUID(bytes=fullData[0:16])
        username = fullData[16:48].decode('ascii')
        command = fullData[48:51].decode('ascii')
        origin = chr(fullData[51])
        messagesCount = int.from_bytes(fullData[52:60], byteorder='big')
        messageNr = int.from_bytes(fullData[60:68], byteorder='big')
        data = fullData[68:]
        return cls(sessionId, username, command, origin, messagesCount, messageNr, data)

    def toBytes(self) -> bytes:
        return self.sessionId.bytes + \
               self.username.encode('ascii') + \
               self.command.encode('ascii') + \
               self.origin.encode('ascii') + \
               self.messagesCount.to_bytes(length=8, byteorder='big') + \
               self.messageNr.to_bytes(length=8, byteorder='big') + \
               self.data

