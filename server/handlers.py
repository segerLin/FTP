# coding=utf-8

from response_helper import make_response, send_data

import subprocess
import shlex
import os

ROOT_DIRNAME = "ftp"
ROOT_PATH = os.path.dirname( os.path.realpath(__file__) ) + "/" + ROOT_DIRNAME + "/"
CWD = ROOT_PATH

def system_call(args):
    """
    以args为参数调用系统命令
    :param args: 参数列表, [0] 为 命令名
    :return: status_code, stdout, stderr
    """
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out, err

def restrain_dir(args):
    """
    限制绝对路径和相对路径到程序指定的位置
    :param args:
    :return:
    """
    if len(args) > 1:
        abs_paths = []
        rel_paths = []
        opts = []
        for arg in args[1:]:
            if arg.startswith("-"):
                opts.append(arg)
            elif arg.startswith("/"):
                # 用限定过的根目录替换根
                arg = arg.replace("/", CWD, 1)
                abs_paths.append( os.path.realpath( arg ))
            else:
                rel_paths.append(os.path.realpath( CWD + arg ))

        args = [ args[0] ] + abs_paths + rel_paths + opts

        if len(abs_paths) == 0 and len(rel_paths) == 0:
            args.insert(1, CWD)
        print("altered:", args)

    return args

class FTPCommandHandler:

    """
    用于处理命令
    """

    def __init__(self, callback_table):
        """
        初始化FTPCommandHandler
        :param callback_table: 回调函数表
        :return:
        """
        self.callback_table = callback_table

    def handle(self, client, address, command):
        print("Command:", command)
        # 解析args
        args = shlex.split(command)
        if len(args) == 0:
            reply = make_response(1, "invalid command")
            send_data(client, address, reply)
            return restrain_dir(args)

        # 命令名
        cmd = args[0]

        if not cmd in self.callback_table:
            reply = make_response(1, "Command '{}' doesn't exist.".format(cmd))
        else:
            code, stdout, stderr = self.callback_table[cmd](args)
            if code != 0:
                reply = make_response(code, stderr)
            else:
                reply = make_response(code, stdout)

        send_data(client, address, reply)

        return restrain_dir(args)


class FileHandler:

    def __init__(self):
        pass

    def handle(self, client, address, filename, content):
        if filename.endswith("/"):
            reply = make_response(1, "Invalid filename")
        elif filename.strip() == "":
            reply = make_response(1, "Invalid filename")
        else:
            with open(filename, "wb") as f:
                f.write(content)
            reply = make_response(0, "uploaded")
        send_data(client, address, reply)



def ls_callback(args):
    print("/ -->", CWD)
    if len(args) == 1:
        args = [args[0], CWD]
    else:
        args = restrain_dir(args)

    return system_call(args)

def open_callback(args):
    if len(args) > 2:
        return 1, b'', b"can't open multiple files at the same time"
    elif len(args) < 2:
        return 2, b'', b"please specify a single file name."
    args = restrain_dir(args)
    args[0] = "cat"
    return system_call(args)

def cd_callback(args):
    global CWD
    if len(args) > 2:
        return 1, b'', b"invalid command: cd requires only one argument"
    if len(args) == 1:
        return 3, b'', b"invalid command: cd requires one argument"

    args = restrain_dir(args)
    # 目标路径
    dest = args[1]
    if not dest.endswith("/"):
        dest = dest + "/"

    if not dest.startswith(ROOT_PATH):
        # print()
        # 防止用户不停 cd ../
        dest = ROOT_PATH

    print("dest:", dest)

    if os.path.isdir(dest):
        CWD = dest
        return 0, b'INTO ' + dest.encode("UTF-8"), b''
    else:
        return 2, b'', b"invalid path"

def rm_callback(args):
    global CWD
    if len(args) == 1:
        return 1, b'', b"require one single argument."
    if len(args) > 2:
        return 2, b'', b"require one single argument."
    args = restrain_dir(args)
    # 需要删除的文件
    file_to_remove = args[1]
    if os.path.isfile(file_to_remove):
        print("removing", file_to_remove)
        os.unlink(file_to_remove)
        return 0, b'deleted', b""
    else:
        print("file not found")
        return 3, b"", b"File not found or it is a dir."

def get_callback(args):
    """
    传输文件给客户端
    :param args:
    :return:
    """
    if len(args) == 1:
        return 1, b'', b"require one single argument."
    args = restrain_dir(args)
    file = args[1]
    if os.path.isfile(file):
        with open(file, mode="rb") as f:
            return 0, f.read(-1), b''
    return 2, b'', b"file not exist or it is a dir"

def put_callback(args):
    if len(args) == 1:
        return 1, b'', b"require one single argument."
    if len(args) > 2:
        return 2, b'', b"require one single argument."

    # args = restrain_dir(args)
    return 0, b'ready to receive the file.', b''
