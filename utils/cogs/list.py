import tkinter, os, datetime, math
import tkinter.simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData
from utils.api import API
from utils.wiki import Wiki

class List():
    root: tkinter.Tk
    wiki: Wiki
    force: bool

    def __init__(self, root: tkinter.Tk, wiki: Wiki, force: bool = False) -> None:
        self.root = root
        self.wiki = wiki
        self.force = force
    
    def gunbuddies(self):
        _ftype = "CORE.LIST.BUDDY"
        
        try:
            buddies: dict = JSON.read("api/buddies.json")
            contracts: dict = JSON.read("api/contracts.json")
            agents: dict = JSON.read("api/agents.json")

            uuid_list: dict = {}

            # Agent Contracts
            uuid_list["contracts"] = []

            for agent_uuid in Misc.CoreList.Agent:
                battlepass: dict

                for contract in contracts:
                    if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                        battlepass = contract
                        break
                
                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="EquippableCharmLevel":
                            buddy = ApiData.buddy_from_charmlevel_uuid(level["reward"]["uuid"])
                            uuid_list["contracts"].append({
                                "name": buddy["uuid"],
                                "title": buddy["displayName"]["ja-JP"],
                                "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                                "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                            })
                            buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])

            # Battlepass
            act: int = 1
            episode: int = 1
            uuid_list["battlepass"] = {}

            for act_uuid in Misc.CoreList.Act():
                if uuid_list["battlepass"].get("EP"+str(episode))==None:
                    uuid_list["battlepass"]["EP"+str(episode)] = {}
                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)] = []
                battlepass: dict

                for contract in contracts:
                    if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==act_uuid:
                        battlepass = contract
                        break
                

                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="EquippableCharmLevel":
                            buddy = ApiData.buddy_from_charmlevel_uuid(level["reward"]["uuid"])
                            uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)].append({
                                "name": buddy["uuid"],
                                "title": buddy["displayName"]["ja-JP"],
                                "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                                "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                            })
                            buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])

                    if chapter["freeRewards"]!=None:
                        for free_level in chapter["freeRewards"]:
                            if free_level["type"]=="EquippableCharmLevel":
                                buddy = ApiData.buddy_from_charmlevel_uuid(free_level["uuid"])
                                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)].append({
                                    "name": buddy["uuid"],
                                    "title": buddy["displayName"]["ja-JP"],
                                    "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                                buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])
                
                if act==3:
                    act = 1
                    episode = episode + 1
                else:
                    act = act+1

            # Eventpass
            uuid_list["eventpass"] = []

            for contract in contracts:
                if contract["uuid"] == "a3dd5293-4b3d-46de-a6d7-4493f0530d9b" or contract["content"]["relationType"] == "Event" or (contract["content"]["relationType"] == "Season" and contract["content"]["relationUuid"] == "0df5adb9-4dcb-6899-1306-3e9860661dd3"):
                    battlepass = contract
            
                    for chapter in battlepass["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="EquippableCharmLevel":
                                buddy = ApiData.buddy_from_charmlevel_uuid(level["reward"]["uuid"])
                                uuid_list["eventpass"].append({
                                    "name": buddy["uuid"],
                                    "title": buddy["displayName"]["ja-JP"],
                                    "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                                buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])


            # Competitive
            maxep = math.ceil(len(Misc.CoreList.Act())/3)
            uuid_list["competitive"] = {}

            for episode in range(1,maxep+1):
                uuid_list["competitive"]["EP"+str(episode)] = []

                for tier in Misc.CoreList.CompetitiveTiersName:
                    name = f"EP{episode}: {tier} Buddy"

                    for buddy in buddies:
                        if buddy["displayName"]["en-US"]==name:
                            uuid_list["competitive"]["EP"+str(episode)].append({
                                "name": buddy["uuid"],
                                "title": buddy["displayName"]["ja-JP"],
                                "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                                "description": "{{Act|"+str(episode)+"}}"
                            })
                            buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])
                            break
                    
            # Prime Gaming Drops
            buddy_list = [
                "1e909ee9-4af5-5d50-aa27-2bb596187986",
                "839c6e7d-4821-157b-fd38-71b3debc874f",
                "4bfcc79c-4352-aa06-53de-259530012e45",
                "42cb4b6a-45e3-8a83-2f52-0d90c7ca306d",
                "278e4d19-4026-02ac-263e-bca2b69df8fb",
                "46841a97-48b1-3432-5b28-5ca47df923a9",
                "8e992d1d-4e3e-627f-7e84-cc98963f304c",
                "30abc170-4cbb-bd6e-8a19-b1bbe91fa99a",
                "90b6b7eb-4960-5a26-7d49-7cbab0d7cfb2",
                "d22eff46-419a-9ebc-c60a-4892359fa2d1",
                "7516ebb5-405d-e0ff-0fd9-67b8135b7821",
                "5f5db91e-4fd5-e0f9-3944-63a93397d3ee",
                "759b4a69-4742-cdf9-4211-4c867cdcabd7",
                "2020356c-4061-7736-053d-90963f8e3caf",
                "b3066549-4b2a-f7d4-d655-3784181db732"
            ]
            uuid_list["primegaming"] = []

            for buddy_uuid in buddy_list:
                buddy = ApiData.buddy_from_uuid(buddy_uuid)
                uuid_list["primegaming"].append({
                    "name": buddy["uuid"],
                    "title": buddy["displayName"]["ja-JP"],
                    "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png"
                })
                buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])
            
            # VCT
            buddy_list = {
                "82bdb8b5-40bf-9b65-272e-4eb7dad1264e": "[[VALORANT Masters]]の優勝報酬",
                "e96e6f84-4315-409a-09bf-788e0cf13ecf": "[[VALORANT Champions]]の優勝報酬",
                "902bac6e-4674-cda0-cd3f-92b65d943fed": "[[Game Changers 2022 Championship]]の優勝報酬",
                "0556c983-462c-1f6b-1bef-b1979aa07a7f": "[[VALORANT Champions Tour 2023: LOCK//IN São Paulo]]の優勝報酬",
            }
            uuid_list["vct"] = []

            for buddy_uuid, description in buddy_list.items():
                buddy = ApiData.buddy_from_uuid(buddy_uuid)
                uuid_list["vct"].append({
                    "name": buddy["uuid"],
                    "title": buddy["displayName"]["ja-JP"],
                    "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                    "description": description
                })
                buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])

            # Misc
            buddy_list = {
                "ad508aeb-44b7-46bf-f923-959267483e78": "Riot Gamesの社員などから与えられる特別なガンバディー<ref>{{Cite|url=https://support-valorant.riotgames.com/hc/ja/articles/6708651826579-%E3%83%A9%E3%82%A4%E3%82%A2%E3%83%83%E3%83%88-%E3%82%AC%E3%83%B3%E3%83%90%E3%83%87%E3%82%A3%E3%83%BC%E3%81%AE%E5%85%A5%E6%89%8B%E6%96%B9%E6%B3%95|title=ライアット ガンバディーの入手方法|author=DullMoment|website=VALORANT Support|date=2022-07-15}}</ref>",
                "d12a80c0-44a0-0549-cc1f-eeb83f7ad248": "中東地域でのVALORANTリリース記念<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1326057002322124803|title=中東地域でのVALORANTのリリースを記念して無料のガンバディーをプレゼント カフワカップで一緒にお祝いしましょう|author=@VALORANTjp|website=Twitter|date=2020-11-10}}</ref>",
                "e4267845-4725-ff8e-6c71-ae933844565f": "{{Patch|1.14}}で[[スノーボールファイト]]をプレイする<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1343361023085064193|title=「スノーブラザーバディー」をゲットできるのは12月29日まで！期間限定モード「スノーボールファイト」をプレイして手に入れるのをお忘れなく|website=Twitter|author=@VALORANTjp|date=2020-12-28}}</ref>",
                "9e601160-4679-d2df-261b-56a398248271": "[[BLAST Spike Nations #2]]の視聴報酬（60分以上）",
                "237f36ef-40d5-410a-84be-6c896aad6fde": "RiotX Arcaneのサイト上で特定のミッションをクリア<ref>{{Cite|title=限定特典「ARCANE ポロ バディー」、「暴走キャノン スプレー」が配布中、「RiotX Arcane」特設サイトのミッション完了でゲット|url=https://www.valorant4jp.com/2021/11/arcane_20.html|website=VALORANT4JP|date=2021-11-20}}</ref>",
                "912110cb-4f40-ada7-e338-518244fff9b2": "Arcaneプレミアの視聴報酬<ref>{{Cite|url=https://www.riotgames.com/ja/news/welcome-to-riotx-arcane-ja|title=ようこそ、「RiotX Arcane」へ。|quote=11月7日はRiotアカウントをTwitchにリンクして、私たちと一緒に、またはお好きな配信者と一緒にArcaneプレミアを視聴してゲーム内アイテムをゲットしましょう。|website=Riot Games|date=2021-11-01}}</ref>",
                "e2e5ab96-4103-8473-14a7-8d8321a3ae6e": "[[VALORANT Champions 2021]]の決勝戦（2021年12月12日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/champions-items-and-drops-are-coming/|title=CHAMPIONSアイテムと観戦報酬が間もなく登場！|website=VALORANT Esports|quote=あなたのVALORANTアカウントをYouTube、Twitch、AfreecaTV、またはTrovoアカウントにリンクすると、Championsガンバディーやスプレーを含むゲーム内報酬を受け取れます！|date=2021-11-24}}</ref>",
                "ada5f921-4d81-f439-0017-0e86877a02bd": "2021年12月15日以降にログイン<ref>{{Cite|url=https://twitter.com/PlayVALORANT/status/1470785666330071045|title=‘Tis the season for giving and we’re ready to start it off right. Get your Exquisitely Wrapped Gun Buddy by logging in to your VALORANT account. It’ll take a bit for us to deliver to everyone’s inventory, but you’ll see it soon.|website=Twitter|author=@PlayVALORANT|date=2021-12-15|}}</ref>",
                "c14745d0-4958-26d9-60e6-7c863080fef1": "二要素認証を有効化する<ref>{{Cite|title=二要素認証の導入で報酬を獲得|url=https://www.riotgames.com/ja/news/get-rewarded-for-enabling-2fa-ja|website=Riot Games|quote=そして今回、二要素認証を導入していただいた方を対象に、限定のゲーム内報酬をお贈りすることとなりました。これから新たに導入される方、すでに導入済みの方のどちらも対象となります。|date=2022-10-17}}</ref>",
                "86e61d30-4f29-ef14-e880-ef89f53eff09": "2022年12月中にRiotアカウントとXboxプロフィールをリンクする<ref>{{Cite|url=https://twitter.com/riotgames/status/1600958902253789207|title=We’re coming to #XboxGamePass in 4 days! Starting today, link your Riot account and Xbox profile to prepare for #TheUnlock and for a limited time, get these extra in-game rewards across all titles. 👉 Here’s how https://riot.com/3W3R0KR|website=Twitter|author=@riotgames|date=2022-12-09}}</ref>",
                "d2b317f7-4f19-7052-cd50-33a32f210da0": "[[VALORANT Champions Tour 2023: LOCK//IN São Paulo]]の決勝戦（2023年3月4日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/watch-vct-lock-in-earn-drops|title=VCT23 LOCK//INを観戦してDROPSを獲得しよう|quote=3月4日にグランドファイナルの試合をライブ配信で観戦すると獲得できます|website=VALORANT Esports|date=2023-02-08}}</ref>"
            }
            uuid_list["misc"] = []

            for buddy_uuid, description in buddy_list.items():
                buddy = ApiData.buddy_from_uuid(buddy_uuid)
                uuid_list["misc"].append({
                    "name": buddy["uuid"],
                    "title": buddy["displayName"]["ja-JP"],
                    "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                    "description": description
                })
                buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])
            
            # bundles
            bundles: dict = JSON.read("api/dict/bundles.json")
            uuid_list["bundle"] = []

            for bundle in bundles.values():
                for item in bundle.get("items", []):
                    if item["type"]=="EquippableCharmLevel":
                        buddy = ApiData.buddy_from_charmlevel_uuid(item["uuid"])
                        uuid_list["bundle"].append({
                            "name": buddy["uuid"],
                            "title": buddy["displayName"]["ja-JP"],
                            "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png",
                            "description": "[[" + bundle["displayName"]["ja-JP"] +"]]"
                        })
                        buddies = Misc.CoreList.remove_list_from_uuid(buddies, buddy["uuid"])
            
            # other
            uuid_list["other"] = []
            for buddy in buddies:
                uuid_list["other"].append({
                    "name": buddy["uuid"],
                    "title": buddy["displayName"]["ja-JP"],
                    "file": String.wiki_format(buddy["displayName"]["en-US"]) + ".png"
                })
            
            # makelist
            def makelist(gallery: list) -> str:
                ret = "{{Gallery-begin}}\n"
                for item in gallery:
                    ret = ret + "{{Gallery|[[File:" + item["file"] + "]]|" + item["title"]
                    if item.get("description")!=None:
                        ret = ret + "||" + item["description"] + "}}"
                    else:
                        ret = ret + "}}"
                    ret = ret + "\n"
                ret = ret + "{{Gallery-end}}"
                return ret

            def maketab(gallery) -> str:
                if type(gallery)==type([]):
                    return makelist(gallery)
                elif type(gallery)==type({}):
                    ret = "{{Tab|bgnone=yes\n"
                    i: int = 1
                    for key, value in gallery.items():
                        ret = ret + f"|tab{i} = {key} |panel{i} = \n{maketab(value)}\n"
                        i = i + 1
                    ret = ret + "}}"
                    return ret
            
            os.makedirs(f"output/buddies/list", exist_ok=True)
            for name, category in uuid_list.items():
                txt = maketab(category)
                with open(f"output/buddies/list/{name}.txt", "w", encoding="utf-8") as fp:
                    fp.write(txt)
        

        except Exception as e:
            messagebox.showerror("ガンバディー (リスト)", "ガンバディー の作成に失敗しました。")
            Log.exception(e, "ガンバディーの作成に失敗しました。", _ftype)

    def sprays(self):
        _ftype = "CORE.LIST.SPRAY"
        
        try:
            sprays: dict = JSON.read("api/sprays.json")
            contracts: dict = JSON.read("api/contracts.json")

            uuid_list: dict = {}

            # Agent Contracts
            uuid_list["contracts"] = {}

            for agent_uuid in Misc.CoreList.Agent:
                battlepass: dict
                agent: dict = {}

                for contract in contracts:
                    if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                        battlepass = contract
                        agent = ApiData.agent_from_uuid(agent_uuid)
                        uuid_list["contracts"][agent["displayName"]["ja-JP"]] = []
                        break
                
                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="Spray":
                            spray = ApiData.spray_from_uuid(level["reward"]["uuid"])
                            uuid_list["contracts"][agent["displayName"]["ja-JP"]].append({
                                "name": spray["uuid"],
                                "title": spray["displayName"]["ja-JP"],
                                "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png",
                                "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                            })
                            sprays = Misc.CoreList.remove_list_from_uuid(sprays, spray["uuid"])

            # Battlepass
            act: int = 1
            episode: int = 1
            uuid_list["battlepass"] = {}

            for act_uuid in Misc.CoreList.Act():
                if uuid_list["battlepass"].get("EP"+str(episode))==None:
                    uuid_list["battlepass"]["EP"+str(episode)] = {}
                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)] = []
                battlepass: dict

                for contract in contracts:
                    if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==act_uuid:
                        battlepass = contract
                        break
                

                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="Spray":
                            spray = ApiData.spray_from_uuid(level["reward"]["uuid"])
                            uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)].append({
                                "name": spray["uuid"],
                                "title": spray["displayName"]["ja-JP"],
                                "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png",
                                "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                            })
                            sprays = Misc.CoreList.remove_list_from_uuid(sprays, spray["uuid"])

                    if chapter["freeRewards"]!=None:
                        for free_level in chapter["freeRewards"]:
                            if free_level["type"]=="Spray":
                                spray = ApiData.spray_from_uuid(free_level["uuid"])
                                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)].append({
                                    "name": spray["uuid"],
                                    "title": spray["displayName"]["ja-JP"],
                                    "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png",
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                                sprays = Misc.CoreList.remove_list_from_uuid(sprays, spray["uuid"])
                
                if act==3:
                    act = 1
                    episode = episode + 1
                else:
                    act = act+1

            # Eventpass
            uuid_list["eventpass"] = []

            for contract in contracts:
                if contract["uuid"] == "a3dd5293-4b3d-46de-a6d7-4493f0530d9b" or contract["content"]["relationType"] == "Event" or (contract["content"]["relationType"] == "Season" and contract["content"]["relationUuid"] == "0df5adb9-4dcb-6899-1306-3e9860661dd3"):
                    battlepass = contract
            
                    for chapter in battlepass["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Spray":
                                spray = ApiData.spray_from_uuid(level["reward"]["uuid"])
                                uuid_list["eventpass"].append({
                                    "name": spray["uuid"],
                                    "title": spray["displayName"]["ja-JP"],
                                    "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png",
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                                sprays = Misc.CoreList.remove_list_from_uuid(sprays, spray["uuid"])

            # Prime Gaming Drops
            spray_list = [
                "180a93cb-4ba4-db87-b357-b9b104373a74",
                "7da0141a-4f39-33c9-8e0b-a8b44bc59a36",
                "2d9be381-4686-b392-310e-8bb2a6707f7e",
                "48601754-442d-98cb-2109-3fb2075500ec",
                "40cc1645-43f4-4db3-ebb2-fdb46f8e9bf3",
                "f677065c-449d-dd91-78ef-6fa7d95ded8d",
                "e8a8c717-4845-3c69-9c16-d8a78153c51d",
                "85637987-4961-177a-28f0-f3acf8facb6a",
                "5a328cd4-4cb5-4e64-60c2-6487281390ff",
                "3085ca2f-4e7a-25a5-909d-33940b0148e2",
                "166a3fb6-492c-9437-417d-b8852128f73c",
                "f3c383f4-41c7-d0fb-190b-ed8b974e043e"
            ]
            uuid_list["primegaming"] = []

            for spray_uuid in spray_list:
                spray = ApiData.spray_from_uuid(spray_uuid)
                uuid_list["primegaming"].append({
                    "name": spray["uuid"],
                    "title": spray["displayName"]["ja-JP"],
                    "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png"
                })
                sprays = Misc.CoreList.remove_list_from_uuid(sprays, spray["uuid"])
            
            # Misc
            spray_list = {
                "0a6db78c-48b9-a32d-c47a-82be597584c1": "デフォルトのスプレー",
                "47575563-4d43-96fb-1586-849d35c7ddd5": "RiotX Arcaneのサイト上で特定のミッションをクリア<ref>{{Cite|title=限定特典「ARCANE ポロ バディー」、「暴走キャノン スプレー」が配布中、「RiotX Arcane」特設サイトのミッション完了でゲット|url=https://www.valorant4jp.com/2021/11/arcane_20.html|website=VALORANT4JP|date=2021-11-20}}</ref>",
                "f9bcf120-42b6-6986-2acd-6aa87bab4089": "[[VALORANT Champions 2021]]（2021年12月1日～11日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/champions-items-and-drops-are-coming/|title=CHAMPIONSアイテムと観戦報酬が間もなく登場！|website=VALORANT Esports|quote=あなたのVALORANTアカウントをYouTube、Twitch、AfreecaTV、またはTrovoアカウントにリンクすると、Championsガンバディーやスプレーを含むゲーム内報酬を受け取れます！|date=2021-11-24}}</ref>",
                "be8eeab6-43eb-d0b7-7b38-f6bb25ef7547": "エイプリルフール（2022年4月1日～9日の間にログイン）<ref>{{Cite|url=https://www.youtube.com/watch?v=8nbvUWiNLaI|title=GO WIDE // 「ワイドジョイ」モード 発表トレーラー - VALORANT|website=YouTube|quote=「芸術の復興 スプレー」は日本時間4月1日21時00分～4月9日15時59分まで入手可能です。|author=VALORANT // JAPAN|date=2022-04-01}}</ref>",
                "a7b00f01-49ee-c0c2-a910-4d9ae605dbe1": "[[VALORANT Champions 2022]]の視聴報酬（2022年9月16～17日）", 
                "6aff01b3-443c-d98c-820e-05852efc075f": "[[BLAST Spike Nations 2022]]の決勝戦の視聴報酬（60分以上）",
                "890c4f6d-4794-3d88-617b-1b906c7a8ea6": "[[Red Bull Home Ground]]（2022年12月11日）・[[Red Bull Campus Clutch 2022]]の決勝戦（2022年12月16日）の視聴報酬",
                "32df08b6-4d6e-d642-b57c-fc915063418b": "エイプリルフール（2023年4月1日～8日の間にログイン）<ref>{{Cite|url=https://www.youtube.com/watch?v=F5ulYOASiAE|title=チェックメイト // 「サイファーの復讐」ゲームモードトレーラー - VALORANT|website=YouTube|quote=日本時間4月1日22時00分～4月8日21時59分までの間にログインして、限定の「俺はここだ」スプレーを手に入れましょう。 |author=VALORANT // JAPAN|date=2023-04-01}}</ref>",
            }
            uuid_list["misc"] = []

            for spray_uuid, description in spray_list.items():
                spray = ApiData.spray_from_uuid(spray_uuid)
                uuid_list["misc"].append({
                    "name": spray["uuid"],
                    "title": spray["displayName"]["ja-JP"],
                    "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png",
                    "description": description
                })
                sprays = Misc.CoreList.remove_list_from_uuid(sprays, spray["uuid"])
            
            # bundles
            bundles: dict = JSON.read("api/dict/bundles.json")
            uuid_list["bundle"] = []

            for bundle in bundles.values():
                for item in bundle.get("items", []):
                    if item["type"]=="Spray":
                        spray = ApiData.spray_from_uuid(item["uuid"])
                        uuid_list["bundle"].append({
                            "name": spray["uuid"],
                            "title": spray["displayName"]["ja-JP"],
                            "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png",
                            "description": "[[" + bundle["displayName"]["ja-JP"] +"]]"
                        })
                        sprays = Misc.CoreList.remove_list_from_uuid(sprays, spray["uuid"])
            
            # other
            uuid_list["other"] = []
            for spray in sprays:
                uuid_list["other"].append({
                    "name": spray["uuid"],
                    "title": spray["displayName"]["ja-JP"],
                    "file": String.wiki_format(spray["displayName"]["en-US"]) + ".png"
                })
            
            # makelist
            def makelist(gallery: list) -> str:
                ret = "{{Gallery-begin}}\n"
                for item in gallery:
                    ret = ret + "{{Gallery|[[File:" + item["file"] + "]]|" + item["title"]
                    if item.get("description")!=None:
                        ret = ret + "||" + item["description"] + "}}"
                    else:
                        ret = ret + "}}"
                    ret = ret + "\n"
                ret = ret + "{{Gallery-end}}"
                return ret

            def maketab(gallery) -> str:
                if type(gallery)==type([]):
                    return makelist(gallery)
                elif type(gallery)==type({}):
                    ret = "{{Tab|bgnone=yes\n"
                    i: int = 1
                    for key, value in gallery.items():
                        ret = ret + f"|tab{i} = {key} |panel{i} = \n{maketab(value)}\n"
                        i = i + 1
                    ret = ret + "}}"
                    return ret
            
            os.makedirs(f"output/sprays/list", exist_ok=True)
            for name, category in uuid_list.items():
                txt = maketab(category)
                with open(f"output/sprays/list/{name}.txt", "w", encoding="utf-8") as fp:
                    fp.write(txt)

        except Exception as e:
            messagebox.showerror("スプレー (リスト)", "スプレー の作成に失敗しました。")
            Log.exception(e, "スプレーの作成に失敗しました。", _ftype)

    def playercards(self):
        _ftype = "CORE.LIST.CARD"
        
        try:
            playercards: dict = JSON.read("api/playercards.json")
            contracts: dict = JSON.read("api/contracts.json")
            cardtype = {"カード": "", "バナー" : " wide", "アイコン" : " icon"}


            uuid_list: dict = {}

            # Agent Contracts
            uuid_list["contracts"] = {}

            for agent_uuid in Misc.CoreList.Agent:
                battlepass: dict
                agent: dict = {}

                for contract in contracts:
                    if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                        battlepass = contract
                        agent = ApiData.agent_from_uuid(agent_uuid)
                        uuid_list["contracts"][agent["displayName"]["ja-JP"]] = {"カード": [], "バナー": [], "アイコン": []}
                        break
                
                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="PlayerCard":
                            playercard = ApiData.playercard_from_uuid(level["reward"]["uuid"])
                            for name,tp in cardtype.items():
                                uuid_list["contracts"][agent["displayName"]["ja-JP"]][name].append({
                                    "name": playercard["uuid"],
                                    "title": playercard["displayName"]["ja-JP"],
                                    "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp +".png",
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                            playercards = Misc.CoreList.remove_list_from_uuid(playercards, playercard["uuid"])

            # Battlepass
            act: int = 1
            episode: int = 1
            uuid_list["battlepass"] = {}

            for act_uuid in Misc.CoreList.Act():
                if uuid_list["battlepass"].get("EP"+str(episode))==None:
                    uuid_list["battlepass"]["EP"+str(episode)] = {}
                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)] = {"カード": [], "バナー": [], "アイコン": []}
                battlepass: dict

                for contract in contracts:
                    if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==act_uuid:
                        battlepass = contract
                        break
                

                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="PlayerCard":
                            playercard = ApiData.playercard_from_uuid(level["reward"]["uuid"])
                            for name,tp in cardtype.items():
                                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)][name].append({
                                    "name": playercard["uuid"],
                                    "title": playercard["displayName"]["ja-JP"],
                                    "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp + ".png",
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                            playercards = Misc.CoreList.remove_list_from_uuid(playercards, playercard["uuid"])

                    if chapter["freeRewards"]!=None:
                        for free_level in chapter["freeRewards"]:
                            if free_level["type"]=="PlayerCard":
                                playercard = ApiData.playercard_from_uuid(free_level["uuid"])
                                for name,tp in cardtype.items():
                                    uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)][name].append({
                                        "name": playercard["uuid"],
                                        "title": playercard["displayName"]["ja-JP"],
                                        "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp + ".png",
                                        "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                    })
                                playercards = Misc.CoreList.remove_list_from_uuid(playercards, playercard["uuid"])
                
                if act==3:
                    act = 1
                    episode = episode + 1
                else:
                    act = act+1

            # Eventpass
            uuid_list["eventpass"] = {"カード": [], "バナー": [], "アイコン": []}

            for contract in contracts:
                if contract["uuid"] == "a3dd5293-4b3d-46de-a6d7-4493f0530d9b" or contract["content"]["relationType"] == "Event" or (contract["content"]["relationType"] == "Season" and contract["content"]["relationUuid"] == "0df5adb9-4dcb-6899-1306-3e9860661dd3"):
                    battlepass = contract
            
                    for chapter in battlepass["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="PlayerCard":
                                playercard = ApiData.playercard_from_uuid(level["reward"]["uuid"])
                                for name,tp in cardtype.items():
                                    uuid_list["eventpass"][name].append({
                                        "name": playercard["uuid"],
                                        "title": playercard["displayName"]["ja-JP"],
                                        "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp + ".png",
                                        "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                    })
                                playercards = Misc.CoreList.remove_list_from_uuid(playercards, playercard["uuid"])

            # Prime Gaming Drops
            playercard_list = [
                "8453f8ef-4c0b-46e2-8768-3e9e45c67a2c",
                "1ec054a0-4184-8802-57fb-0ab81599befd",
                "584b90b0-4bdc-e9e4-a13f-9eaff115b624",
                "a26b6480-4bc4-51df-fe97-4680f30786d5",
                "33910cd9-4ac5-a0e1-8e79-3ca6916af3ef"
            ]
            uuid_list["primegaming"] = {"カード": [], "バナー": [], "アイコン": []}

            for playercard_uuid in playercard_list:
                playercard = ApiData.playercard_from_uuid(playercard_uuid)
                for name,tp in cardtype.items():
                    uuid_list["primegaming"][name].append({
                        "name": playercard["uuid"],
                        "title": playercard["displayName"]["ja-JP"],
                        "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp + ".png",
                        "description": "[[Prime Gaming Drops]]"
                    })
                playercards = Misc.CoreList.remove_list_from_uuid(playercards, playercard["uuid"])
            
            # Misc
            playercard_list = {
                "9fb348bc-41a0-91ad-8a3e-818035c4e561": "デフォルトのプレイヤーカード",
                "e6529e9c-4a2b-c31c-7252-e185a8ce4a04": "クローズドベータへのアクセス権を入手したプレイヤーに与えられた（2020年6月2日）<ref name=\"Beta Watch\">{{Cite|url=https://playvalorant.com/ja-jp/news/announcements/valorant-closed-beta-ends-may-28/|title=VALORANTのクローズドベータが5月29日（日本時間）に終了|website=VALORANT|quote=獲得権利があったにもかかわらずクローズドベータのアクセス権を受け取り損ねてしまった方には、限定のTwitch/VALORANTプレイヤーカードをお贈りします。VALORANTが正式リリースされる6月2日に、インベントリーから受け取りが可能になります。|author=CHRIS “PWYFF” TOM|date=2020-05-23}}</ref>",
                "e17c2e94-44fb-9486-8497-9dab8b942b3d": "[[AfreecaTV Asia Showdown]]の視聴報酬（60分以上）<ref name=\"Showdown Watch\">{{Cite|url=https://playvalorant.com/ko-kr/news/esports/asia-valorant-showdown-announcement/|title=‘아시아 발로란트 쇼다운’ 개막 안내|website=VALORANT|quote=아프리카TV에서 AVS를 시청하시는 분들께 특별한 플레이어 카드를 선물해 드립니다. 보상을 받는 방법은 아래와 같습니다.|date=2020-09-15}}</ref>",
                "bb5cedcd-4ed9-ee2e-f129-48bf60a8e540": "[[DUALITY]]の公開記念で48時間の限定配布がなされたが、コード交換サイトの接続不具合により2021年6月8日に存在する全アカウントに配布された<ref name=\"Duality\">{{Cite|url=https://twitter.com/PlayVALORANT/status/1402037655307702274|title=Due to the issues with our code redemption process, we're granting all players the Duality player card! You should see the card appear in your inventory soon. ICYMI, take a look at the Duality cinematic and dive deeper into the lore of VALORANT:|author=@PlayVALORANT|website=Twitter|date=2021-06-08}}</ref>",
                "bab9caaa-4913-2704-833e-8c89e2128eb9": "2021年6月10日に存在するアカウントに与えられた<ref name=\"EP 1 // IGNITION\">{{Cite|url=https://twitter.com/VALORANTjp/status/1402762436730572803|title=VALORANTの1周年を記念して、プレイヤーカード「EP 1 // IGNITION」を皆さんにプレゼント🎉 ゲーム内のインベントリをチェックしてみてください。|website=Twitter|author=@VALORANTjp|date=2021-06-10}}</ref>",
                "f67a7c8f-4d3f-b76f-2921-478a4da44109": "2021年11月24日に存在するアカウントに与えられた（[[VALORANT Champions 2021]]開催記念）<ref name=\"Art of Greatness // Champions Card\">{{Cite|url=https://valorantesports.com/news/champions-items-and-drops-are-coming/|title=CHAMPIONSアイテムと観戦報酬が間もなく登場！|quote=初のChampionsイベントを記念して、VALORANTの全アクティブアカウントに対し、Champions 2021プレイヤーカードが贈られます。|website=VALORANT Esports|author=RILEY YURK|date=2021-11-24}}</ref>",
                "68b0c8c2-4158-7b21-658d-b4ae86f137ce": "2022年7月14日以降にログイン<ref name=\"Alpha Threat\">{{Cite|url=https://twitter.com/VALORANTjp/status/1547234407991222272|title=アルファの脅威が迫っている。ログインして、コミックの表紙がテーマのプレイヤーカードを入手しよう。なお、このカードはオメガアースの厚意により無料です。|website=Twitter|author=@VALORANTjp|date=2022-07-14}}</ref>",
                "9e9c4c4a-4d53-6c37-4e48-85b771b9dd4e": "2022年8月12日～20日にログイン<ref name=\"War Dawgs\">{{Cite|url=https://twitter.com/VALORANTjp/status/1557834240896614400|title=もっとコミックブックのアイテムが欲しい！そんなあなたに。日本時間8月12日6時00分～8月20日6時00分までの間にログインすると、「戦友たち」プレイヤーカードが無料で手に入ります。|website=Twitter|author=@VALORANTjp|date=2022-08-12}}</ref>",
                "c87737f8-44bc-1b71-8424-c18d9cd6336a": "[[VALORANT Champions 2022]]の決勝（2022年9月18日）の視聴報酬<ref name=\"Champions 2022 Hero\">{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2022/ja-jp|title=CHAMPIONS 2022期間中に試合を観戦＆プレイして、アイテムを獲得しよう|quote=Champions期間中、下記の指定時間にDropsが有効なチャンネルでVALORANTの試合を観戦すれば、報酬を獲得できます。|website=VALORANT Esports|date=2022-08-19}}</ref>",
                "6a578461-430d-e0a9-d67e-4c967e0bdf1a": "[[Game Changers 2022 Championship]]の決勝（2022年11月21日）の視聴報酬<ref name=\"2022 Game Changers Championship\">{{Cite|url=https://valorantesports.com/news/valorant-game-changers-championship-everything-you-need-to-know/ja-jp|title=VALORANT GAME CHANGERS CHAMPIONSHIP ：知っておくべきすべて|quote=日本時間11月21日にグランドファイナルのライブ配信を視聴すると「2022 Game Changers Championship カード」を獲得可能。|website=VALORANT Esports|author=JEN NEALE|date=2022-11-08}}</ref>",
                "cb7157ed-4fc7-a5c9-714b-1786ca3949f1": "[[Riot Games ONE]]の来場者特典<ref name=\"Versus // Yoru + Phoenix\">{{Cite|url=https://twitter.com/RiotGamesJapan/status/1595258348101931008|title=🎁来場者特典・全員 プレイヤーカード「VERSUS // ヨル + フェニックス」 ONE限定タイトル「ONE // 2022」・抽選（一日1,000名様） Riot Games ONE限定VALORANT オリジナルキーリング|website=Twitter|author=@RiotGamesJapan|date=2022-11-23}}</ref>",
                "23a03943-4c16-0de4-0fe0-b9bcba24a26a": "[[Premier]] オープンベータで1試合参加する",
                "3f77186a-40a9-7abc-9ac6-5a988d279dad": "[[Premier]] オープンベータのプレイオフで勝利する",
                "0c196ea1-48ac-97eb-5362-c884937c016f": "[[VCT 2023: Masters Tokyo]]の決勝戦の視聴報酬（6月25日）<ref name=\"vct 2023 masters tokyo\">{{Cite|url=https://valorantesports.com/news/watch-vct-masters-earn-drops|title=VCT MASTERSを観戦してDROPSを獲得しよう|date=2023-06-08|author=ANTON “JOKRCANTSPELL” FERRARO|website=VALORANT Esports}}</ref>",
                "bcf9cff4-4163-a536-458d-22b8904876ad": "未実装",
                "01aa3a02-4ab1-0739-83fd-f3b37eba01db": "未実装",
            }
            uuid_list["misc"] = {"カード": [], "バナー": [], "アイコン": []}

            for playercard_uuid, description in playercard_list.items():
                playercard = ApiData.playercard_from_uuid(playercard_uuid)
                for name,tp in cardtype.items():
                    uuid_list["misc"][name].append({
                        "name": playercard["uuid"],
                        "title": playercard["displayName"]["ja-JP"],
                        "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp + ".png",
                        "description": description
                    })
                playercards = Misc.CoreList.remove_list_from_uuid(playercards, playercard["uuid"])
            
            # bundles
            bundles: dict = JSON.read("api/dict/bundles.json")
            uuid_list["bundle"] = {"カード": [], "バナー": [], "アイコン": []}

            for bundle in bundles.values():
                for item in bundle.get("items", []):
                    if item["type"]=="PlayerCard":
                        playercard = ApiData.playercard_from_uuid(item["uuid"])
                        for name,tp in cardtype.items():
                            uuid_list["bundle"][name].append({
                                "name": playercard["uuid"],
                                "title": playercard["displayName"]["ja-JP"],
                                "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp + ".png",
                                "description": "[[" + bundle["displayName"]["ja-JP"] +"]]"
                            })
                        playercards = Misc.CoreList.remove_list_from_uuid(playercards, playercard["uuid"])
            
            # other
            uuid_list["other"] = {"カード": [], "バナー": [], "アイコン": []}
            for playercard in playercards:
                for name,tp in cardtype.items():
                    uuid_list["other"][name].append({
                        "name": playercard["uuid"],
                        "title": playercard["displayName"]["ja-JP"],
                        "file": String.wiki_format(playercard["displayName"]["en-US"]) + tp + ".png"
                    })
            
            # makelist
            def makelist(gallery: list) -> str:
                ret = "{{Gallery-begin}}\n"
                for item in gallery:
                    ret = ret + "{{Gallery|[[File:" + item["file"] + "]]|" + item["title"]
                    if item.get("description")!=None:
                        ret = ret + "||" + item["description"] + "}}"
                    else:
                        ret = ret + "}}"
                    ret = ret + "\n"
                ret = ret + "{{Gallery-end}}"
                return ret

            def maketab(gallery) -> str:
                if type(gallery)==type([]):
                    return makelist(gallery)
                elif type(gallery)==type({}):
                    ret = "{{Tab|bgnone=yes\n"
                    i: int = 1
                    for key, value in gallery.items():
                        ret = ret + f"|tab{i} = {key} |panel{i} = \n{maketab(value)}\n"
                        i = i + 1
                    ret = ret + "}}"
                    return ret
            
            os.makedirs(f"output/playercards/list", exist_ok=True)
            for name, category in uuid_list.items():
                txt = maketab(category)
                with open(f"output/playercards/list/{name}.txt", "w", encoding="utf-8") as fp:
                    fp.write(txt)

        except Exception as e:
            messagebox.showerror("プレイヤーカード (リスト)", "プレイヤーカード の作成に失敗しました。")
            Log.exception(e, "プレイヤーカードの作成に失敗しました。", _ftype)

    def playertitles(self):
        _ftype = "CORE.LIST.TITLE"
        
        try:
            playertitles: dict = JSON.read("api/playertitles.json")
            contracts: dict = JSON.read("api/contracts.json")

            uuid_list: dict = {}

            # Agent Contracts
            uuid_list["contracts"] = {}

            for agent_uuid in Misc.CoreList.Agent:
                battlepass: dict
                agent: dict = {}

                for contract in contracts:
                    if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                        battlepass = contract
                        agent = ApiData.agent_from_uuid(agent_uuid)
                        uuid_list["contracts"][agent["displayName"]["ja-JP"]] = []
                        break
                
                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="Title":
                            playertitle = ApiData.playertitle_from_uuid(level["reward"]["uuid"])
                            uuid_list["contracts"][agent["displayName"]["ja-JP"]].append({
                                "name": playertitle["uuid"],
                                "title": playertitle["displayName"]["ja-JP"],
                                "file": playertitle["titleText"]["ja-JP"],
                                "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                            })
                            playertitles = Misc.CoreList.remove_list_from_uuid(playertitles, playertitle["uuid"])

            # Battlepass
            act: int = 1
            episode: int = 1
            uuid_list["battlepass"] = {}

            for act_uuid in Misc.CoreList.Act():
                if uuid_list["battlepass"].get("EP"+str(episode))==None:
                    uuid_list["battlepass"]["EP"+str(episode)] = {}
                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)] = []
                battlepass: dict

                for contract in contracts:
                    if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==act_uuid:
                        battlepass = contract
                        break
                

                for chapter in battlepass["content"]["chapters"]:
                    for level in chapter["levels"]:
                        if level["reward"]["type"]=="Title":
                            playertitle = ApiData.playertitle_from_uuid(level["reward"]["uuid"])
                            uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)].append({
                                "name": playertitle["uuid"],
                                "title": playertitle["displayName"]["ja-JP"],
                                "file": playertitle["titleText"]["ja-JP"],
                                "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                            })
                            playertitles = Misc.CoreList.remove_list_from_uuid(playertitles, playertitle["uuid"])

                    if chapter["freeRewards"]!=None:
                        for free_level in chapter["freeRewards"]:
                            if free_level["type"]=="Title":
                                playertitle = ApiData.playertitle_from_uuid(free_level["uuid"])
                                uuid_list["battlepass"]["EP"+str(episode)]["ACT"+str(act)].append({
                                    "name": playertitle["uuid"],
                                    "title": playertitle["displayName"]["ja-JP"],
                                    "file": playertitle["titleText"]["ja-JP"],
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                                playertitles = Misc.CoreList.remove_list_from_uuid(playertitles, playertitle["uuid"])
                
                if act==3:
                    act = 1
                    episode = episode + 1
                else:
                    act = act+1

            # Eventpass
            uuid_list["eventpass"] = []

            for contract in contracts:
                if contract["uuid"] == "a3dd5293-4b3d-46de-a6d7-4493f0530d9b" or contract["content"]["relationType"] == "Event" or (contract["content"]["relationType"] == "Season" and contract["content"]["relationUuid"] == "0df5adb9-4dcb-6899-1306-3e9860661dd3"):
                    battlepass = contract
            
                    for chapter in battlepass["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Title":
                                playertitle = ApiData.playertitle_from_uuid(level["reward"]["uuid"])
                                uuid_list["eventpass"].append({
                                    "name": playertitle["uuid"],
                                    "title": playertitle["displayName"]["ja-JP"],
                                    "file": playertitle["titleText"]["ja-JP"],
                                    "description": "[["+battlepass["displayName"]["ja-JP"]+"]]"
                                })
                                playertitles = Misc.CoreList.remove_list_from_uuid(playertitles, playertitle["uuid"])
            
            # VCT
            playertitle_list = {
                "f0751060-4d86-39e8-b881-469f52058b3f": "[[VCT 2021 Stage 1: Masters]]に優勝（{{Hlist|[[Acend]]|[[Australs]]|[[Crazy Raccoon]]|[[FUT Esports]]|[[Gambit Esports]]|[[LDM Esports]]|[[Sentinels]]|[[Team Vikings]]|[[Vision Strikers]]|[[X10 Esports]]}}）",
                "cd19dad9-4975-7e7d-c511-c6a851589c15": "[[VCT 2021 Stage 2: Masters Reykjavík]]に優勝（[[Sentinels]]）",
                "00031857-43a9-9545-4e05-58ad0a62b79d": "[[VCT 2021 Stage 3: Masters Berlin]]に優勝（[[Gambit Esports]]）",
                "1ba98f24-4989-8778-f8a6-b7af353a1625": "[[VALORANT Champions 2021]]に優勝（[[Acend]]）",
                "d9c1a80f-4531-8c05-9841-4aafd417df8c": "[[VCT 2022 Stage 1: Masters Reykjavík]]に優勝（[[OpTic Gaming]]）",
                "75aaadc3-427a-e194-e8d0-fd8b76b4540f": "[[VCT 2022 Stage 2: Masters Copenhagen]]に優勝（[[FunPlus Phoenix]]）",
                "a6d9e243-4046-b025-358e-0087b4b7fcf3": "[[VALORANT Champions 2022]]に優勝（[[LOUD]]）",
                "2c4634dd-40bd-052e-bf3c-92a7aca4f084": "[[Game Changers 2022 Championship]]に優勝（[[G2 Gozen]]）",
                "ce6f4f24-402c-d24d-c28c-4db1aa89dc9b": "[[VCT 2023: LOCK//IN São Paulo]]に優勝（[[Fnatic]]）",
                "cc33f13b-4b66-56da-f80a-e9be7271b163": "[[VCT 2023: Masters Tokyo]]に優勝（[[Fnatic]]）",
            }
            uuid_list["vct"] = []

            for playertitle_uuid, description in playertitle_list.items():
                playertitle = ApiData.playertitle_from_uuid(playertitle_uuid)
                uuid_list["vct"].append({
                    "name": playertitle["uuid"],
                    "title": playertitle["displayName"]["ja-JP"],
                    "file": playertitle["titleText"]["ja-JP"],
                    "description": description
                })
                playertitles = Misc.CoreList.remove_list_from_uuid(playertitles, playertitle["uuid"])

            # Misc
            playertitle_list = {
                "f802662f-7a82-43d9-a626-335d65df08c5": "特定のコードを入力で入手（ベトナムでのリリース記念）",
                "c70f542b-4880-c65f-485e-ec8ffd055243": "特定のコードを入力で入手（2021プライド）<ref name=\"2021 Pride\">{{Cite|url=https://playvalorant.com/ja-jp/news/announcements/show-your-pride-in-valorant/|title=VALORANTでプライドを示そう|website=VALORANT|author=JEFF LANDA|date=2021-06-04}}</ref>",
                "f3bf3c15-4e3b-6e58-64a3-8f9995f39370": "特定のコードを入力で入手（2021プライド）<ref name=\"2021 Pride\"/>",
                "6966d46b-4fd1-3287-fd00-a790c9e7a3d8": "[[VALORANT Champions 2022]]の視聴報酬（2022年8月31日～9月13日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2022/ja-jp|title=CHAMPIONS 2022期間中に試合を観戦＆プレイして、アイテムを獲得しよう|website=VALORANT Esports|quote=Champions期間中、下記の指定時間にDropsが有効なチャンネルでVALORANTの試合を観戦すれば、報酬を獲得できます。|date=2022-08-19}}</ref>",
                "a7d5ae34-4907-072c-13f9-67af86ec737c": "[[Game Changers 2022 Championship]]の視聴報酬（2022年11月15日～20日）<ref>{{Cite|url=https://valorantesports.com/news/valorant-game-changers-championship-everything-you-need-to-know/ja-jp|title=VALORANT GAME CHANGERS CHAMPIONSHIP ：知っておくべきすべて|quote=日本時間11月15日～20日に試合のライブ配信を視聴すると「Game Changer タイトル」を獲得可能。|website=VALORANT Esports|author=JEN NEALE|date=2022-11-08}}</ref>",
                "d11e42f8-45e9-7d71-720b-8c9c54c3b808": "[[Game Changers]]に参加した選手やその他の関係者に与えられる",
                "08ac32fb-450a-34b8-4aef-d88e50ebd3cb": "[[Red Bull Home Ground]]（2022年12月10日）・[[Red Bull Campus Clutch 2022]]の決勝戦（2022年12月15日）の視聴報酬",
                "39a0f753-4a86-9a32-5e1d-7687b13f6e7e": "[[Riot Games ONE]]の来場者特典<ref>{{Cite|url=https://twitter.com/RiotGamesJapan/status/1595258348101931008|title=🎁来場者特典・全員 プレイヤーカード「VERSUS // ヨル + フェニックス」 ONE限定タイトル「ONE // 2022」・抽選（一日1,000名様） Riot Games ONE限定VALORANT オリジナルキーリング|website=Twitter|author=@RiotGamesJapan|date=2022-11-23}}</ref>",
                "dd9b86b1-4661-1c98-65ac-c09b70a88e74": "[[VCT 2023: LOCK//IN São Paulo]]の視聴報酬（2023年2月14日～3月4日）<ref>{{Cite|url=https://valorantesports.com/news/watch-vct-lock-in-earn-drops|title=VCT23 LOCK//INを観戦してDROPSを獲得しよう|quote=2月14日～3月4日に試合をライブ配信で観戦すると獲得できます|website=VALORANT Esports|date=2023-02-08}}</ref>",
                "302f332d-4a9a-1f2c-9331-779b338fdcc7": "[[Premier]] オープンベータで1試合参加する",
                "c3ea6ac6-4dad-98d4-99a3-f7813edbc431": "[[Premier]] オープンベータのプレイオフで勝利する",
                "af85e868-4c20-2e15-7b2e-51b6721ed93e": "[[VCT 2023: Masters Tokyo]]の視聴報酬（2023年6月11日～6月25日）<ref>{{Cite|url=https://valorantesports.com/news/watch-vct-masters-earn-drops|title=VCT MASTERSを観戦してDROPSを獲得しよう|date=2023-06-08|author=ANTON “JOKRCANTSPELL” FERRARO|website=VALORANT Esports}}</ref>",
                "e8c04a61-49a8-8d0a-501c-13b26f20110a": "実装予定", 
            }
            uuid_list["misc"] = []

            for playertitle_uuid, description in playertitle_list.items():
                playertitle = ApiData.playertitle_from_uuid(playertitle_uuid)
                uuid_list["misc"].append({
                    "name": playertitle["uuid"],
                    "title": playertitle["displayName"]["ja-JP"],
                    "file": playertitle["titleText"]["ja-JP"],
                    "description": description
                })
                playertitles = Misc.CoreList.remove_list_from_uuid(playertitles, playertitle["uuid"])
            
            # other
            uuid_list["other"] = []
            for playertitle in playertitles:
                if playertitle.get("displayName")!=None and playertitle.get("titleText")!=None:
                    uuid_list["other"].append({
                        "name": playertitle["uuid"],
                        "title": playertitle["displayName"]["ja-JP"],
                        "file": playertitle["titleText"]["ja-JP"]
                    })
            
            # makelist
            def makelist(gallery: list) -> str:
                ret = "{{Gallery-begin}}\n"
                for item in gallery:
                    ret = ret + "{{Gallery|[[File:Player Titles Red.png]]|" + item["title"] + "|" + item["file"]
                    if item.get("description")!=None:
                        ret = ret + "|" + item["description"] + "}}"
                    else:
                        ret = ret + "}}"
                    ret = ret + "\n"
                ret = ret + "{{Gallery-end}}"
                return ret

            def maketab(gallery) -> str:
                if type(gallery)==type([]):
                    return makelist(gallery)
                elif type(gallery)==type({}):
                    ret = "{{Tab|bgnone=yes\n"
                    i: int = 1
                    for key, value in gallery.items():
                        ret = ret + f"|tab{i} = {key} |panel{i} = \n{maketab(value)}\n"
                        i = i + 1
                    ret = ret + "}}"
                    return ret
            
            os.makedirs(f"output/playertitles/list", exist_ok=True)
            for name, category in uuid_list.items():
                txt = maketab(category)
                with open(f"output/playertitles/list/{name}.txt", "w", encoding="utf-8") as fp:
                    fp.write(txt)

        except Exception as e:
            messagebox.showerror("タイトル (リスト)", "タイトル の作成に失敗しました。")
            Log.exception(e, "タイトルの作成に失敗しました。", _ftype)

    def levelborders(self):
        _ftype = "CORE.LIST.BORDER"
        
        try:
            data: dict = JSON.read("api/levelborders.json")
            os.makedirs(f"output/levelborders/list", exist_ok=True)


            def makeFile(filename: str, category: str):
                out = "{{Gallery-begin}}\n"

                for value in data:
                    level = value["startingLevel"]
                    fn = filename.format(level=level)

                    out = out + "{{" + f"Gallery|[[File:{fn}]]|レベル{level}ボーダー||レベル{level}" + "}}\n"
                
                out = out + "{{Gallery-end}}"
                
                with open(f"output/levelborders/list/{category}.txt", "w", encoding="utf-8") as fp:
                    fp.write(out)
                
            
            makeFile("Border Lv{level}.png", "number")
            makeFile("Border Card Lv{level}.png", "card")
                

        except Exception as e:
            messagebox.showerror("レベルボーダー (リスト)", "レベルボーダー の作成に失敗しました。")
            Log.exception(e, "レベルボーダーの作成に失敗しました。", _ftype)
