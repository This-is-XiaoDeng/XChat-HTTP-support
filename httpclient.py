from rich.console import Console
import urllib.parse
import json
import time

console = Console()

http_msgid = {}
def http_handle(sock, addr, recv_data, messages):
    global console, http_msgid
    path1 = recv_data.split("\r\n")[0].split(" ")[1].split("/")
    # path = urllib.parse.unquote(path1)
    path = []
    for i in path1:
        path += [urllib.parse.unquote(i)]
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