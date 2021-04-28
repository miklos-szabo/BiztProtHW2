from communication.clientCommunication import ClientCommunication
from communication.fullMessage import FullMessage
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
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
keyPassword =''.join(random.choice(letters) for _ in range(32))

clientKey = RSA.generate(4096)
o1file = open('client/client-keypair.pem', 'w')
o2file = open('client/client-publKey.pem', 'w')
keypairStr = clientKey.export_key(format='PEM', passphrase=keyPassword).decode('ASCII')
publKeyStr = clientKey.public_key().export_key(format='PEM').decode('ASCII')
o1file.write(keypairStr)
o2file.write(publKeyStr)
o1file.close()
o2file.close()



sessionId = uuid.uuid4()
communication = ClientCommunication(clientAddress, keyPassword)
loggedIn = False

kfile = open('client/client-publKey.pem', 'r')
clientPublicKeyStr = kfile.read()
kfile.close()

# handshake
randomString = ''.join(random.choice(letters) for _ in range(512))
hdsMsg = FullMessage(sessionId, "HDS", clientAddress, randomString=randomString, clientKey=clientPublicKeyStr,
                     username=b"12345678901234567890123456789012")
communication.sendMessageToServer(hdsMsg)
response = communication.receiveMessageFromServer()

if response.randomString != randomString:
    print("The handshake with server was unsuccessful!")
    sys.exit()

while True:
    # login
    userName = SHA256.new(input("User name: ").encode('ascii')).digest()
    password = SHA256.new(input("Password: ").encode('ascii')).digest()

    loginMsg = FullMessage(sessionId, "LGN", "A", userName, password=password)
    communication.sendMessageToServer(loginMsg)
    response = communication.receiveMessageFromServer()

    if response.replyStatus == "OK":
        loggedIn = True
        print("Login success!")
        break
    else:
        print("Login failed")



#general operation
while loggedIn:
    inputcommand = input("Enter a command: ").split(' ')
    command = inputcommand[0].upper()
    if command == "MKD":
        if len(inputcommand) < 2:
            print("Wrong command")
            continue
        dirName = inputcommand[1]

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("Directory created!")
        else:
            print("Unable to create directory!")

    elif command == "RMD":
        if len(inputcommand) < 2:
            print("Wrong command")
            continue
        dirName = inputcommand[1]

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("Directory removed!")
        else:
            print("Unable to remove directory!")

    elif command == "CWD":
        if len(inputcommand) < 2:
            print("Wrong command")
            continue
        dirName = inputcommand[1]

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
        if len(inputcommand) < 2:
            dirName = "."
        else:
            dirName = inputcommand[1]

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        content = response.path.split(";")
        print("Directory content:")
        for c in content:
            print(c)

    elif command == "UPL":
        if len(inputcommand) < 2:
            print("Wrong command")
            continue
        filePath = inputcommand[1]
        file = open(f"client/{filePath}", "r").read().encode()

        msg = FullMessage(sessionId, command, clientAddress, userName, file=file, path=filePath)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("File uploaded!")
        else:
            print("Unable to upload the file!")

    elif command == "DNL":
        if len(inputcommand) < 2:
            print("Wrong command")
            continue
        filePath = inputcommand[1]

        msg = FullMessage(sessionId, command, clientAddress, userName, path=filePath)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if len(response.file) > 0:
            fileName = filePath.split('/')[-1]
            file = open(f"client/{fileName}", 'wb')
            file.write(response.file)
            file.close()
            print("File downloaded!")

        else:
            print("Unable to download the file!")

    elif command == "RMF":
        if len(inputcommand) < 2:
            print("Wrong command")
            continue
        fileName = inputcommand[1]

        msg = FullMessage(sessionId, command, clientAddress, userName, path=fileName)
        communication.sendMessageToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK":
            print("File removed!")
        else:
            print("Unable to remove the file!")
    
    else:
        print("Unknown command!")
