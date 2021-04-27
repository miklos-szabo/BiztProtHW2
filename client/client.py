from communication.clientCommunication import ClientCommunication
from communication.fullMessage import FullMessage
from Crypto.PublicKey import RSA
from getpass import getpass
from pathlib import Path
import uuid
import random
import string
import sys
import getopt

try:
    opts, args = getopt.getopt(sys.argv[1:], 'a:', ['address='])
except getopt.GetoptError:
    print('Usage:')
    print("-a: client's address, 1 character from A-Y")
    sys.exit(1)

if len(opts) < 1:
    print("-a: client's address, 1 character from A-Y")
    sys.exit(1)

for opt, arg in opts:
    if opt == '-a' or opt == '--address':
        if arg in list(string.ascii_uppercase):
            clientAddress = arg
        else:
            print("-a: client's address, 1 character from A-Y")
            sys.exit(1)
    else:
        print("-a: client's address, 1 character from A-Y")
        sys.exit(1)

print("Client's address: " + clientAddress)

# Get a random password with which to store the key, we won't need to use it again
letters = string.printable
keyPassword = ''.join(random.choice(letters) for _ in range(32))

clientKey = RSA.generate(4096)
o1file = open('../client/client-keypair.pem', 'w')
o2file = open('../client/client-publKey.pem', 'w')
keypairStr = clientKey.export_key(format='PEM', passphrase=keyPassword).decode('ASCII')
publKeyStr = clientKey.public_key().export_key(format='PEM').decode('ASCII')
o1file.write(keypairStr)
o2file.write(publKeyStr)
o1file.close()
o2file.close()



sessionId = uuid.uuid4()
communication = ClientCommunication(clientAddress, keyPassword)
loggedIn = False

kfile = open('../client/client-publKey.pem', 'r')
clientPublicKeyStr = kfile.read()
kfile.close()

#handshake
randomString = ''.join(random.choice(letters) for _ in range(512))
hdsMsg = FullMessage(sessionId, "HDS", clientAddress, randomString=randomString, clientKey=clientPublicKeyStr)
communication.sendMessageToServer(hdsMsg)
response = communication.receiveMessageFromServer()

if response.randomString != randomString:
    print("The handshake with server was unsuccessful!")
    sys.exit()

#login
userName = input("User name: ")
password = getpass()

loginMsg = FullMessage(sessionId, "LGN", "A", userName, password=password)
communication.sendMessageToServer(loginMsg)
response = communication.receiveMessageFromServer()

if response.replyStatus == "OK":
    loggedIn = True
    print("Login success!")
else:
    print("Login failed")

#general operation
while loggedIn:
    command = input("Enter a command: ").capitalize()

    if command == "MKD":
        dirName = input("Enter the name of the directory: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("Directory created!")
        else:
            print("Unable to create directory!")

    elif command == "RMD":
        dirName = input("Enter the name of the directory")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("Directory removed!")
        else:
            print("Unable to remove directory!")

    elif command == "CWD":
        dirName = input("Enter the path of the directory: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("Directory changed!")
        else:
            print("Unable to change directory!")

    elif command == "GWD":
        msg = FullMessage(sessionId, command, clientAddress, userName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        print("Working directory: " + response.path)

    elif command == "LST":
        dirName = input("Enter the path of the directory: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        content = response.path.split(";")
        print("Directory content:")
        for c in content:
            print(c)

    elif command == "UPL":
        filePath = input("Enter the path of the file: ")
        file = open(filePath, "r").read().encode()

        msg = FullMessage(sessionId, command, clientAddress, userName, file=file)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("File uploaded!")
        else:
            print("Unable to upload the file!")

    elif command == "DNL":
        filePath = input("Enter the path of the file to dowload: ")
        fileName = Path(filePath).name

        msg = FullMessage(sessionId, command, clientAddress, userName, path=fileName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        file = open(fileName, 'wb')
        file.write(response.file)
        file.close()

    elif command == "RMF":
        fileName = input("Enter the name of the file to remove: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=fileName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("File removed!")
        else:
            print("Unable to remove the file!")
    
    print("Unknown command!")
