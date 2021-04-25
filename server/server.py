from communication.serverCommunication import ServerCommunication
from communication.fullMessage import FullMessage
import uuid
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

#%%
communication = ServerCommunication("keyPassword")

kfile = open('client-publKey.pem', 'r')
clientKey = kfile.read()
kfile.close()

while True:
    print("Waiting for message...")
    msg = communication.receiveMessageFromClient()
    print("Received message!")

    response = FullMessage(uuid.uuid4(), msg.command, msg.clientAddress, msg.username, clientToServer=False,
                          file="Hello there!aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab".encode('ascii'),
                          path="/user1/asdf", password="passwordpassword".encode('ascii'),
                          clientKey=clientKey,
                          randomString="stringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstring",
                          replyStatus="OK")
    communication.sendMessageToClient(response)
    print("Response sent")

#%%

# serverKey = RSA.generate(4096)
# o1file = open('server-keypair.pem', 'w')
# o2file = open('server-publKey.pem', 'w')
#
# keypairStr = serverKey.export_key(format='PEM', passphrase='keyPassword').decode('ASCII')
# publKeyStr = serverKey.public_key().export_key(format='PEM').decode('ASCII')
#
# o1file.write(keypairStr)
# o2file.write(publKeyStr)
#
# o1file.close()
# o2file.close()