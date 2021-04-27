from typing import List


class UserDatabase:
    def check_valid_user(self, user: bytes) -> bool:
        user_dict = self.__create_dict()
        return user.hex() in user_dict.keys()

    def check_valid_password(self, user, password) -> bool:
        user_dict = self.__create_dict()
        return user.hex() in user_dict.keys() and password.hex() == user_dict[user.hex()]

    def get_usernames(self):
        user_dict = self.__create_dict()
        return user_dict.keys()

    def __create_dict(self) -> dict:
        with open('server/users.txt') as f:
            user_dict = dict(x.rstrip().split(None, 1) for x in f)
        return user_dict


class CommandDatabase:
    create_folder: str = "mkdir"
    change_folder: str = "cd"
    delete_folder: str
    delete_file: str
    list_files: str
    current_folder: str


class WindowsCommands(CommandDatabase):
    delete_folder = "rmdir"
    delete_file = "del"
    list_files = "dir"
    current_folder = "chdir"


class LinuxCommands(CommandDatabase):
    delete_folder = "rm -rs"
    delete_file = "rm"
    list_files = "ls -ln"
    current_folder = "pwd"
