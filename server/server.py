from Communication.serverCommunication import ServerCommunication
from Communication.message import Message
import uuid

communication = ServerCommunication()

#%%
while True:
    print("Waiting for message...")
    msg = communication.receiveMessageFromClient()
    print("Received message!")
    if msg.data.decode('ascii') == "Hello there!":
        response = Message(uuid.uuid4(), "12345678901234567890123456789012", "TST", "A", 1, 1, "General Kenobi!".encode('ascii'))
        communication.sendMessageToClient(response)
    else:
        response = Message(uuid.uuid4(), "12345678901234567890123456789012", "TST", "A", 1, 1, "You're a bold one!".encode('ascii'))
        communication.sendMessageToClient(response)
    print("Response sent")

