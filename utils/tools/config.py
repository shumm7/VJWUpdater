import os
from utils.tools.json import JSON

class Config:
    data = {
        "lang": "ja-JP",
        "api": "https://valorantjp.miraheze.org/w/api.php",
        "theme": "system",
        "logo": "",
        "wikibot": {
            "id": "",
            "password": ""
        }
    }

    def read() -> dict:
        if not os.path.exists("config.json"):
            JSON.save("config.json", Config.data)

        j = JSON.read("config.json")
        ret = {}

        for i in Config.data.keys():
            ret[i] = j.get(i, Config.data[i])
        return ret

    def save(cfg: dict) -> None:
        ret = {}
        for i in Config.data.keys():
            ret[i] = cfg.get(i, Config.data[i])
            
            JSON.save("config.json", ret)
    
    def save_key(key:str, value:str):
        ret = Config.read()

        ret[key] = value
        Config.save(ret)
    
    def read_key(key: str):
        ret = Config.read()
        return ret.get(key, Config.data.get("key", None))

