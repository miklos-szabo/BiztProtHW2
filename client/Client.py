from Communication import clientCommunication

communication = clientCommunication.ClientCommunication("A")

#%%

communication.sendBytesToServer("Dooku".encode('ascii'))
print("Message sent, waiting for response...")
print(communication.receiveMessageFromServer())