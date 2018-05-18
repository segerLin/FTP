# coding=utf-8

import socket
import threading

class FTPServer:

    """
    多线程的FTP服务端
    """

    def __init__(self, host, port, backlog):
        """
        初始化Server
        :param host: 地址名
        :param port: 端口
        :param backlog: 最大等待数量
        :return:
        """

        self.host = host
        self.port = port
        self.backlog = backlog
        # 存储已经连接的客户端
        self.clients = []
        # socket
        # 设置成 TCP , 面向连接
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEPORT
        # https://my.oschina.net/miffa/blog/390931
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # 绑定socket
        self.sock.bind((self.host, self.port))

        # 用于停止服务
        self.__stop = False

    def listen(self):
        # 开启监听
        print("Server: start listening")
        self.sock.listen(self.backlog)

    def accept_connections(self, client_handler, command_handler, file_handler, new_threading=False, daemon=True):
        """
        开始监听
        :param client_handler: 处理和客户端的通信的类, 需要有recv方法, 初始化方法接受 command_handler 和 file_handler 为参数
        :param command_handler: 处理命令的handler
        :param file_handler: 处理文件的handler, 用于保存接受到的文件
        :param new_threading: 是否在新进程中运行
        :param daemon: 是否是后台线程
        :return:
        """
        print("Server: start accepting connections")
        if not callable(client_handler):
            raise TypeError("client_handler must be callable")
        while not self.__stop:
            client_handler_obj = client_handler(command_handler, file_handler)
            # 接收请求
            client, address = self.sock.accept()
            print("new client:", address)
            # 添加client到list中
            self.clients.append(client)
            # 设置超时时间
            # client.settimeout(60 * 10)
            # 是否开启新的线程
            if not new_threading:
                client_handler(client, address)
            else:
                # 在另外一个线程中进行服务
                thread = threading.Thread(target=client_handler_obj.recv, args=(client, address))
                thread.setDaemon(daemon)
                thread.start()

    def stop(self):
        self.__stop = True
        for client in self.clients:
            client.close()

