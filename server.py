from rich.console import Console
import socket
import json
import threading
import time
import atexit
import sys
import os
import urllib.parse

console = Console()
threads = {}
messages = [
        {"IP":"127.0.0.1","from":"Server","msg":"Server Started","time":time.time(),"version":"xchat-server"}
]
threadList = []
users = {}

try:
    config = json.load(open("config.json"))
except:
    config = {
        "eula":False,
        "port":False,
        "asp":True
    }

if config["eula"] == False:
    if console.input(
        """I have read and agree to the disclaimer(https://thisisxd.tk/index.php/archives/262/).(y/n): """
        ) == "y":
        config["eula"] = True
    else:
        sys.exit()

def saveMsg():
    global config,  messages
    try:
        os.mkdir("logs")
    except:
        pass

    json.dump(
            messages,
            open(f"./logs/{int(time.time())}.log", "w")
    )
    json.dump(
        config,
        open("config.json", "w")
    )

    sys.exit(0)

atexit.register(saveMsg)

http_msgid = {}
def http_handle(sock, addr, recv_data):
    global console, messages, http_msgid
    path = urllib.parse.unquote(recv_data).split("\r\n")[0].split(" ")[1].split("/")
    resp_data = "HTTP/1.1 200 OK \r\n\r\n"
    console.log(path)
    if path[1] == "getMsg":
        try:
            console.log(http_msgid[addr[0]])
        except:
            http_msgid[addr[0]] = 0
        
        resp_data += json.dumps(messages[http_msgid[addr[0]]:])
        http_msgid[addr[0]] = messages.__len__() 
        # else:
            # resp_data += "[]"
    elif path[1] == "Send":
        messages += [
            {
                "IP":addr[0],
                "version":"xchat-v2 http",
                "from":path[2],
                "time":time.time(),
                "msg":path[3]
            }
        ]
        resp_data += "Done"
    sock.send(resp_data.encode("utf-8"))
    sock.close()
    return True

def handle(sock, addr):
    global console, messages, threads, threadList, users
    msgid = 0
    username = ""
    version = "xchat-v1"

    while True:
        resp_data = {
            "code":200,
            "msg":"OK",
            "data":{}
        }

        recv_data = sock.recv(1024)
        try:
            recv_data = recv_data.decode("utf-8")
            try:
                recv_data = json.loads(recv_data)
            except:
                if http_handle(sock,addr,recv_data):
                    return 0
                

            if username != "":
                if recv_data["mode"] == "getMsg":
                    try:
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
                            "version":version,
                            "IP":addr[0]
                        }
                    ]
                    console.log(f"[CHAT] <{username}({version})> {recv_data['data']['msg']}")

                elif recv_data["mode"] == "exit":
                    sock.close()
                    return 0

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
                username = recv_data["data"]["username"]
                # threads[addr[1]].setName(username)
                users[addr[1]] = username
                try:
                    version = recv_data["data"]["version"]
                except:
                    pass

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
    if config["port"] == False:
        port = int(console.input("[blue]Port: "))
        if config["asp"]:
            rem = console.input(
                "[blue]Remember the port (y/n)? [/]"
            )
            if rem == "y":
                config["port"] = port
            elif rem == "n":
                config["asp"] = False
    else:
        port = config["port"]


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(
        (
            "",
            port
        )
    )
    sock.listen(128)
    console.log(f"Server started on 0.0.0.0:{port}.")

    while True:
        s, addr = sock.accept()
        console.log(f"{addr} connected to this server.")
        threadList += [addr[1]]
        users[addr[1]] = ""

        threads[addr[1]] = threading.Thread(None, lambda: handle(s, addr))
        threads[addr[1]].setDaemon(True)
        threads[addr[1]].start()
