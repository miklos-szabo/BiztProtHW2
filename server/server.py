from communication.serverCommunication import ServerCommunication
from communication.fullMessage import FullMessage
import uuid

communication = ServerCommunication()

#%%
while True:
    print("Waiting for message...")
    msg = communication.receiveMessageFromClient()
    print("Received message!")
    if msg.file.decode('ascii') == "Hello there!":
        response = FullMessage(msg.sessionId, msg.command, msg.clientAddress, msg.username, clientToServer=False, file="General Kenobi!".encode('ascii'))
        communication.sendMessageToClient(response)
    else:
        response = FullMessage(msg.sessionId, msg.command, msg.clientAddress, msg.username, clientToServer=False, file="You're a bold one!ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccd".encode('ascii'))
        communication.sendMessageToClient(response)
    print("Response sent")

