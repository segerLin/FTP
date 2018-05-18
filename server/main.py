# coding=utf-8

from handlers import FTPCommandHandler, ls_callback, open_callback, cd_callback, rm_callback, get_callback, put_callback, FileHandler
from threaded_server import FTPServer
from ftp_client_handler import FTPClientHandler

if __name__ == '__main__':
    server = FTPServer("0.0.0.0", 50000, 5)
    server.listen()
    callback_table = {
        "ls": ls_callback,
        "open": open_callback,
        "cd": cd_callback,
        "rm": rm_callback,
        "get": get_callback,
        "put": put_callback
    }
    server.accept_connections(FTPClientHandler, FTPCommandHandler(callback_table), FileHandler(), True)
