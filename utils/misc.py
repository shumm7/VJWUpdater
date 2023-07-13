import os, json, datetime, re, tkinter
import urllib.error
import urllib.request
import urllib.parse
import requests

class Log:
    def print(msg: str, _type: str, category: str, logging: bool = True):
        if category!=None:
            if len(category)>0:
                category = f"<{category}>"
        else:
            category = ""
        
        if _type=="info":
            _type="INFO"
        elif _type=="warn":
            _type="WARN"
        elif _type == "error":
            _type="ERROR"
        else:
            _type = "UNKNOWN"

        if type(msg)==type(""):
            if logging:
                with open("log.txt", "a", encoding="utf-8") as fp:
                    fp.write(f'[{datetime.datetime.now()}][{_type}]{category} {msg}\n')

                
                print(f'[{datetime.datetime.now()}][{_type}]{category} {msg}')
    
    def append(msg: str):
        if type(msg)==type(""):
            with open("log.txt", "a", encoding="utf-8") as fp:
                fp.write(f'[{datetime.datetime.now()}] {msg}\n')

    def exception(e: Exception, msg: str = None, category: str = None):
        if type(msg)!=type(""):
            msg = "Unknown exception has occured."
        if category!=None:
            if len(category)>0:
                category = f"<{category}>"
        else:
            category = ""
        
        Log.append(f'[{datetime.datetime.now()}][ERROR]{category} {msg}\n\tdetail: {e}')
        Log.print(msg, "error", category, False)
        

class String:
    def wiki_format(string: str) -> str:
        return string.replace("/", "").replace("?", "").replace(":", "").replace("#", "")
    
    def wiki_template(template: str, args: dict, div: str = "") -> str:
        ret: str = "{{" + template + div
        for key,value in args.items():
            ret += f"|{key}={value}{div}"
        
        ret += "}}"
        return ret

    def wiki_mklist(ls: list, div: str = "\n") -> str:
        ret: str = ""

        for v in ls:
            if len(ret)!=0:
                ret += div
            ret += v
        return ret



class JSON:
    def __create__(filename: str, formats: dict) -> None:
        """ Create a json file """
        
        file_path = filename
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as fp:
                json.dump(formats, fp, indent=2)


    def read(filename: str, force: bool = True) -> dict:
        """Read json file"""
        try:
            with open(filename, "r", encoding='utf-8') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            if force:
                JSON.__create__(filename, {})
                return JSON.read(filename, False)
        return data

    def save(filename: str, data: dict) -> None:
        """Save data to json file"""
        try:
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            JSON.__create__(filename, {})
            return JSON.save(filename, data)

class Fetch:
    def download(url, dst_path):
        with urllib.request.urlopen(url, timeout=10) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)

class ApiData:
    def agent_from_uuid(uuid: str) -> dict:
        agents = JSON.read("api/agents.json")

        for agent in agents:
            if agent["uuid"] == uuid:
                return agent
        return None

    def buddy_from_uuid(uuid: str) -> dict:
        buddies = JSON.read("api/buddies.json")

        for buddy in buddies:
            if buddy["uuid"]==uuid:
                return buddy
        return None

    def buddy_from_charmlevel_uuid(uuid: str) -> dict:
        buddies = JSON.read("api/buddies.json")

        for buddy in buddies:
            for level in buddy["levels"]:
                if level["uuid"]==uuid:
                    return buddy
        return None
    def spray_from_uuid(uuid: str) -> dict:
        sprays = JSON.read("api/sprays.json")

        for spray in sprays:
            if spray["uuid"]==uuid:
                return spray
        return None

    def playercard_from_uuid(uuid: str) -> dict:
        playercards = JSON.read("api/playercards.json")

        for playercard in playercards:
            if playercard["uuid"]==uuid:
                return playercard
        return None

    def playertitle_from_uuid(uuid: str) -> dict:
        playertitles = JSON.read("api/playertitles.json")

        for playertitle in playertitles:
            if playertitle["uuid"]==uuid:
                return playertitle
        return None
            
class Misc:
    class CoreList:
        Agent = [
            "9f0d8ba9-4140-b941-57d3-a7ad57c6b417", #Brimstone
            "707eab51-4836-f488-046a-cda6bf494859", #Viper
            "8e253930-4c05-31dd-1b6c-968525494517", #Omen
            "1e58de9c-4950-5125-93e9-a0aee9f98746", #Killjoy
            "117ed9e3-49f3-6512-3ccf-0cada7e3823b", #Cypher
            "320b2a48-4d9b-a075-30f1-1f93a9b638fa", #Sova
            "569fdd95-4d10-43ab-ca70-79becc718b46", #Sage
            "eb93336a-449b-9c1b-0a54-a891f7921d69", #Phoenix
            "add6443a-41bd-e414-f6ad-e58d267f4e95", #Jett
            "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc", #Reyna
            "f94c3b30-42be-e959-889c-5aa313dba261", #Raze
            "5f8d3a7f-467b-97f3-062c-13acf203c006", #Breach
            "6f2a04ca-43e0-be17-7f36-b3908627744d", #Skye
            "7f94d92c-4234-0a36-9646-3a87eb8b5c89", #Yoru
            "41fb69c1-4189-7b37-f117-bcaf1e96f1bf", #Astra
            "601dbbe7-43ce-be57-2a40-4abd24953621", #KAY/O
            "22697a3d-45bf-8dd7-4fec-84a9e28c69d7", #Chamber
            "bb2a4828-46eb-8cd1-e765-15848195d751", #Neon
            "dade69b4-4f5a-8528-247b-219e5a1facd6", #Fade
            "95b78ed7-4637-86d9-7e41-71ba8c293152", #Harbor
            "e370fa57-4757-3604-3648-499e1f642d3f", #Gekko
            "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235" #Deadlock
        ]

        CompetitiveTiersName = [
            "Iron",
            "Bronze",
            "Silver",
            "Gold",
            "Platinum",
            "Diamond",
            "Ascendant",
            "Immortal",
            "Radiant"
        ]

        def Act() -> list:
            seasons: dict = JSON.read("api/seasons.json")
            out: dict = {}
            out_list: list = []

            for season in seasons:
                if season["parentUuid"]!=None:
                    parent = season["parentUuid"]
                    episode: int
                    act: int

                    for ep_season in seasons:
                        if ep_season["uuid"]==parent:
                            episode = int(re.findall('[0-9]+', ep_season["displayName"]["en-US"])[0])
                            break
                    
                    act = int(re.findall('[0-9]+', season["displayName"]["en-US"])[0])
                    uuid = season["uuid"]
                    key = int(str(episode)+str(act))

                    out[key] = uuid

            sorted_dict: dict = dict(sorted(out.items()))
            for item in sorted_dict.values():
                out_list.append(item)
            return out_list

        def remove_list_from_uuid(_list: list, uuid: str):
            return [i for i in _list if i["uuid"]!=uuid]

    
