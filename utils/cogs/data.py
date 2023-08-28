import flet as ft
import datetime
import os
import zipfile
import subprocess
import shutil

from utils.tools.localize import Lang
from utils.tools.wiki import Wiki, WikiString
from utils.tools.gui import Gui
from utils.tools.endpoint import Endpoint
from utils.tools.fetch import Fetch
from utils.tools.json import JSON, Lua
from utils.tools.api import API

class Data():
    page: ft.Page
    wiki: Wiki
    gui: Gui
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.spray = Spray(wiki, gui, page)
    
    def main(self):
        self.content = ft.Container(self.spray.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index
            contents = [
                self.spray.main()
            ]

            try:
                self.content.content = contents[i]
            except IndexError:
                pass
            self.gui.safe_update(self.content)
            

        return ft.Row(
            [
                ft.NavigationRail(
                    selected_index=0,
                    label_type=ft.NavigationRailLabelType.ALL,
                    min_width=100,
                    min_extended_width=400,
                    destinations=[
                        ft.NavigationRailDestination(
                            icon_content=ft.Icon(ft.icons.SHOPPING_BAG_OUTLINED),
                            selected_icon_content=ft.Icon(ft.icons.SHOPPING_BAG),
                            label=Lang.value("contents.misc.store.title"),
                        ),
                        
                        ft.NavigationRailDestination(
                            icon_content=ft.Icon(ft.icons.AUDIO_FILE_OUTLINED),
                            selected_icon_content=ft.Icon(ft.icons.AUDIO_FILE),
                            label=Lang.value("contents.misc.wemconv.title"),
                        ),
                    ],
                    on_change=on_clicked
                ),
                ft.Card(
                    content=ft.Column([
                        ft.Container(
                            width=500,
                            padding=20,
                            content = self.content,
                        )],
                        horizontal_alignment=ft.MainAxisAlignment.START,
                        scroll=True
                    ),
                    expand=True
                )
            ]
        )

class Spray():
    page: ft.Page
    dictionary: dict = {}

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
    
    def main(self):
        self.make_list()
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.data.spray.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.data.spray.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),
            ]
        )

    def make_list(self):
        sprays = JSON.read("api/sprays.json")
        uuid_list = []
        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/bundles2.json")

        # data
        self.dictionary["data"] = {}
        for d in sprays:
            self.dictionary["data"][d["displayName"]["en-US"].lower()] = {
                "uuid": d["uuid"],
                "name": d["displayName"]["en-US"].lower(),
                "title": d["displayName"]["ja-JP"],
                "image": self.get_filename(d)
            }
            uuid_list.append(d["uuid"])

        l= sorted(self.dictionary["data"].items())
        self.dictionary["data"].clear()
        self.dictionary["data"].update(l)


        # category
        self.dictionary["category"] = {}

        # agent gear
        self.dictionary["category"]["agent"] = {}
        for agent in sorted(agents, key=lambda x: x["displayName"]["ja-JP"]):
            agent_uuid = agent["uuid"]
            self.dictionary["category"]["agent"][agent["displayName"]["ja-JP"]] = []

            for contract in contracts:
                if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Spray":
                                spray = API.spray_by_uuid(level["reward"]["uuid"])
                                self.dictionary["category"]["agent"][agent["displayName"]["ja-JP"]].append({
                                    "name": spray["displayName"]["en-US"],
                                    "description": "[[" + contract["displayName"]["ja-JP"] + "]]"
                                })
                                sprays = API.remove_list_from_uuid(sprays, spray["uuid"])

        # battlepass
        act: int = 1
        episode: int = 1
        self.dictionary["category"]["act"] = {}
        for season_uuid in API.get_act_list():
            if self.dictionary["category"]["act"].get("EP"+str(episode))==None:
                self.dictionary["category"]["act"]["EP"+str(episode)] = {}
            self.dictionary["category"]["act"]["EP"+str(episode)]["ACT"+str(act)] = []

            for contract in contracts:
                if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==season_uuid:

                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Spray":
                                spray = API.spray_by_uuid(level["reward"]["uuid"])
                                self.dictionary["category"]["act"]["EP"+str(episode)]["ACT"+str(act)].append({
                                    "name": spray["displayName"]["en-US"],
                                    "description": "[[" + contract["displayName"]["ja-JP"] + "]]"
                                })
                                sprays = API.remove_list_from_uuid(sprays, spray["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Spray":
                                    spray = API.spray_by_uuid(free_level["uuid"])
                                    self.dictionary["category"]["act"]["EP"+str(episode)]["ACT"+str(act)].append({
                                        "name": spray["displayName"]["en-US"],
                                        "description": "[[" + contract["displayName"]["ja-JP"] + "]] (無料報酬)"
                                    })
                                    sprays = API.remove_list_from_uuid(sprays, spray["uuid"])
            
            if act==3:
                act = 1
                episode = episode + 1
            else:
                act = act+1
        
        # eventpass
        self.dictionary["category"]["event"] = []
        for eventpass_uuid in API.get_eventpass_list():
            for contract in contracts:
                if contract["uuid"] == eventpass_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Spray":
                                spray = API.spray_by_uuid(level["reward"]["uuid"])
                                self.dictionary["category"]["event"].append({
                                    "name": spray["displayName"]["en-US"],
                                    "description": "[[" + contract["displayName"]["ja-JP"] + "]]"
                                })
                                sprays = API.remove_list_from_uuid(sprays, spray["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Spray":
                                    spray = API.spray_by_uuid(free_level["uuid"])
                                    self.dictionary["category"]["event"].append({
                                        "name": spray["displayName"]["en-US"],
                                        "description": "[[" + contract["displayName"]["ja-JP"] + "]] (無料報酬)"
                                    })
                                    sprays = API.remove_list_from_uuid(sprays, spray["uuid"])
        
        # bundle
        self.dictionary["category"]["bundle"] = []
        for bundle in sorted(bundles, key=lambda x: (x["last_seen"] is None, x["last_seen"])):
            if bundle["uuid"]=="2ed936df-4959-acc7-9aca-358d34a50619": #doodle buds
                bundle["sprays"].append({"name": "Doodle Buds // Tactifriends Spray", "uuid": "8f9caa22-4dd6-5649-1007-0bbaf7001c04"})
                bundle["sprays"].append({"name": "Doodle Buds // League of Legends Spray", "uuid": "bbdcf328-4f71-3c0c-7830-568913236d35"})
            elif bundle["uuid"]=="2116a38e-4b71-f169-0d16-ce9289af4bfa": #prime
                bundle["sprays"].append({"name": "Prime Brick Spray", "uuid": "880d5de5-4268-769d-5407-55921ad2db12"})
            
            for bundle_spray in bundle["sprays"]:
                for spray in sprays:
                    if bundle_spray["uuid"]==spray["uuid"]:
                        self.dictionary["category"]["bundle"].append(
                            {
                                "name": spray["displayName"]["ja-JP"],
                                "description": "[[" + API.get_bundle_name(bundle["uuid"]) + "]]"
                            }
                        )
                        sprays = API.remove_list_from_uuid(sprays, spray["uuid"])
        
        # prime gaming drops
        self.dictionary["category"]["prime"] = [
            {
                "name": "Clip It Spray",
                "description": "[[Prime Gaming Drops]]<br>(2020年11月)"
            },
            {
                "name": "200 IQ Spray",
                "description": "[[Prime Gaming Drops]]<br>(2021年4月)"
            },
            {
                "name": "Pity Party Spray",
                "description": "[[Prime Gaming Drops]]<br>(2021年5月)"
            },
            {
                "name": "Can't Teach That Spray",
                "description": "[[Prime Gaming Drops]]<br>(2021年7月)"
            },
            {
                "name": "Just Business Spray",
                "description": "[[Prime Gaming Drops]]<br>(2021年9月)"
            },
            {
                "name": "Flames in my Veins Spray",
                "description": "[[Prime Gaming Drops]]<br>(2021年10月)"
            },
            {
                "name": "Bruno Coin Spray",
                "description": "[[Prime Gaming Drops]]<br>(2021年12月)"
            },
            {
                "name": "Googly Moogly Spray",
                "description": "[[Prime Gaming Drops]]<br>(2022年4月)"
            },
            {
                "name": "Ego or Eco Spray",
                "description": "[[Prime Gaming Drops]]<br>(2022年7月)"
            },
            {
                "name": "Runnin' on Empty Spray",
                "description": "[[Prime Gaming Drops]]<br>(2022年9月)"
            },
            {
                "name": "Sic' Em Spray",
                "description": "[[Prime Gaming Drops]]<br>(2022年11月)"
            },
            {
                "name": "Doomscrolling Spray",
                "description": "[[Prime Gaming Drops]]<br>(2023年2月)"
            },
            {
                "name": "Claw and Order Spray",
                "description": "[[Prime Gaming Drops]]<br>(2023年5月)"
            },
            {
                "name": "Predicament Pals Spray",
                "description": "[[Prime Gaming Drops]]<br>(2023年7月)"
            },
        ]
        for d in self.dictionary["category"]["prime"]:
            for spray in sprays:
                if spray["displayName"]["en-US"]==d["name"]:
                    sprays = API.remove_list_from_uuid(sprays, spray["uuid"])

        # misc
        self.dictionary["category"]["misc"] = [
            {
                "name": "No Spray Equipped",
                "description": "スプレーを装備していない状態"
            },
            {
                "name": "VALORANT Spray",
                "description": "デフォルトのスプレー"
            },
            {
                "name": "Loose Cannon Spray",
                "description": "RiotX Arcaneのサイト上で特定のミッションをクリア<ref>{{Cite|title=限定特典「ARCANE ポロ バディー」、「暴走キャノン スプレー」が配布中、「RiotX Arcane」特設サイトのミッション完了でゲット|url=https://www.valorant4jp.com/2021/11/arcane_20.html|website=VALORANT4JP|date=2021-11-20}}</ref>"
            },
            {
                "name": "VCT 2021 Spark Spray",
                "description": "[[VCT 2021: Champions Berlin|Champions 2021]]（2021年12月1日～11日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/champions-items-and-drops-are-coming/|title=CHAMPIONSアイテムと観戦報酬が間もなく登場！|website=VALORANT Esports|quote=あなたのVALORANTアカウントをYouTube、Twitch、AfreecaTV、またはTrovoアカウントにリンクすると、Championsガンバディーやスプレーを含むゲーム内報酬を受け取れます！|date=2021-11-24}}</ref>"
            },
            {
                "name": "Accidental Renaissance Spray",
                "description": "エイプリルフール（2022年4月1日～9日の間にログイン）<ref>{{Cite|url=https://www.youtube.com/watch?v=8nbvUWiNLaI|title=GO WIDE // 「ワイドジョイ」モード 発表トレーラー - VALORANT|website=YouTube|quote=「芸術の復興 スプレー」は日本時間4月1日21時00分～4月9日15時59分まで入手可能です。|author=VALORANT // JAPAN|date=2022-04-01}}</ref>"
            },
            {
                "name": "Champions 2022 Curse Spray",
                "description": "[[VCT 2022: Champions Istanbul|Champions 2022]]の視聴報酬（2022年9月16～17日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2022/ja-jp|title=CHAMPIONS 2022期間中に試合を観戦＆プレイして、アイテムを獲得しよう|quote=Champions期間中、下記の指定時間にDropsが有効なチャンネルでVALORANTの試合を観戦すれば、報酬を獲得できます。|website=VALORANT Esports|date=2022-08-19}}</ref>"
            },
            {
                "name": "Shreddy Teddy Spray",
                "description": "[[BLAST Spike Nations 2022]]の決勝戦の視聴報酬（2022年10月16日）<ref>{{Cite|url=https://www.spikenations.gg/drops/|title=Drops|website=Spike Nations|quote=Viewers who tune into BLAST’s broadcast for the finals on the 16th of October will be eligible to earn a unique Shreddy Teddy Spray, exclusively available to viewers of this event!}}</ref>"
            },
            {
                "name": "Clutch Spray",
                "description": "[[Red Bull Home Ground 2022]]（2022年12月11日）・[[Red Bull Campus Clutch 2022]]の決勝戦（2022年12月16日）の視聴報酬"
            },
            {
                "name": "Here I Am Spray",
                "description": "エイプリルフール（2023年4月1日～8日の間にログイン）<ref>{{Cite|url=https://www.youtube.com/watch?v=F5ulYOASiAE|title=チェックメイト // 「サイファーの復讐」ゲームモードトレーラー - VALORANT|website=YouTube|quote=日本時間4月1日22時00分～4月8日21時59分までの間にログインして、限定の「俺はここだ」スプレーを手に入れましょう。 |author=VALORANT // JAPAN|date=2023-04-01}}</ref>"
            },
            {
                "name": "Gekko Diff Spray",
                "description": "[[VCT 2023: Champions Los Angeles|Champions 2023]]の視聴報酬（2023年8月17日～26日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2023/|title=CHAMPIONS 2023期間中に試合を観戦＆プレイして、アイテムを獲得しよう|website=VALORANT Esports|author=ANTON “JOKRCANTSPELL” FERRARO|date=2023-07-29}}</ref>"
            }
        ]
        for d in self.dictionary["category"]["misc"]:
            for spray in sprays:
                if spray["displayName"]["en-US"]==d["name"]:
                    sprays = API.remove_list_from_uuid(sprays, spray["uuid"])
        
        for spray in sprays:
            self.dictionary["category"]["misc"].append(
                {
                    "name": spray["displayName"]["en-US"],
                    "description": "未使用"
                }
            )



        os.makedirs("output/lists", exist_ok=True)

        JSON.save("output/lists/sprays.json", self.dictionary)
        JSON.save("output/lists/remain_sprays.json", sprays)
        with open("output/lists/sprays.lua", "w", encoding="UTF-8") as f:
            f.write("return " + Lua.to_lua(self.dictionary))
        
    def get_filename(self, data: dict) -> str:
        name = data.get("displayName", {})["en-US"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
    
        if uuid == "ecba2299-4e4a-0ca7-a194-95a4c92f3f4a": # ¯\\_(ツ)_/¯ Spray
            name = "Shrug Spray"
        elif uuid == "87c0b8c9-4b11-2e9a-95fe-ad94cf102d85": # <3 Spray
            name = "＜3 Spray"
        elif uuid == "a8765b06-4131-5be0-575a-e288cfa904a8": # Love > Hate Spray
            name = "Love ＞ Hate Spray"
        
        name = WikiString.wiki_format(name)
        return f"{name}.png"