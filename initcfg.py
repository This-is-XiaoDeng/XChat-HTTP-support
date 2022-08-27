def init(cf: dict) -> dict:
    config = cf
    keys = list(config.keys())
    
    if not("eula" in keys):
        config["eula"] = False
    
    if not("max_resp_msg" in keys):
        config["max_resp_msg"] = 15

    if not("server" in keys):
        config["server"] = {}

    keys = list(config["server"].keys())

    if not("port" in keys):
        config["server"]["port"] = None

    if not("save_port" in keys):
        config["server"]["save_port"] = None

    if not("passwd" in keys):
        config["server"]["passwd"] = None

    return config
         