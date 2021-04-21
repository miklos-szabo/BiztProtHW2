from Communication.clientCommunication import ClientCommunication
from Communication.message import Message
import uuid

communication = ClientCommunication("A")

#%%

message = Message(uuid.uuid4(), "12345678901234567890123456789012", "TST", "A", 1, 1, "Hello there!".encode('ascii'))
communication.sendBytesToServer(message)
print("Message sent, waiting for response...")
response = communication.receiveMessageFromServer()
print("Received response!")