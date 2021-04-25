from communication.clientCommunication import ClientCommunication
from communication.fullMessage import FullMessage
from Crypto.Hash import SHA256
from getpass import getpass
from pathlib import Path
import uuid
import random
import string
import sys

keyPasword = getpass("Enter your key password: ")

clientAddress = "A"
sessionId = uuid.uuid4()
communication = ClientCommunication(clientAddress, keyPasword)
loggedIn = False

#handshacke
letters = string.printable
randomString = ''.join(random.choice(letters) for i in range(512))
hdsMsg = FullMessage(sessionId, "HDS", clientAddress, randomString=randomString )
communication.sendBytesToServer(hdsMsg)
response = communication.receiveMessageFromServer()

if response.randomString != randomString
    print("The handshake with server was unsuccessful!")
    sys.exit()

#login
userName = input("User name: ")
password = getpass()

loginMsg = FullMessage(sessionId, "LGN", "A", userName, password=password)
communication.sendBytesToServer(loginMsg)
response = communication.receiveMessageFromServer()

if response.replyStatus == "OK"
    loggedIn = True
    print("Login succes!")
else
    print("Login failed")

#general operation
while loggedIn
    command = input("Enter a command: ").capitalize()

    if command == "MKD"
        dirName = input("Enter the name of the directory: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK"
            print("Directory created!")
        else
            print("Unable to create directory!")

    elif command == "RMD"
        dirName = input("Enter the name of the directory")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK"
            print("Directory removed!")
        else
            print("Unable to remove directory!")

    elif command == "CWD"
        dirName = input("Enter the path of the directory: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK"
            print("Directory changed!")
        else
            print("Unable to change directory!")

    elif command == "GWD"
        msg = FullMessage(sessionId, command, clientAddress, userName)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        print("Working directory: " + response.path)

    elif command == "LST"
        dirName = input("Enter the path of the directory: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        content = response.path.split(";")
            print("Directory content:")
            for c in content
                print(c)

    elif command == "UPL"
        filePath = input("Enter the path of the file: ")
        file = open(filePath, "r").read().encode()

        msg = FullMessage(sessionId, command, clientAddress, userName, file=file)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK"
            print("File uploaded!")
        else
            print("Unable to upload the file!")

    elif command == "DNL"
        filePath = input("Enter the path of the file to dowload: ")
        fileName = Path(filePath).name

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        file = open(fileName, 'wb')
        file.write(response.file)
        file.close

    elif command == "RMF"
        fileName = input("Enter the name of the file to remove: ")

        msg = FullMessage(sessionId, command, clientAddress, userName, path=dirName)
        communication.sendBytesToServer(msg)
        response = communication.receiveMessageFromServer()

        if response.replyStatus == "OK"
            print("File removed!")
        else
            print("Unable to remove the file!")
    
    print("Unknown command!")
