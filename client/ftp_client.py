import socket
from ctypes import c_int32, c_int8

NORMALCOMMAND = 1
PUTCOMMAND = 1
UPLOADFILE = 2
GETFILE = 3


class FTP_Client():
    BufSize = 1024
    SIZEOF_TYPE = 1
    SIZEOF_META_DATA = 4
    msgSize = -1
    TRUECOMMAND = 0
    FALSECOMMAND = 1

    def __init__(self, host="172.22.55.28", port=50000):
        self.host = host
        self.port = port
        self.address = (host, port)
        self.totalSize = 0
        self.sendSize = 0
        self.msgSize = -1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

        # pass

    def reset(self):
        self.msgSize = -1
        self.totalSize = 0
        self.sendSize = 0

    def Judge(self, Command):
        CmdList = ["ls", "rm", "open", "put", "get", "cd"]
        print(Command)
        cmd = Command.split()
        for i in CmdList:

            if cmd[0].lower() == i:
                return True

        return False
        # pass

    def connection(self):
        self.sock.connect(self.address)
        print("connect succeed")

    """
    def getCmdLength(self,Command):
        CommandBytes = Command.encode("utf-8")
        byteSend = bytes(c_int32(len(CommandBytes)))
        self.totalSize = len(byteSend)
        return self.totalSize
    """

    def uploadFile(self, Command):
        filename = Command.split()[1]
        fp = open(filename, "r")
        data = ""
        for i in fp:
            data += i

        return data

    def sendCommand(self, Command, cmdType, encoding="utf-8", default=1):

        if(default==GETFILE):
            Command=Command.split()[0]+" "+Command.split()[1]

        CommandBytes = Command.encode(encoding)
        bytesSend = bytes(c_int32(len(CommandBytes)))
        # print(bytesSend.decode("utf-8"))
        bytesSend = bytes(c_int8(cmdType)) + bytesSend + CommandBytes
        # print(bytesSend)
        self.totalSize = len(bytesSend)
        while self.sendSize < self.totalSize:
            hasSend = self.sock.send(bytesSend)
            if hasSend > 0:
                self.sendSize += hasSend

            else:
                print("-->disconnected")
                self.sock.close()
                return
        if default == GETFILE:
            if(len(cmd.split())>2):
                state = self.ReceiverMessage(filename=cmd.split()[2], default=GETFILE)
            else:
                state = self.ReceiverMessage(filename=cmd.split()[1], default=GETFILE)

        else:
            state = self.ReceiverMessage()
        self.reset()

        if default == 2 and state == self.TRUECOMMAND:
            try:
                msgdata = self.uploadFile(Command)

                if msgdata:
                    self.sendCommand(msgdata, UPLOADFILE)
            except Exception as e:
                print(e)

    def ReceiverMessage(self,  filename="", default=1):
        sizeReceived = 0
        bytesReceived = b""
        # self.sock.recv(self.BufSize)

        state = -1
        while True:
            if sizeReceived < self.SIZEOF_TYPE:
                data = self.sock.recv(self.SIZEOF_TYPE - sizeReceived)
                if data:
                    bytesReceived += data
                    sizeReceived += len(data)
            elif state == -1 and sizeReceived == self.SIZEOF_TYPE:
                state = int.from_bytes(bytesReceived, "little")
            elif sizeReceived < self.SIZEOF_META_DATA + self.SIZEOF_TYPE:
                data = self.sock.recv(self.SIZEOF_META_DATA + self.SIZEOF_TYPE - sizeReceived)
                if data:
                    bytesReceived += data

                    sizeReceived += len(data)
                else:
                    print("error")
                    return
            elif self.msgSize == -1 and sizeReceived == self.SIZEOF_META_DATA + self.SIZEOF_TYPE:
                self.msgSize = int.from_bytes(bytesReceived[self.SIZEOF_TYPE: self.SIZEOF_META_DATA], "little")

            elif sizeReceived < self.SIZEOF_TYPE + self.SIZEOF_META_DATA + self.msgSize:
                data = self.sock.recv(
                    min((self.SIZEOF_TYPE + self.SIZEOF_META_DATA + self.msgSize - sizeReceived), 1024))
                if data:
                    bytesReceived += data
                    sizeReceived += len(data)
                else:
                    print("msg recv error")
                    return
            elif sizeReceived == self.SIZEOF_TYPE + self.SIZEOF_META_DATA + self.msgSize:
                break

        data = bytesReceived[self.SIZEOF_TYPE + self.SIZEOF_META_DATA:].decode("utf-8")
        if state == self.TRUECOMMAND:
            if default == GETFILE:
                f = open(filename, "w")
                f.write(data)
                f.close()


            else:
                print("-->", data)



        else:
            print("-->", data)

        return state

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


if __name__ == "__main__":
    ftpClient = FTP_Client()
    ftpClient.connection()

    while True:
        cmd = input("-->")
        if cmd:
            # if ftpClient.Judge(cmd):
            cmdType = cmd.split()
            if cmdType[0].lower() == "put":
                ftpClient.sendCommand(cmd, NORMALCOMMAND, default=UPLOADFILE)
            elif cmdType[0].lower() == "get":

                ftpClient.sendCommand(cmd, NORMALCOMMAND, default=GETFILE)

            else:
                ftpClient.sendCommand(cmd, NORMALCOMMAND)


                # else:
                # print("Command not found")
        else:
            break
    ftpClient.close()
