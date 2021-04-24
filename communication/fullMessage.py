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
    messagesCount: int = 0
    messages: List[Message] = []
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
        self.constructMessagesAsClient() if self.clientToServer else self.contructMessagesAsServer()

    def constructMessagesAsClient(self):
        for i in range(0, math.ceil(len(self.file) / 256)):
            self.messages.append(Message(self.sessionId, self.username, self.command, self.clientAddress, math.ceil(len(self.file) / 256), i + 1,
                                         self.file[i * 256 : (i+1) * 256 if (i+1) * 256 < len(self.file) else len(self.file)]))
            self.messagesCount += 1

    def contructMessagesAsServer(self):
        for i in range(0, math.ceil(len(self.file) / 256)):
            self.messages.append(Message(self.sessionId, self.username, self.command, self.clientAddress, math.ceil(len(self.file) / 256), i + 1,
                                         self.file[i * 256 : (i+1) * 256 if (i+1) * 256 < len(self.file) else len(self.file)]))
            self.messagesCount += 1
