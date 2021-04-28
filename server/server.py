import os
import logging
import uuid
from pathlib import Path
from enum import Enum
from typing import Optional
from server.database import CommandDatabase, UserDatabase, CommandDatabase, WindowsCommands, LinuxCommands
from communication.serverCommunication import ServerCommunication
from communication.fullMessage import FullMessage
from eventlet import Timeout


class ResponseType(Enum):
    OK = "OK"
    FAIL = "FAIL"


class Client:
    def __init__(self, key, sessionId, username=b'', address=""):
        self.address = address
        self.username = username
        self.key = key
        self.sessionId = sessionId


class Server:
    def __init__(self, logger, command_database, base_address: str):
        self.__logger = logger
        self.__logger.info("Init FTPServer")
        self.__client: Optional[Client] = None
        self.__communication: Optional[ServerCommunication] = None
        self.__command_database: CommandDatabase = command_database
        self.__act_path = base_address
        self.__userdatabase = UserDatabase()
        self.__create_server_home()
        self.__set_communication()
        self.__logger.debug(f"Base address: {base_address}")

    def start(self) -> None:
        self.__logger.info("Start FTPServer")
        while True:
            self.__waiting_for_handshake()
            if self.__waiting_for_login():
                self.__waiting_for_messages()
                self.__end_connection()

    def __create_server_home(self) -> None:
        self.__create_folder_from_foldername(folder_name="server_home")
        self.__act_path = f"{self.__act_path}/server_home"
        for username in self.__userdatabase.get_usernames():
            self.__create_folder_from_foldername(folder_name=username)
            self.__create_folder_from_foldername(
                folder_name=f"{username}/home")

    def __create_folder_from_foldername(self, folder_name: str) -> None:
        if not self.__check_folder_is_exist(folder_name):
            cmd: str = self.__command_database.create_folder
            path: str = self.__command_database.create_path(
                self.__act_path, folder_name)
            os.system(f"{cmd} {path}")
            self.__logger.debug(f"{cmd} {path}")

    def __set_communication(self) -> None:
        keypass = input("Enter your key pass!\n")
        self.__communication = ServerCommunication(keypass)

    def __waiting_for_handshake(self) -> None:
        self.__logger.info("Waiting for handshake...")
        while True:
            msg: FullMessage = self.__communication.receiveMessageFromClient()
            self.__logger.debug("Received handshake message:")
            self.__logger.debug(msg)
            if msg.command == "HDS":
                randomString = msg.randomString
                clientPublicKey = msg.clientPublicKey
                self.__client = Client(key=clientPublicKey,
                                       sessionId=msg.sessionId)
                self.__send_response(ResponseType.OK, msg,
                                     randomString=randomString)
                self.__communication.setClientPublicKey(clientPublicKey)
                break
            else:
                self.__send_response(ResponseType.FAIL, msg)

    def __waiting_for_login(self) -> bool:
        self.__logger.info("Waiting for login...")
        counter: int = 0
        while counter < 5:
            msg: FullMessage = self.__communication.receiveMessageFromClient()
            self.__logger.debug(f"Received message: {msg}")
            if msg.command == "LGN" and self.__login(msg):
                self.__send_response(ResponseType.OK, msg)
                return True
            else:
                self.__send_response(ResponseType.FAIL, msg)
                counter += 1
        return False

    def __login(self, msg: FullMessage) -> bool:
        if self.__client.sessionId == msg.sessionId and self.__userdatabase.check_valid_user(msg.username):
            if self.__userdatabase.check_valid_password(msg.username, msg.password):
                self.__client.username = msg.username
                self.__client.address = 'A'
                self.__act_path += f"/{msg.username.hex()}/home"
                return True
        return False

    def __waiting_for_messages(self) -> None:
        msg: Optional[FullMessage] = None
        while True:
            with Timeout(50000, Exception("No messages recieved for a long time")):
                self.__logger.info("Waiting for message...")
                msg = self.__communication.receiveMessageFromClient()
                if msg is None:
                    return
                self.__logger.info("Get message!")
                self.__logger.debug({msg})
                if msg.command == "HDS" or msg.command == "LGN" or not self.__valid_session(msg):
                    self.__send_response(ResponseType.FAIL, msg)
                if msg.command == "MKD":
                    self.__create_folder(msg)
                if msg.command == "RMD":
                    self.__delete_folder(msg)
                if msg.command == "RMF":
                    self.__delete_file(msg)
                if msg.command == "CWD":
                    self.__change_act_folder(msg)
                if msg.command == "LST":
                    self.__list_folder(msg)
                if msg.command == "GWD":
                    self.__send_act_path(msg)
                if msg.command == "UPL":
                    self.__upload_file(msg)
                if msg.command == "DNL":
                    self.__download_file(msg)
                msg = None

    def __valid_session(self, msg: FullMessage) -> bool:
        return msg.sessionId == self.__client.sessionId

    def __create_folder(self, msg: FullMessage) -> None:
        folder_name = msg.path
        if not self.__check_folder_is_exist(folder_name):
            cmd: str = self.__command_database.create_folder
            path: str = self.__command_database.create_path(
                self.__act_path, folder_name)
            os.system(f"{cmd} {path}")
            self.__logger.debug(f"create folder: {folder_name}")
            self.__send_response(ResponseType.OK, msg)
        else:
            self.__send_response(ResponseType.FAIL, msg)

    def __delete_folder(self, msg: FullMessage) -> None:
        folder_name = msg.path
        if self.__check_folder_is_exist(folder_name):
            cmd: str = self.__command_database.delete_folder
            path: str = self.__command_database.create_path(
                self.__act_path, folder_name)
            os.system(f"{cmd} {path}")
            self.__logger.debug(f"delete folder: {folder_name}")
            self.__send_response(ResponseType.OK, msg)
        else:
            self.__send_response(ResponseType.FAIL, msg)

    def __delete_file(self, msg: FullMessage) -> None:
        file_name = msg.path
        if self.__check_folder_is_exist(file_name):
            cmd: str = self.__command_database.delete_file
            path: str = self.__command_database.create_path(
                self.__act_path, file_name)
            os.system(f"{cmd} {path}")
            self.__logger.debug(f"delete file: {file_name}")
            self.__send_response(ResponseType.OK, msg)
        else:
            self.__send_response(ResponseType.FAIL, msg)

    def __change_act_folder(self, msg: FullMessage) -> None:
        folder_name = msg.path
        if not self.__check_folder_path_is_correct(folder_name):
            self.__logger.debug("wrong path")
            self.__send_response(ResponseType.FAIL, msg)
        else:
            if folder_name == '..':
                suffix: str = f"/{self.__act_path.split('/')[-1]}"
                self.__act_path = self.__act_path.removesuffix(suffix)
            elif folder_name == '.':
                pass
            else:
                self.__act_path = self.__command_database.create_path(
                    self.__act_path, folder_name)
            self.__send_response(ResponseType.OK, msg)

    def __list_folder(self, msg: FullMessage) -> None:
        path = self.__command_database.create_path(self.__act_path, msg.path)
        file = ';'.join(file.name for file in os.scandir(path))
        self.__logger.debug(file)
        if file == "":
            file = "empty"
        self.__send_response(ResponseType.OK, msg, path=file)

    def __send_act_path(self, msg: FullMessage) -> None:
        act_path = '~' + self.__act_path.split(self.__client.username.hex())[1]
        self.__send_response(ResponseType.OK, msg, path=act_path)

    def __upload_file(self, msg: FullMessage) -> None:
        file_name = msg.path
        path = self.__command_database.create_path(self.__act_path, file_name)
        with open(path, 'wb') as f:
            f.write(msg.file)
        self.__logger.debug(f"upload file: {file_name}")
        self.__send_response(ResponseType.OK, msg)

    def __download_file(self, msg: FullMessage) -> None:
        file_name = msg.path
        path = self.__command_database.create_path(self.__act_path, file_name)
        with open(path, 'r') as f:
            file = f.read()
        self.__logger.debug(f"download file: {file_name}")
        self.__send_response(ResponseType.OK, msg, file=file, path=path)

    def __check_folder_path_is_correct(self, folder_name: str) -> bool:
        if (self.__check_folder_is_exist(folder_name) and
            folder_name.count('..') < 2 and
                not (folder_name == '..' and self.__act_path.split('/')[-1] == 'home')):
            return True
        return False

    def __check_folder_is_exist(self, folder_name: str) -> bool:
        path = Path(self.__command_database.create_path(
            self.__act_path, folder_name))
        self.__logger.debug(f"path: {path} exists: {path.exists()}")
        return path.exists()

    def __end_connection(self) -> None:
        self.__logger.info("end connection")
        self.__client = None
        self.__act_path = f"{os.getcwd()}/server_home"

    def __send_response(self, status: ResponseType, msg: FullMessage,
                        file: str = "", path: str = "", randomString: str = "") -> None:
        password = ""
        sessionId = msg.sessionId
        address = msg.clientAddress
        clientKey = msg.clientPublicKey
        username = msg.username
        if self.__client:
            sessionId = self.__client.sessionId
            clientKey = self.__client.key
        response: FullMessage = FullMessage(
            sessionId=sessionId,
            command=msg.command,
            clientAddress=address,
            username=username,
            clientToServer=False,
            file=file.encode('ascii'),
            path=path,
            password=password.encode('ascii'),
            clientKey=clientKey,
            randomString=randomString,
            replyStatus=status.value)
        self.__communication.sendMessageToClient(response)
        self.__logger.debug(f"Response sent: {response}")


if __name__ == "__main__":
    # serverKey = RSA.generate(4096)
    # o1file = open('server/server-keypair.pem', 'w')
    # o2file = open('server/server-publKey.pem', 'w')
    #
    # keypairStr = serverKey.export_key(format='PEM', passphrase='keyPassword').decode('ASCII')
    # publKeyStr = serverKey.public_key().export_key(format='PEM').decode('ASCII')
    #
    # o1file.write(keypairStr)
    # o2file.write(publKeyStr)
    #
    # o1file.close()
    # o2file.close()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    if os.name == 'posix':
        commands = LinuxCommands()
    else:
        commands = WindowsCommands()
    server: Server = Server(logger, commands, os.getcwd())
    server.start()
