import tkinter, os, datetime, math
import tkinter.simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData
from utils.vlr import VLR, VLR_Event
from utils.api import API
from utils.wiki import Wiki

class Esports():
    root: tkinter.Tk
    wiki: Wiki
    force: bool

    def __init__(self, root: tkinter.Tk, wiki: Wiki, force: bool = False) -> None:
        self.root = root
        self.wiki = wiki
        self.force = force
    
    def match(self):
        _ftype = "CORE.ESPORTS.MATCH"

        id = tkinter.simpledialog.askstring("Match", "VLR.ggのMatch IDを入力してください。", initialvalue="170956")
        id = id.replace("https://www.vlr.gg/", "").replace("https://vlr.gg/", "")

        vlr = VLR(id)
        data = vlr.get_data()

        # patch
        patch = data["patch"]

        # date
        dt = datetime.datetime.strptime(data["date"] + '+0000', '%Y-%m-%d %H:%M:%S%z')
        dt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=+14)))
        date = datetime.datetime.strftime(dt, '%Y-%m-%d')
        time = datetime.datetime.strftime(dt, '%H:%M')

        # vlr
        vlr = data["vlr"]["id"]

        # vods
        vod = data["vod"]

        # team
        team1 = data["team"]["long"][0]
        team2 = data["team"]["long"][1]

        # map count
        map_count = str(data["score"][0]) + "-" + str(data["score"][1])

        # player
        playerlist = []
        for tm in data["player"]:
            players = []
            for p in tm.values():
                players.append(p["name"])
            playerlist.append(players)

        # map
        i = 1
        map: str = ""
        duration: str = ""
        score: str = ""
        player: list = ["", ""]
        acs: list = ["", ""]
        kda: list = ["", ""]
        kast: list = ["", ""]
        adr: list = ["", ""]
        hs: list = ["", ""]
        fk: list = ["", ""]
        fd: list = ["", ""]
        agent: list = ["", ""]
        round: str = ""
        side: str = ""

        for match in data["match"]:
            map = map + f"|map{i}=" + match["map"] + " "
            
            if match.get("duration")!=None:
                score = score + f"|score{i}=" + str(match["score"][0]) + "-" + str(match["score"][1]) + " "
                duration = duration + f"|duration{i}=" + match["duration"] + " "
                round = round + f"|round{i}="

                for team in [0, 1]:
                    player[team] = player[team] + f"|player{i}-{team+1}="
                    acs[team] = acs[team] + f"|acs{i}-{team+1}="
                    kda[team] = kda[team] + f"|kda{i}-{team+1}="
                    kast[team] = kast[team] + f"|kast{i}-{team+1}="
                    adr[team] = adr[team] + f"|adr{i}-{team+1}="
                    hs[team] = hs[team] + f"|hs%{i}-{team+1}="
                    fk[team] = fk[team] + f"|fk{i}-{team+1}="
                    fd[team] = fd[team] + f"|fd{i}-{team+1}="
                    agent[team] = agent[team] + f"|agent{i}-{team+1}="

                    for p in match["player"][team].values():
                        player[team] = player[team] + p["name"] + "; "
                        acs[team] = acs[team] + str(p["acs"]) + "; "
                        kda[team] = kda[team] + str(p["kill"]) + "-" + str(p["death"]) + "-" + str(p["assist"]) + "; "
                        kast[team] = kast[team] + str(p["kast"]) + "; "
                        adr[team] = adr[team] + str(p["adr"]) + "; "
                        hs[team] = hs[team] + str(p["hs%"]) + "; "
                        fk[team] = fk[team] + str(p["fk"]) + "; "
                        fd[team] = fd[team] + str(p["fd"]) + "; "
                        agent[team] = agent[team] + p["agent"].lower() + "; "

                    player[team] = player[team] + "\n"
                    acs[team] = acs[team] + "\n"
                    kda[team] = kda[team] + "\n"
                    kast[team] = kast[team] + "\n"
                    adr[team] = adr[team] + "\n"
                    hs[team] = hs[team] + "\n"
                    fk[team] = fk[team] + "\n"
                    fd[team] = fd[team] + "\n"
                    agent[team] = agent[team] + "\n"
                
                for r in match["round"].values():
                    if r["team"]==1:
                        round = round + "w-" + r["type"] + "; "
                    elif r["team"]==2:
                        round = round + "l-" + r["type"] + "; "
                
                if match["round"][1]["team"]==1:
                    if match["round"][1]["side"]=="attacker":
                        side = side + f"|side{i}=attacker "
                    else:
                        side = side + f"|side{i}=defender "
                else:
                    if match["round"][1]["side"]=="attacker":
                        side = side + f"|side{i}=defender "
                    else:
                        side = side + f"|side{i}=attacker "
                
                round = round +  "\n"
            i = i + 1
        

        # map veto
        mapveto: str = "|mapveto="
        mapveto_action: str = "|mapveto-action="
        mapveto_team: str = "|mapveto-team="

        for veto in data["map_veto"]:
            mapveto = mapveto + veto["map"] + "; "
            mapveto_action = mapveto_action + veto["action"] + "; "
            mapveto_team = mapveto_team + str(veto["team"]) + "; "
        
        # vods
        vod = ""
        i = 1
        for v in data["vod"]:
            vod = vod + f"|vod{i}={v}\n"
            i = i + 1


        template = f"|team1={team1} |team2={team2}\n"
        template = template + f"|score={map_count}\n"
        template = template + f"|date={date} |time={time} |patch={patch}\n"
        template = template + f"|vlr={vlr}"
        template = template + f"{map}\n"
        template = template + f"{duration}\n"
        template = template + f"{score}\n\n"
        template = template + player[0]
        template = template + agent[0]
        template = template + acs[0]
        template = template + kda[0]
        template = template + kast[0]
        template = template + adr[0]
        template = template + hs[0]
        template = template + fk[0]
        template = template + fd[0] + "\n"
        template = template + player[1]
        template = template + agent[1]
        template = template + acs[1]
        template = template + kda[1]
        template = template + kast[1]
        template = template + adr[1]
        template = template + hs[1]
        template = template + fk[1]
        template = template + fd[1] + "\n"
        template = template + round
        template = template + side + "\n"
        template = template + mapveto + "\n"
        template = template + mapveto_action + "\n"
        template = template + mapveto_team + "\n\n"
        template = template + vod

        template = "{{Match\n" + template + "}}<noinclude>\n[[Category:試合結果]]\n</noinclude>"
        
        os.makedirs(f"output/wiki/match", exist_ok=True)
        with open("output/wiki/match/" + data["vlr"]["id"] + ".txt", "w", encoding="utf-8") as fp:
            fp.write(template)

        Log.print("テンプレートの生成が完了しました。", "info", _ftype)

    def matchlist(self):
        _ftype = "CORE.ESPORTS.MATCHLIST"

        id = tkinter.simpledialog.askstring("Match list", "VLR.ggのMatch IDを入力してください。", initialvalue="170956")
        id = id.replace("https://www.vlr.gg/", "").replace("https://vlr.gg/", "")

        vlr = VLR(id)
        data = vlr.get_data()

        # vlr
        vlr = data["vlr"]["id"]

        # vods
        vod = data["vod"]

        # team
        team1 = data["team"]["long"][0]
        team2 = data["team"]["long"][1]

        # map count
        map_count = str(data["score"][0]) + "-" + str(data["score"][1])

        # player
        playerlist = []
        for tm in data["player"]:
            players = []
            for p in tm.values():
                players.append(p["name"])
            playerlist.append(players)

        # map
        i = 1
        map: str = ""
        score: str = ""
        player: list = ["", ""]
        agent: list = ["", ""]

        for match in data["match"]:
            map = map + f"|map{i}=" + match["map"] + " "
            
            if match.get("duration")!=None:
                score = score + f"|score{i}=" + str(match["score"][0]) + "-" + str(match["score"][1]) + " "

                for team in [0, 1]:
                    player[team] = player[team] + f"|player{i}-{team+1}="
                    agent[team] = agent[team] + f"|agent{i}-{team+1}="

                    for p in match["player"][team].values():
                        player[team] = player[team] + p["name"] + "; "
                        agent[team] = agent[team] + p["agent"].lower() + "; "

                    player[team] = player[team] + "\n"
                    agent[team] = agent[team] + "\n"
                
            i = i + 1
        
        # vods
        vod = ""
        i = 1
        for v in data["vod"]:
            vod = vod + f"|vod{i}={v}\n"
            i = i + 1


        template = f"|team1={team1} |team2={team2}\n"
        template = template + f"|score={map_count}\n"
        template = template + f"{map}\n"
        template = template + f"{score}\n"
        template = template + player[0]
        template = template + agent[0]
        template = template + player[1]
        template = template + agent[1]
        template = template + vod
        template = template + f"|vlr={vlr}"

        template = "{{Match list\n" + template + "\n}}"
        
        os.makedirs(f"output/wiki/matchlist", exist_ok=True)
        with open("output/wiki/matchlist/" + data["vlr"]["id"] + ".txt", "w", encoding="utf-8") as fp:
            fp.write(template)

        Log.print("テンプレートの生成が完了しました。", "info", _ftype)
        
    def roster(self):
        _ftype = "CORE.ESPORTS.ROSTER"

        id = tkinter.simpledialog.askstring("Roster", "VLR.ggのEvent IDを入力してください。", initialvalue="1494")
        id = id.replace("https://www.vlr.gg/event/", "").replace("https://vlr.gg/event/", "")
        event_title = ""

        if id in "/":
            s = id.split("/", 1)
            id = s[0]
            event_title = s[1]

        vlr = VLR_Event(id, event_title)
        data = vlr.get_data()

        template: str = ""
        for team in data.get("teams", []):
            title = team.get("title", "")
            template = template + "{{Roster|team=" + title + "|image=" + title + " logo.png"

            i: int = 1
            for player in team.get("players", []):
                template = template + f"|p{i}=" + player
                i = i + 1
            
            template = template + "|header=|qualifier=}}\n"
        
        template = "{{Rosters-begin}}\n" + template + "{{Rosters-end}}"
        
        os.makedirs(f"output/wiki/roster", exist_ok=True)

        filename = "output/wiki/roster/" + (event_title.replace("/", "-")) + ".txt"
        if len(event_title)==0:
            filename = filename = "output/wiki/roster/" + id.replace("/", "-") + ".txt"

        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(template)

        Log.print("テンプレートの生成が完了しました。", "info", _ftype)
        