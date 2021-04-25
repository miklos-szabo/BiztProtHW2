from communication.clientCommunication import ClientCommunication
from communication.fullMessage import FullMessage
import uuid

from Crypto.PublicKey import RSA

#%%

communication = ClientCommunication("A", "keyPassword")

kfile = open('client-publKey.pem', 'r')
clientKey = kfile.read()
kfile.close()

message = FullMessage(uuid.uuid4(), "UPL", "A", "12345678901234567890123456789012", clientToServer=True, file="Hello there!aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab".encode('ascii'),
                      path="/user1/asdf", password="passwordpassword".encode('ascii'), clientKey=clientKey,
                      randomString="stringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstringstring",
                      replyStatus="OK")
communication.sendMessageToServer(message)
print("Message sent, waiting for response...")
response = communication.receiveMessageFromServer()
print("Received response!")

#%%

# clientKey = RSA.generate(4096)
# o1file = open('client-keypair.pem', 'w')
# o2file = open('client-publKey.pem', 'w')
#
# keypairStr = clientKey.export_key(format='PEM', passphrase='keyPassword').decode('ASCII')
# publKeyStr = clientKey.public_key().export_key(format='PEM').decode('ASCII')
#
# o1file.write(keypairStr)
# o2file.write(publKeyStr)
#
# o1file.close()
# o2file.close()