from rich.console import Console
import socket
import json
import threading
import time
import atexit
import httpclient
import sys
import os
import initcfg

console = Console()
threads = {}
messages = [
        {"from":"Server","msg":"Server Started","time":time.time(),"version":"xchat-v3 server","IP":"127.0.0.1"}
]
threadList = []
users = {}

try:
    config = json.load(open("config.json"))
except:
    config = {}

config = initcfg.init(config)

if config["eula"] == False:
    if console.input(
        """I have read and agree to the disclaimer(https://thisisxd.tk/index.php/archives/262/).(y/n): """
        ) == "y":
        config["eula"] = True
    else:
        sys.exit()

def saveMsg(exit = True):
    global config,  messages
    json.dump(
        config,
        open("config.json", "w")
    )
    if exit:
        sys.exit()

atexit.register(saveMsg)

def handle(sock, addr):
    global console, messages, threads, threadList, users, config
    msgid = 0
    username = ""
    version = "xchat-v1 unkown"

    if config["max_resp_msg"] <= messages.__len__():
        msgid = messages.__len__() - config["max_resp_msg"]

    while True:
        # 重置 resp_data
        resp_data = {
            "code":200,
            "msg":"OK",
            "data":{}
        }

        recv_data = sock.recv(1024)

        try:
            try:
                recv_data = recv_data.decode("utf-8")
            except:
                recv_data = recv_data.decode("gbk")

            try:
                recv_data = json.loads(recv_data)
            except:
                httpclient.http_handle(sock, addr, recv_data, messages)

            if username != "":
                if recv_data["mode"] == "getMsg":
                    try:
                        # 限制返回数据量
                        if config["max_resp_msg"] <= messages.__len__():
                            msgid = messages.__len__() - config["max_resp_msg"]
                            
                        resp_data["data"]["messages"] = messages[msgid:]
                        msgid = messages.__len__()

                    except:
                        resp_data["data"]["messages"] = []

                elif recv_data["mode"] == "sendMsg":
                    messages += [
                        {
                            "from":username,
                            "msg":recv_data["data"]["msg"],
                            "time":time.time(),
                            "version":version
                        }
                    ]
                    console.log(f"[CHAT] <{username}({version})> {recv_data['data']['msg']}")

                elif recv_data["mode"] == "getList":
                    userList = []
                    for t in threadList:
                        if threads[t].is_alive():
                            userList += [users[t]]
                    resp_data["data"]["list"] = userList

                else:
                    resp_data["code"] = 404
                    resp_data["msg"] = "Unkown mode"

            elif recv_data["mode"] == "login":
                if config["server"]["passwd"]:
                    try: passwd = recv_data["data"]["passwd"]
                    except: passwd = None
                else:
                    passwd = None
                console.log(passwd,config["server"]["msg"])
                if passwd == config["server"]["passwd"]:
                    username = recv_data["data"]["username"]
                    users[addr[1]] = username
                    try: version = recv_data["data"]["version"]
                    except: pass
                else:
                    resp_data["code"] = 403
                    resp_data["msg"] = "Wrong Password"

            else:
                resp_data["code"] = 403
                resp_data["msg"] = "Please Login First"


        except Exception as e:
            console.print_exception(show_locals=True)
            resp_data["code"] = 500
            resp_data["msg"] = "Internal Server Error"
            resp_data["data"]["exception"] = str(e)

        # 回复
        resp_data = json.dumps(resp_data)
        sock.send(resp_data.encode("utf-8"))



if __name__ == "__main__":
    if config["server"]["port"] == None:
        port = int(console.input("[blue]Port: "))
        if config["server"]["save_port"] == None:
            rememberPort = console.input(
                "[blue]Remember the port (y/n)? [/]"
            )
            if rememberPort == "y":
                config["server"]["port"] = port
                config["server"]["save_port"] == True
            elif rememberPort == "n":
                config["server"]["save_port"] = False
    else:
        port = config["server"]["port"]


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(
        (
            "",
            port
        )
    )
    sock.listen(128)
    console.log(f"Server started on 0.0.0.0:{port}.")

    saveMsg(False)

    while True:
        s, addr = sock.accept()
        console.log(f"{addr} connected to this server.")
        threadList += [addr[1]]
        users[addr[1]] = ""

        threads[addr[1]] = threading.Thread(None, lambda: handle(s, addr))
        threads[addr[1]].setDaemon(True)
        threads[addr[1]].start()
