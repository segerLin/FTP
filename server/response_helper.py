# coding=utf-8

import ctypes

def send_data(client, address, data):
    size_sent = 0
    size_to_send = len(data)
    while size_sent < size_to_send:
        # 数据还没有发送完毕的时候
        # 发送剩余部分的数据
        try:
            num = client.send(data[size_sent:])
        except Exception as e:
            print(e)
            return
        if num > 0:
            size_sent += num
        else:
            print("client {} disconnected.".format(address))
            return

def make_response(status_code, message):
        if not isinstance(message, bytes):
            message = bytes(message, encoding="UTF-8")
        data_size = bytes(ctypes.c_int32(len(message)))
        return bytes(ctypes.c_int8(status_code)) + data_size + message
