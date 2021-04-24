from communication.clientCommunication import ClientCommunication
from communication.fullMessage import FullMessage
import uuid

communication = ClientCommunication("A")

#%%

message = FullMessage(uuid.uuid4(), "TST", "A", "12345678901234567890123456789012", clientToServer=True, file="Hello there!aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab".encode('ascii'))
communication.sendMessageToServer(message)
print("Message sent, waiting for response...")
response = communication.receiveMessageFromServer()
print("Received response!")