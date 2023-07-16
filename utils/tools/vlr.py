import requests, bs4, datetime
from utils.tools.api import API
from utils.tools.wiki import Wiki

class VLR():
    match_id: str
    url: str
    soup: bs4.BeautifulSoup

    def __init__(self, match_id: str) -> None:
        self.match_id = match_id
        self.url = f"https://www.vlr.gg/{match_id}"

        res = requests.get(self.url)
        res.raise_for_status()
        self.soup = bs4.BeautifulSoup(res.text, "html.parser")
    
    def get_data(self) -> dict:
        team = self.get_team()
        team_short = self.get_team_short()
        score = self.get_map_count()
        players = self.get_players()
        map_veto = self.get_map_veto()
        match = self.get_match()
        date = self.get_date()
        patch = self.get_patch()
        vod = self.get_vods()


        return {
            "date": date,
            "patch": patch,
            "vlr": {
                "url": self.url,
                "id": self.match_id
            },
            "team": {
                "long": team,
                "short": team_short
            },
            "player": players,
            "score": score,
            "map_veto": map_veto,
            "match": match,
            "vod": vod
        }

    def get_team(self) -> tuple[str]:
        res = []
        for e in self.soup.select(".match-header-link-name .wf-title-med"):
            res.append(e.get_text(strip=True))
        return (res[0], res[1])

    def get_team_short(self) -> tuple[str]:
        res = []

        sp = self.soup.find("div", {"class": "vm-stats-game", "data-game-id": "all"})
        for tbl in sp.select(".mod-overview"):
            short = tbl.select_one(".mod-player .ge-text-light").get_text(strip=True)
            res.append(short)
        return (res[0], res[1])

    def get_map_count(self) -> tuple[int]:
        res = []
        for e in self.soup.select(".match-header-vs-score-winner, .match-header-vs-score-loser"):
            res.append(int(e.get_text(strip=True)))
        return (res[0], res[1])
    
    def get_patch(self) -> str:
        for e in self.soup.select_one(".match-header-date").select("div"):
            if not "moment-tz-convert" in e.attrs.get("class", []):
                return e.getText(strip=True).replace("Patch ", "")
    
    def get_date(self) -> str:
        for e in self.soup.select_one(".match-header-date").select("div"):
            if "moment-tz-convert" in e.attrs.get("class", []):
                return e.attrs["data-utc-ts"]
    
    def get_players(self) -> list:
        players: list = []
        div = self.soup.find("div", {"class":"vm-stats-game", "data-game-id":"all"})

        for tbl in div.select("table.mod-overview > tbody"):
            player_team = {}
            for tr in tbl.find_all("tr"):
                player = {}
                player["name"] = tr.select_one("td.mod-player > div div").get_text(strip=True)
                

                i=1
                for td in tr.select("td.mod-stat"):
                    if i==1:
                        player["rating"] = float(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    elif i==2:
                        player["acs"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    elif i==3:
                        player["kill"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    elif i==4:
                        player["death"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    elif i==5:
                        player["assist"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    elif i==7:
                        player["kast"] = int(td.select_one("span.mod-both").get_text(strip=True).replace('%', '') or -1)
                    elif i==8:
                        player["adr"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    elif i==9:
                        player["hs%"] = int(td.select_one("span.mod-both").get_text(strip=True).replace('%', '') or -1)
                    elif i==10:
                        player["fk"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    elif i==11:
                        player["fd"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                    i = i + 1
                player_team[player["name"]] = player
            players.append(player_team)

        return players


    def get_match(self) -> list[str]:
        r = []
        
        # Get Map name
        map_dict={}
        for btn in self.soup.select(".vm-stats-gamesnav .vm-stats-gamesnav-item"):
            if btn["data-game-id"]!="all":
                text = btn.find("div")
                span = text.find("span")
                if span!=None:
                    text.find("span").decompose()
                mapname = text.get_text(strip=True).lower()
                map_dict[str(btn["data-game-id"])] = {"name": mapname, "id": str(btn["data-game-id"])}

        # Detail
        for map in map_dict.values():
            div: bs4.BeautifulSoup = None
            for d in self.soup.select(".vm-stats-game "):
                if d["data-game-id"]==map["id"]:
                    div = d
                    break
            
            res = {}
            if div==None:
                res["map"] = map["name"]
                r.append(res)
            else:
                # map name
                res["map"] = map["name"]

                # duration
                header_div = div.select_one(".vm-stats-game-header")
                res["duration"] = header_div.select_one(".map-duration").get_text(strip=True)

                # score
                score: list = []
                for s in header_div.select(".team .score"):
                    score.append(s.get_text(strip=True))
                res["score"] = (int(score[0]), int(score[1]))

                # rounds
                rounds: dict = {}
                for rnd in div.select(".vlr-rounds .vlr-rounds-row-col"):
                    num = rnd.select_one(".rnd-num")
                    if num!=None:
                        i = 1
                        num = int(num.get_text(strip=True))
                        win: int = 1
                        lose: int = 2
                        type: str
                        side: str
                        for sq in rnd.select(".rnd-sq"):
                            if "mod-win" in sq.attrs["class"]:
                                # type
                                win = i
                                img = sq.find("img")["src"]

                                if "elim" in img:
                                    type = "elimination"
                                elif "boom" in img:
                                    type="detonate"
                                elif "defuse" in img:
                                    type="defuse"
                                elif "time" in img:
                                    type="timeup"

                                
                                if win==1:
                                    lose = 2
                                elif win==2:
                                    lose = 1
                                
                                # side
                                if "mod-t" in sq.attrs["class"]:
                                    side = "attacker"
                                elif "mod-ct" in sq.attrs["class"]:
                                    side = "defender"

                                    
                                rounds[num] = {"team": win, "type": type, "side": side}

                            i = i + 1
                res["round"] = rounds

                # player
                players: list = []
                for tbl in div.select("table.mod-overview > tbody"):
                    player_team = {}
                    for tr in tbl.find_all("tr"):
                        player = {}
                        player["name"] = tr.select_one("td.mod-player > div div").get_text(strip=True)
                        player["agent"] = tr.select_one("td.mod-agents img")["title"]
                        

                        i=1
                        for td in tr.select("td.mod-stat"):
                            if i==1:
                                player["rating"] = float(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==2:
                                player["acs"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==3:
                                player["kill"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==4:
                                player["death"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==5:
                                player["assist"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==4:
                                player["death"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==5:
                                player["assist"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==7:
                                player["kast"] = int(td.select_one("span.mod-both").get_text(strip=True).replace('%', '') or -1)
                            elif i==8:
                                player["adr"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==9:
                                player["hs%"] = int(td.select_one("span.mod-both").get_text(strip=True).replace('%', '') or -1)
                            elif i==10:
                                player["fk"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            elif i==11:
                                player["fd"] = int(td.select_one("span.mod-both").get_text(strip=True) or -1)
                            i = i + 1
                        player_team[player["name"]] = player
                    players.append(player_team)

                res["player"] = players



                r.append(res)
                
        return r

    def get_map_veto(self) -> list[str]:
        res = []
        short = self.get_team_short()

        for e in self.soup.select(".match-header-note"):
            map_veto_text = e.get_text(strip=True)

            for text in map_veto_text.split(";"):
                text = text.strip()
                s: list = text.split(" ")

                if len(s)==2:
                    res.append({
                        "map": s[0].strip().lower(),
                        "team": 0,
                        "action": "pick"
                    })
                elif len(s)==3:
                    team = s[0].strip()
                    if short[0]==s[0]:
                        team = 1
                    elif short[1]==s[0]:
                        team = 2
                    else:
                        team = 0

                    res.append({
                        "map": s[2].strip().lower(),
                        "team": team,
                        "action": s[1].strip().lower()
                    })
        return res

    def get_vods(self) -> list[str]:
        res = []
        for e in self.soup.select(".match-vods .match-streams-container a"):
            res.append(e.attrs["href"])
        return res

class VLR_Event():
    event_id: str
    url: str
    soup: bs4.BeautifulSoup

    def __init__(self, event_id: str, event_name: str = "") -> None:
        self.event_id = event_id
        self.url = f"https://www.vlr.gg/event/{event_id}/{event_name}"

        res = requests.get(self.url)
        res.raise_for_status()
        self.soup = bs4.BeautifulSoup(res.text, "html.parser")
    
    def get_data(self) -> dict:
        title = self.get_title()
        description= self.get_description()
        section = self.get_section()
        date = self.get_date()
        prize = self.get_prize()
        location = self.get_location()
        rosters = self.get_rosters()

        return {
            "title": title,
            "description": description,
            "section": section,
            "date": date,
            "prize": prize,
            "location": location,
            "teams": rosters
        }

    def get_title(self) -> str:
        return self.soup.select_one(".event-header .wf-title").get_text(strip=True)

    def get_description(self) -> str:
        return self.soup.select_one(".event-header .event-desc-subtitle").get_text(strip=True)

    def get_section(self) -> str:
        return self.soup.select_one(".wf-subnav a.wf-subnav-item.mod-active .wf-subnav-item-title").get_text(strip=True)

    def get_date(self) -> str:
        for e in self.soup.select(".event-desc-items .event-desc-item"):
            if e.select_one(".event-desc-item-label").get_text(strip=True) == "Dates":
                return e.select_one(".event-desc-item-value").get_text(strip=True)
    
    def get_prize(self) -> str:
        for e in self.soup.select(".event-desc-items .event-desc-item"):
            if e.select_one(".event-desc-item-label").get_text(strip=True) == "Prize pool":
                return e.select_one(".event-desc-item-value").get_text(strip=True)

    def get_location(self) -> str:
        for e in self.soup.select(".event-desc-items .event-desc-item"):
            if e.select_one(".event-desc-item-label").get_text(strip=True) == "Location":
                return e.select_one(".event-desc-item-value").get_text(strip=True)

    def get_rosters(self) -> list:
        ret: list = []

        for e in self.soup.select(".event-teams-container .wf-card.event-team"):
            team_data = {}
            team_data["title"] = e.select_one(".event-team-name").get_text(strip=True)
            team_data["players"] = []

            for f in e.select(".event-team-players .event-team-players-item"):
                team_data["players"].append(f.get_text(strip=True))

            ret.append(team_data)
        return ret

