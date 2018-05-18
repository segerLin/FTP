import threading

class TextHandler():

    # 字节流开始的几个字节存放的是消息体的长度
    SIZEOF_META_DATA = 4

    def __init__(self, callback=None):
        super(TextHandler, self).__init__()

        # 用于标记是否已经开始接受消息了
        self.receiving = False

        self.callback = callback

        self.msgSize = -1
        self.sizeReceived = 0   # 已经接收到的数据
        self.receivedBytes = b''


    def reset(self):
        self.msgSize = -1
        self.sizeReceived = 0
        self.receivedBytes = b''

    def __sendText(self, message):
        pass


    def recvText(self, client, address):
        """
        从client中读取文字消息, 将在新的线程中处理
        :param client:
        :param address:
        :param callback: 回调函数
        :return:
        """
        if not self.receiving:
            threading.Thread(target=self.__recv, args=(client, address)).start()

    def __recv(self, client, address):
        # buffer size
        size = 1024
        print("->client @{} connected".format(address))
        while True:
            try:
                if self.sizeReceived < TextHandler.SIZEOF_META_DATA:
                    # 继续接收一开始的SIZEOF_META_DATA字节
                    # 注意不要多接收字节,不然有几条消息的话可能会混乱
                    data = client.recv(TextHandler.SIZEOF_META_DATA - self.sizeReceived)
                    print(data)
                    if data:
                        self.receivedBytes += data
                        self.sizeReceived += len(data)
                    else:
                        # 断开了链接
                        print("->client @{} disconnected".format(address))
                        client.close()
                        return
                else:
                    if self.msgSize == -1:
                        # 读取信息大小
                        self.msgSize = int.from_bytes(self.receivedBytes[: TextHandler.SIZEOF_META_DATA], byteorder="little")
                        print('->message body size: ', self.msgSize)

                    if self.sizeReceived < TextHandler.SIZEOF_META_DATA + self.msgSize:
                        # 继续读取信息, 但是注意不能少读也不能多读
                        data = client.recv(min(TextHandler.SIZEOF_META_DATA + self.msgSize - self.sizeReceived, size))
                        print(data)
                        if data:
                            self.receivedBytes += data
                            self.sizeReceived += len(data)
                        else:
                            print("->client @{} disconnected".format(address))
                            client.close()
                            return
                    else:
                        # 读取完毕
                        print("fuck")
                        print("->received {} bytes".format(len(self.receivedBytes)))
                        data = self.receivedBytes[TextHandler.SIZEOF_META_DATA: ].decode("UTF-8")
                        print("->msg", data)
                        #self.emit(SIGNAL("newText"), data)
                        if callable(self.callback):
                            self.callback(data)
                        # 清空状态
                        self.reset()
            except Exception as e:
                print("->error occurred @{}: {}".format(address, str(e)))
                client.close()
                self.receiving = False
                return
