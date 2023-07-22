import requests, bs4, datetime
from utils.tools.api import API
from utils.tools.wiki import Wiki

class Match():
    match_id: str
    url: str
    soup: bs4.BeautifulSoup

    def __init__(self, match_id: str) -> None:
        self.match_id = match_id
        self.url = f"https://www.vlr.gg/{match_id}"

        html = requests.get(self.url)
        html.raise_for_status()
        self.soup = bs4.BeautifulSoup(html.text, "html.parser")

        # team
        teams = []
        for e in self.soup.select(".match-header-link-name .wf-title-med"):
            teams.append(e.get_text(strip=True))
        self.team = (teams[0], teams[1])

        # team shortname
        teams_short = []
        sp = self.soup.find("div", {"class": "vm-stats-game", "data-game-id": "all"})
        for tbl in sp.select(".mod-overview"):
            short = tbl.select_one(".mod-player .ge-text-light").get_text(strip=True)
            teams_short.append(short)
        self.team_short = (teams_short[0], teams_short[1])

        # map count
        map_count = []
        for e in self.soup.select(".match-header-vs-score-winner, .match-header-vs-score-loser"):
            map_count.append(int(e.get_text(strip=True)))
        self.map_count = (map_count[0], map_count[1])

        # patch
        patch: str
        for e in self.soup.select_one(".match-header-date").select("div"):
            if not "moment-tz-convert" in e.attrs.get("class", []):
                patch = e.getText(strip=True).replace("Patch ", "")
                break
        self.patch = patch

        # date
        date: str
        for e in self.soup.select_one(".match-header-date").select("div"):
            if "moment-tz-convert" in e.attrs.get("class", []):
                date = e.attrs["data-utc-ts"]
                break
        self.date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        # event id
        event_id: str = self.soup.select_one("a.match-header-event").attrs["href"]
        self.event_id = event_id.split("/")[2]

        # event / series
        event_data = self.soup.select_one("a.match-header-event div")
        self.event: str = event_data.select_one(":not(.match-header-event-series)").get_text(strip=True).replace("\t", "").replace("\n", "")
        self.series: str = event_data.select_one(".match-header-event-series").get_text(strip=True).replace("\t", "").replace("\n", "")
        
        # players
        players: list = []
        div = self.soup.find("div", {"class":"vm-stats-game", "data-game-id":"all"})

        for tbl in div.select("table.mod-overview > tbody"):
            player_team = []
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
                player_team.append(player)
            players.append(player_team)

        self.player = players

        # match
        self.match = self._get_match()

        # vod
        vods = []
        for e in self.soup.select(".match-vods .match-streams-container a"):
            vods.append(e.attrs["href"])
        self.vod = vods

        # map veto
        map_veto = []

        for e in self.soup.select(".match-header-note"):
            map_veto_text = e.get_text(strip=True)

            for text in map_veto_text.split(";"):
                text = text.strip()
                s: list = text.split(" ")

                if len(s)==2:
                    map_veto.append({
                        "map": s[0].strip().lower(),
                        "team": 0,
                        "action": "pick"
                    })
                elif len(s)==3:
                    team = s[0].strip()
                    if teams_short[0]==s[0]:
                        team = 1
                    elif teams_short[1]==s[0]:
                        team = 2
                    else:
                        team = 0

                    map_veto.append({
                        "map": s[2].strip().lower(),
                        "team": team,
                        "action": s[1].strip().lower()
                    })
        self.map_veto = map_veto


    def _get_match(self) -> list[str]:
        r = []

        # Player Sort
        player_sort_list = [[], []]
        for i in range(2):
            for p in self.player[i]:
                player_sort_list[i].append(p["name"])
        
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
                duration = header_div.select_one(".map-duration").get_text(strip=True)
                if duration.count(":")==1:
                    res["duration"] = datetime.timedelta(minutes=int(duration[0]), seconds=int(duration[1]))
                elif duration.count(":")==2:
                    res["duration"] = datetime.timedelta(hours=int(duration[0]), minutes=int(duration[1]), seconds=int(duration[2]))

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
                j = 0
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
                    
                    player_team_sorted: list = []
                    for p in player_sort_list[j]:
                        try:
                            player_team_sorted.append(player_team[p])
                        except KeyError:
                            pass
                    players.append(player_team_sorted)
                    j = j + 1

                res["player"] = players



                r.append(res)
                
        return r


class Event():
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

