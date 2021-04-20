from Communication import serverCommunication

communication = serverCommunication.ServerCommunication()

#%%
while True:
    print("Waiting for message...")
    msg = communication.receiveMessageFromClient()
    print("Received: " + msg)
    if msg == "Hello There!":
        communication.sendMessageToClient("General Kenobi!".encode('ascii'))
    else:
        communication.sendMessageToClient("You're a bold one!".encode('ascii'))
    print("Response sent")

