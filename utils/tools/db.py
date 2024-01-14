import os, dateutil.parser, datetime, re
from pytz import timezone
from utils.tools.localize import Lang
from utils.tools.wiki import Wiki, WikiString, FileName
from utils.tools.gui import Gui
from utils.tools.json import JSON, Lua
from utils.tools.api import API

class Spray():
    def make_list():
        sprays = JSON.read("api/sprays.json")
        dictionary: dict = {}
        row: dict = {
            "Gear": [],
            "Battlepass": [],
            "Eventpass": [],
            "Bundle": [],
            "Misc": []
        }

        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/07.12.00.2164217/bundles2.json")

        # data
        dictionary = {}
        for d in sprays:
            dictionary[d["uuid"]] = {
                "name": d["displayName"]["en-US"],
                "localized_name": d["displayName"]["ja-JP"],
                "uuid": d["uuid"],
                "image": FileName.spray(d, "image"),
                "icon": FileName.spray(d, "icon"),
                "relation": [],
                "bundle": "",
                "description": ""
            }

        # agent gear
        for agent in sorted(agents, key=lambda x: x["displayName"]["ja-JP"]):
            agent_uuid = agent["uuid"]

            for contract in contracts:
                if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Spray":
                                dictionary[level["reward"]["uuid"]]["relation"].append("エージェントギア")
                                if contract["displayName"]["ja-JP"]=="オーメンの契約書":
                                    contract["displayName"]["ja-JP"] = "オーメンのギア"
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                sprays = API.remove_list_from_uuid(sprays, level["reward"]["uuid"])
                                row["Gear"].append(level["reward"]["uuid"])

        # battlepass
        act: int = 1
        episode: int = 1
        for season_uuid in API.get_act_list():
            for contract in contracts:
                if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==season_uuid:

                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Spray":
                                dictionary[level["reward"]["uuid"]]["relation"].append("バトルパス")
                                dictionary[level["reward"]["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                sprays = API.remove_list_from_uuid(sprays, level["reward"]["uuid"])
                                row["Battlepass"].append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Spray":
                                    dictionary[free_level["uuid"]]["relation"].append("バトルパス")
                                    dictionary[free_level["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    sprays = API.remove_list_from_uuid(sprays, free_level["uuid"])
                                    row["Battlepass"].append(free_level["uuid"])
            
            if act==3:
                act = 1
                episode = episode + 1
            else:
                act = act+1
        
        # eventpass
        for eventpass_uuid in API.get_eventpass_list():
            for contract in contracts:
                if contract["uuid"] == eventpass_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Spray":
                                dictionary[level["reward"]["uuid"]]["relation"].append("イベントパス")
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                sprays = API.remove_list_from_uuid(sprays, level["reward"]["uuid"])
                                row["Eventpass"].append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Spray":
                                    dictionary[free_level["uuid"]]["relation"].append("イベントパス")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    sprays = API.remove_list_from_uuid(sprays, free_level["uuid"])
                                    row["Eventpass"].append(free_level["uuid"])
        
        # bundle
        addition = {
            "2ed936df-4959-acc7-9aca-358d34a50619": [{"name": "Doodle Buds // Tactifriends Spray", "uuid": "8f9caa22-4dd6-5649-1007-0bbaf7001c04"}, {"name": "Doodle Buds // League of Legends Spray", "uuid": "bbdcf328-4f71-3c0c-7830-568913236d35"}], #doodle buds
            "2116a38e-4b71-f169-0d16-ce9289af4bfa": [{"name": "Prime Brick Spray", "uuid": "880d5de5-4268-769d-5407-55921ad2db12"}], #prime
            "e6032bbf-403e-47e4-8fbc-a1b212d966e7": [{"name": "Imperium Spray", "uuid": "229d49b4-4e8f-cb5a-12c9-39a5ed45e7ed"}], #imperium
            "3d580e29-435b-8e65-22f4-3c8b8974f5fd": [{"name": "Gaia's Vengeance, Ep 7 Spray", "uuid": "a418d89e-49af-141e-4edd-de9ec79c34da"}], #gaia's ep7
            "f79f85ec-48f8-6573-873a-75b4627b615e": [{"name": "Valiant Hero Spray", "uuid": "3baa428b-4e8e-df38-e50f-1e86f2f9584f"}], #valiant hero
            "753739e7-4447-617c-8253-cf8d9d577b58": [{"name": "Sentinels of Light, Ep 7 Spray", "uuid": "0736596a-4ec0-7330-1f74-44843b6d0663"}], #sentinels of light (ep7)
            "3ad3de55-422b-4076-a89f-81a38ce24973": [{"name": "Overdrive Spray", "uuid": "983d6cf0-43d5-900e-ca43-5298f44378af"}], #overdrive
            "a012ba57-4a6a-db6b-fad2-bebb84a9a588": [{"name": "Kuronami Spray", "uuid": "515a130a-4a2e-e0a4-9a73-c784f8f16e2a"}], #kuronami
            "a042042c-40f3-df48-dbaa-4bbbd6324ba7": [{"name": "Outlaw Spray", "uuid": "b9acb0d5-458f-14db-6a7c-829379727fbd"}], #Throwback Pack: Outlaw

        }
        for uuid,values in addition.items():
            if not uuid in bundles:
                b = API.bundle_by_uuid(uuid)
                b["sprays"] = values
                bundles.append(b)

        for bundle in bundles:
            for bundle_spray in bundle["sprays"]:
                for spray in sprays:
                    if bundle_spray["uuid"]==spray["uuid"]:
                        dictionary[spray["uuid"]]["relation"].append("スキンセット")
                        dictionary[spray["uuid"]]["bundle"] = API.get_bundle_name(bundle["uuid"])
                        sprays = API.remove_list_from_uuid(sprays, spray["uuid"])
                        row["Bundle"].append(spray["uuid"])
        
        # prime gaming drops
        for d in API.get_prime_gaming_reward():
            if d["type"]=="sprays":
                dictionary[d["uuid"]]["relation"].append("Prime Gaming")
                dictionary[d["uuid"]]["description"] = d["date"]
                sprays = API.remove_list_from_uuid(sprays, d["uuid"])
                row["Misc"].append(d["uuid"])

        # misc
        misc = [
            {
                "uuid": "d7efbdd5-4a77-f858-a133-cfb8956ca1fe",
                "description": "スプレーを装備していない状態"
            },
            {
                "uuid": "0a6db78c-48b9-a32d-c47a-82be597584c1",
                "description": "デフォルトのスプレー"
            },
            {
                "uuid": "47575563-4d43-96fb-1586-849d35c7ddd5",
                "description": "RiotX Arcaneのサイト上で特定のミッションをクリア"
            },
            {
                "uuid": "f9bcf120-42b6-6986-2acd-6aa87bab4089",
                "description": "[[VCT 2021: Champions Berlin]]（2021年12月1日～11日）の視聴報酬"
            },
            {
                "uuid": "be8eeab6-43eb-d0b7-7b38-f6bb25ef7547",
                "description": "エイプリルフール期間中（2022年4月1日～9日）にログイン"
            },
            {
                "uuid": "a7b00f01-49ee-c0c2-a910-4d9ae605dbe1",
                "description": "[[VCT 2022: Champions Istanbul|Champions 2022]]（2022年9月16～17日）の視聴報酬"
            },
            {
                "uuid": "6aff01b3-443c-d98c-820e-05852efc075f",
                "description": "[[BLAST Spike Nations 2022]]の決勝戦（2022年10月16日）の視聴報酬"
            },
            {
                "uuid": "890c4f6d-4794-3d88-617b-1b906c7a8ea6",
                "description": "[[Red Bull]]関連の大会の視聴報酬・キャンペーン報酬"
            },
            {
                "uuid": "32df08b6-4d6e-d642-b57c-fc915063418b",
                "description": "エイプリルフール期間中（2023年4月1日～8日）にログイン"
            },
            {
                "uuid": "8080ba65-4089-3487-dcf5-f298be03a470",
                "description": "[[VCT 2023: Champions Los Angeles]]（2023年8月17日～26日）の視聴報酬"
            },
            {
                "uuid": "41450726-4566-aca7-6b98-8d9fcd9105d7",
                "description": "コミュニティーチャレンジの達成報酬"
            }
        ]
        for d in misc:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = d["description"]
            sprays = API.remove_list_from_uuid(sprays, d["uuid"])
            row["Misc"].append(d["uuid"])
        
        for d in sprays:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = "未使用"
            row["Misc"].append(d["uuid"])

        return dictionary, row

class Playercard():
    def make_list():
        playercards = JSON.read("api/playercards.json")
        dictionary: dict = {}
        row: dict = {
            "Gear": [],
            "Battlepass": [],
            "Eventpass": [],
            "Bundle": [],
            "Misc": [],
        }

        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/07.12.00.2164217/bundles2.json")

        # data
        dictionary = {}
        for d in playercards:
            dictionary[d["uuid"]] = {
                "name": d["displayName"]["en-US"],
                "localized_name": d["displayName"]["ja-JP"],
                "uuid": d["uuid"],
                "image": FileName.playercard(d, "large"),
                "icon": FileName.playercard(d, "small"),
                "wide": FileName.playercard(d, "wide"),
                "relation": [],
                "bundle": "",
                "description": ""
            }

        # agent gear
        for agent in sorted(agents, key=lambda x: x["displayName"]["ja-JP"]):
            agent_uuid = agent["uuid"]

            for contract in contracts:
                if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="PlayerCard":
                                dictionary[level["reward"]["uuid"]]["relation"].append("エージェントギア")
                                if contract["displayName"]["ja-JP"]=="オーメンの契約書":
                                    contract["displayName"]["ja-JP"] = "オーメンのギア"
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                playercards = API.remove_list_from_uuid(playercards, level["reward"]["uuid"])
                                row["Gear"].append(level["reward"]["uuid"])

        # battlepass
        act: int = 1
        episode: int = 1
        for season_uuid in API.get_act_list():
            for contract in contracts:
                if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==season_uuid:

                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="PlayerCard":
                                dictionary[level["reward"]["uuid"]]["relation"].append("バトルパス")
                                dictionary[level["reward"]["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                playercards = API.remove_list_from_uuid(playercards, level["reward"]["uuid"])
                                row["Battlepass"].append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="PlayerCard":
                                    dictionary[free_level["uuid"]]["relation"].append("バトルパス")
                                    dictionary[free_level["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    playercards = API.remove_list_from_uuid(playercards, free_level["uuid"])
                                    row["Battlepass"].append(free_level["uuid"])
            
            if act==3:
                act = 1
                episode = episode + 1
            else:
                act = act+1
        
        # eventpass
        for eventpass_uuid in API.get_eventpass_list():
            for contract in contracts:
                if contract["uuid"] == eventpass_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="PlayerCard":
                                dictionary[level["reward"]["uuid"]]["relation"].append("イベントパス")
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                playercards = API.remove_list_from_uuid(playercards, level["reward"]["uuid"])
                                row["Eventpass"].append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="PlayerCard":
                                    dictionary[free_level["uuid"]]["relation"].append("イベントパス")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    playercards = API.remove_list_from_uuid(playercards, free_level["uuid"])
                                    row["Eventpass"].append(free_level["uuid"])
        
        # bundle
        addition = {
            "e6032bbf-403e-47e4-8fbc-a1b212d966e7": [{"name": "Imperium Card", "uuid": "13b0954b-4347-6698-1141-4589e6ef726d"}], #imperium
            "3d580e29-435b-8e65-22f4-3c8b8974f5fd": [{"name": "Gaia's Vengeance, Ep 7 Card", "uuid": "e6773d10-4a98-1ddf-d2c8-0783708dffb5"}], #gaia's ep7
            "d84cd2bf-42e5-34e8-062f-cba8d2c66fb2": [{"name": "Undercity Card", "uuid": "02096add-4c34-b916-af22-50b3791da2f4"}], #undercity
            "54f8793c-4daa-6e45-bcfd-e9bfc742dc30": [{"name": "Origin Card", "uuid": "3c930c58-4f56-1a14-6397-c3bd42f31955"}], #origin
            "f79f85ec-48f8-6573-873a-75b4627b615e": [{"name": "Valiant Hero Card", "uuid": "8de9de55-4e26-94e4-bdba-d790b1bd9b34"}], #valiant hero
            "753739e7-4447-617c-8253-cf8d9d577b58": [{"name": "Sentinels of Light, Ep 7 Card", "uuid": "02ca101e-4f41-fc84-6412-f28230297d76"}], #sentinels of light (ep7)
            "3ad3de55-422b-4076-a89f-81a38ce24973": [{"name": "Overdrive Card", "uuid": "9de26ca3-4203-989d-5c3f-a883af147ac7"}], #overdrive
            "a012ba57-4a6a-db6b-fad2-bebb84a9a588": [{"name": "Kuronami Card", "uuid": "1a127cbf-4131-3581-da59-529b7e0d9495"}], #kuronami
            "a042042c-40f3-df48-dbaa-4bbbd6324ba7": [{"name": "Outlaw Card", "uuid": "6657a4ed-43c9-2218-4970-adbea58ede33"}], #Throwback Pack: Outlaw
        }
        for uuid,values in addition.items():
            if not uuid in bundles:
                b = API.bundle_by_uuid(uuid)
                b["cards"] = values
                bundles.append(b)

        for bundle in bundles:
            for bundle_card in bundle["cards"]:
                for d in playercards:
                    if bundle_card["uuid"]==d["uuid"]:
                        dictionary[d["uuid"]]["relation"].append("スキンセット")
                        dictionary[d["uuid"]]["bundle"] = API.get_bundle_name(bundle["uuid"])
                        playercards = API.remove_list_from_uuid(playercards, d["uuid"])
                        row["Bundle"].append(d["uuid"])
        
        # prime gaming drops
        for d in API.get_prime_gaming_reward():
            if d["type"]=="playercards":
                dictionary[d["uuid"]]["relation"].append("Prime Gaming")
                dictionary[d["uuid"]]["description"] = d["date"]
                playercards = API.remove_list_from_uuid(playercards, d["uuid"])
                row["Misc"].append(d["uuid"])

        # premier
        premier = [
            {
                "uuid": "23a03943-4c16-0de4-0fe0-b9bcba24a26a",
                "description": "[[Premier]]（{{Premier|オープンベータ}}）で1試合参加する",
                "relation": ["オープンベータ"]
            },
            {
                "uuid": "3f77186a-40a9-7abc-9ac6-5a988d279dad",
                "description": "[[Premier]]（{{Premier|オープンベータ}}）のプレイオフで勝利する",
                "relation": ["オープンベータ"]
            },
            {
                "uuid": "29f89efd-4613-c244-fc54-8fb6da4f88e3",
                "description": "[[Premier]]（{{Premier|イグニッション}}）で1試合参加する",
                "relation": ["イグニッション"]
            },
            {
                "uuid": "f32449d4-4787-7344-6559-cdb30e63f70c",
                "description": "[[Premier]]（{{Premier|リリース}}）で1試合参加する",
                "relation": ["リリース"]
            },
            {
                "uuid": "ffeb645c-40e0-2e87-123f-4783a7db4b92",
                "description": "[[Premier]]（{{Premier|E7A3}}）で1試合参加する",
                "relation": ["E7A3"]
            },
        ]
        for d in premier:
            d["relation"].append("Premier")
            dictionary[d["uuid"]]["relation"] = d["relation"]
            dictionary[d["uuid"]]["description"] = d["description"]
            playercards = API.remove_list_from_uuid(playercards, d["uuid"])
            row["Misc"].append(d["uuid"])

        # misc
        misc = [
            {
                "uuid": "9fb348bc-41a0-91ad-8a3e-818035c4e561",
                "description": "デフォルトのプレイヤーカード"
            },
            {
                "uuid": "e6529e9c-4a2b-c31c-7252-e185a8ce4a04",
                "description": "クローズドベータへのアクセス権を入手したプレイヤーに与えられた（2020年6月2日）"
            },
            {
                "uuid": "e17c2e94-44fb-9486-8497-9dab8b942b3d",
                "description": "[[AfreecaTV Asia Showdown]]（2020年9月18～20日）の視聴報酬"
            },
            {
                "uuid": "bb5cedcd-4ed9-ee2e-f129-48bf60a8e540",
                "description": "[[DUALITY]]の公開記念で48時間の限定配布がなされたが、コード交換サイトの接続不具合により2021年6月8日に存在する全アカウントに配布された"
            },
            {
                "uuid": "bab9caaa-4913-2704-833e-8c89e2128eb9",
                "description": "2021年6月10日に存在するアカウントに与えられた（VALORANT1周年記念）"
            },
            {
                "uuid": "f67a7c8f-4d3f-b76f-2921-478a4da44109",
                "description": "2021年11月24日に存在するアカウントに与えられた（[[VCT 2021: Champions Berlin]]開催記念）"
            },
            {
                "uuid": "68b0c8c2-4158-7b21-658d-b4ae86f137ce",
                "description": "2022年7月14日以降にログインで入手"
            },
            {
                "uuid": "9e9c4c4a-4d53-6c37-4e48-85b771b9dd4e",
                "description": "2022年8月12日～20日にログインで入手"
            },
            {
                "uuid": "c87737f8-44bc-1b71-8424-c18d9cd6336a",
                "description": "[[VCT 2022: Champions Istanbul]]の決勝（2022年9月18日）の視聴報酬"
            },
            {
                "uuid": "6a578461-430d-e0a9-d67e-4c967e0bdf1a",
                "description": "[[VCT 2022: Game Changers Championship]]の決勝（2022年11月21日）の視聴報酬"
            },
            {
                "uuid": "cb7157ed-4fc7-a5c9-714b-1786ca3949f1",
                "description": "[[Riot Games ONE 2022]]（2022年12月23～24日）の来場者特典"
            },
            {
                "uuid": "0c196ea1-48ac-97eb-5362-c884937c016f",
                "description": "[[VCT 2023: Masters Tokyo]]の決勝戦（2023年6月25日）の視聴報酬"
            },
            {
                "uuid": "01aa3a02-4ab1-0739-83fd-f3b37eba01db",
                "description": "[[VCT 2023: Champions Los Angeles]]の決勝戦（2023年8月26日）の視聴報酬"
            },
            {
                "uuid": "c3e4a7e3-48c4-8476-6bf5-39892718e1f2",
                "description": "[[Red Bull Home Ground 2023]]（2023年11月3～5日）の視聴報酬"
            },
            {
                "uuid": "bf8a808a-48a5-8c66-cc66-39b49049f7b4",
                "description": "2023年11月29日以降にログインで入手"
            },
            {
                "uuid": "17712b8a-4555-8b65-2bbe-75a288069420",
                "description": "コミュニティーチャレンジの達成報酬"
            },
            {
                "uuid": "260c7a79-4d04-36d5-9b68-a097519459cd",
                "description": "コミュニティーチャレンジの達成報酬"
            }
        ]
        for d in misc:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = d["description"]
            playercards = API.remove_list_from_uuid(playercards, d["uuid"])
            row["Misc"].append(d["uuid"])
        
        
        # unused
        for d in playercards:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = "未使用"
            row["Misc"].append(d["uuid"])

        #JSON.save("output/lists/playercards.json", dictionary)
        #JSON.save("output/lists/remain_playercards.json", playercards)
        return dictionary, row

class Buddy():
    def make_list():
        buddies = JSON.read("api/buddies.json")
        dictionary: dict = {}
        row: dict = {
            "Gear": [],
            "Battlepass": [],
            "Eventpass": [],
            "Bundle": [],
            "Competitive": [],
            "Misc": []
        }

        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/07.12.00.2164217/bundles2.json")
        competitivetiers = JSON.read("api/competitivetiers.json")[-1]

        # data
        for d in buddies:
            dictionary[d["uuid"]] = {
                "name": d["displayName"]["en-US"],
                "localized_name": d["displayName"]["ja-JP"],
                "uuid": d["uuid"],
                "image": FileName.buddy(d),
                "relation": [],
                "bundle": "",
                "description": ""
            }

        # agent gear
        for agent in sorted(agents, key=lambda x: x["displayName"]["ja-JP"]):
            agent_uuid = agent["uuid"]

            for contract in contracts:
                if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="EquippableCharmLevel":
                                uuid = API.buddy_by_charmlevel_uuid(level["reward"]["uuid"])["uuid"]
                                dictionary[uuid]["relation"].append("エージェントギア")
                                if contract["displayName"]["ja-JP"]=="オーメンの契約書":
                                    contract["displayName"]["ja-JP"] = "オーメンのギア"
                                dictionary[uuid]["bundle"] = contract["displayName"]["ja-JP"]
                                buddies = API.remove_list_from_uuid(buddies, uuid)
                                row["Gear"].append(uuid)

        # battlepass
        act: int = 1
        episode: int = 1
        for season_uuid in API.get_act_list():
            for contract in contracts:
                if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==season_uuid:

                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="EquippableCharmLevel":
                                uuid = API.buddy_by_charmlevel_uuid(level["reward"]["uuid"])["uuid"]
                                dictionary[uuid]["relation"].append("バトルパス")
                                dictionary[uuid]["relation"].append(f"Episode {episode}: Act {act}")
                                dictionary[uuid]["bundle"] = contract["displayName"]["ja-JP"]
                                buddies = API.remove_list_from_uuid(buddies, uuid)
                                row["Battlepass"].append(uuid)

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="EquippableCharmLevel":
                                    uuid = API.buddy_by_charmlevel_uuid(free_level["uuid"])["uuid"]
                                    dictionary[uuid]["relation"].append("バトルパス")
                                    dictionary[uuid]["relation"].append(f"Episode {episode}: Act {act}")
                                    dictionary[uuid]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[uuid]["description"] = "無料報酬"
                                    buddies = API.remove_list_from_uuid(buddies, uuid)
                                    row["Battlepass"].append(uuid)
            
            if act==3:
                act = 1
                episode = episode + 1
            else:
                act = act+1
        
        # eventpass
        for eventpass_uuid in API.get_eventpass_list():
            for contract in contracts:
                if contract["uuid"] == eventpass_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="EquippableCharmLevel":
                                uuid = API.buddy_by_charmlevel_uuid(level["reward"]["uuid"])["uuid"]
                                dictionary[uuid]["relation"].append("イベントパス")
                                dictionary[uuid]["bundle"] = contract["displayName"]["ja-JP"]
                                buddies = API.remove_list_from_uuid(buddies, uuid)
                                row["Eventpass"].append(uuid)

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="EquippableCharmLevel":
                                    uuid = API.buddy_by_charmlevel_uuid(free_level["uuid"])["uuid"]
                                    dictionary[uuid]["relation"].append("イベントパス")
                                    dictionary[uuid]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[uuid]["description"] = "無料報酬"
                                    buddies = API.remove_list_from_uuid(buddies, uuid)
                                    row["Eventpass"].append(uuid)
        
        # bundle
        addition = {
            "e6032bbf-403e-47e4-8fbc-a1b212d966e7": [{"name": "Imperium Buddy", "uuid": "8f32610e-48f1-4d6f-46ad-90911845dad3"}], #imperium
            "3d580e29-435b-8e65-22f4-3c8b8974f5fd": [{"name": "Gaia's Vengeance, Ep 7 Buddy", "uuid": "6bdc0477-4b5a-94ed-b944-f284de3b4bd8"}], #gaia's ep7
            "f7f37856-4af7-9b0e-08aa-91a5207c0439": [{"name": "Zedd Buddy", "uuid": "70963a6d-45b7-8fd4-c6aa-62b2155715aa"}], #spectrum
            "f79f85ec-48f8-6573-873a-75b4627b615e": [{"name": "Valiant Hero Buddy", "uuid": "c907c26b-4d42-d60c-ce3a-06b96f911966"}], #valiant hero
            "753739e7-4447-617c-8253-cf8d9d577b58": [{"name": "Sentinels of Light, Ep 7 Buddy", "uuid": "d655890d-47fb-9f93-73a0-e2bd661f9c45"}], #sentinels of light (ep7)
            "3ad3de55-422b-4076-a89f-81a38ce24973": [{"name": "Overdrive Buddy", "uuid": "8b869090-4f20-f809-1932-67909dd92b1f"}], #overdrive
            "a012ba57-4a6a-db6b-fad2-bebb84a9a588": [{"name": "Kuronami Buddy", "uuid": "f57762a3-423c-70f7-c8d5-14bf97d0093e"}], #kuronami
            "a042042c-40f3-df48-dbaa-4bbbd6324ba7": [{"name": "Outlaw Buddy", "uuid": "67592092-4c30-79b7-1a03-bc83deeadd59"}], #Throwback Pack: Outlaw
        }
        for uuid,values in addition.items():
            if not uuid in bundles:
                b = API.bundle_by_uuid(uuid)
                b["buddies"] = values
                bundles.append(b)

        for bundle in bundles:
            for bundle_buddy in bundle["buddies"]:
                for d in buddies:
                    if bundle_buddy["uuid"]==d["uuid"]:
                        dictionary[d["uuid"]]["relation"].append("スキンセット")
                        dictionary[d["uuid"]]["bundle"] = API.get_bundle_name(bundle["uuid"])
                        buddies = API.remove_list_from_uuid(buddies, d["uuid"])
                        row["Bundle"].append(d["uuid"])
        
        # prime gaming drops
        for d in API.get_prime_gaming_reward():
            if d["type"]=="buddies":
                dictionary[d["uuid"]]["relation"].append("Prime Gaming")
                dictionary[d["uuid"]]["description"] = d["date"]
                buddies = API.remove_list_from_uuid(buddies, d["uuid"])
                row["Misc"].append(d["uuid"])

        # event winner
        winner = [
            {
                "uuid": "82bdb8b5-40bf-9b65-272e-4eb7dad1264e",
                "description": "VCT Mastersの優勝報酬"
            },
            {
                "uuid": "e96e6f84-4315-409a-09bf-788e0cf13ecf",
                "description": "VCT Championsの優勝報酬"
            },
            {
                "uuid": "902bac6e-4674-cda0-cd3f-92b65d943fed",
                "description": "VCT Game Changers Championshipの優勝報酬"
            },
            {
                "uuid": "0556c983-462c-1f6b-1bef-b1979aa07a7f",
                "description": "[[VCT 2023: LOCK//IN São Paulo]]の優勝報酬"
            },
        ]
        for d in winner:
            dictionary[d["uuid"]]["relation"].append("大会優勝報酬")
            dictionary[d["uuid"]]["description"] = d["description"]
            buddies = API.remove_list_from_uuid(buddies, d["uuid"])
            row["Misc"].append(d["uuid"])

        # premier
        premier = [
            # ignition
            {
                "uuid": "ac306edc-49bd-0f04-0104-afa2ae783b99",
                "description": "[[Premier]]（{{Premier|イグニッション}}）で優勝する",
                "relation": ["イグニッション"]
            },

            # release
            {
                "uuid": "d3a6c031-4090-e50e-03a4-b2b4afbf141e",
                "description": "[[Premier]]（{{Premier|リリース}}）のオープンディビジョンで優勝する",
                "relation": ["リリース", "オープン"]
            },
            {
                "uuid": "8ef76df3-4f31-4a8b-534b-b29be6f68bed",
                "description": "[[Premier]]（{{Premier|リリース}}）のインターミディエイトディビジョンで優勝する",
                "relation": ["リリース", "インターミディエイト"]
            },
            {
                "uuid": "8d6f45c8-4031-7104-6079-1f934c30917e",
                "description": "[[Premier]]（{{Premier|リリース}}）のアドバンスドディビジョンで優勝する",
                "relation": ["リリース", "アドバンスド"]
            },
            {
                "uuid": "a1bc1340-4884-7eb2-ceeb-aebea6ff5e3b",
                "description": "[[Premier]]（{{Premier|リリース}}）のエリートディビジョンで優勝する",
                "relation": ["リリース", "エリート"]
            },
            {
                "uuid": "ffde61af-4686-0d77-11c2-9ea357381b87",
                "description": "[[Premier]]（{{Premier|リリース}}）のコンテンダーディビジョンで優勝する",
                "relation": ["リリース", "コンテンダー"]
            },

            # ep7act3
            {
                "uuid": "46473ed2-4e80-0066-4a0d-a9b7905d93fa",
                "description": "[[Premier]]（{{Premier|E7A3}}）のオープンディビジョンで優勝する",
                "relation": ["E7A3", "オープン"]
            },
            {
                "uuid": "68f6dbbb-422b-428b-9ef0-3d926312e7cb",
                "description": "[[Premier]]（{{Premier|E7A3}}）のインターミディエイトディビジョンで優勝する",
                "relation": ["E7A3", "インターミディエイト"]
            },
            {
                "uuid": "b13a445f-4ff4-fd0e-01fa-c786e00e1bdb",
                "description": "[[Premier]]（{{Premier|E7A3}}）のアドバンスドディビジョンで優勝する",
                "relation": ["E7A3", "アドバンスド"]
            },
            {
                "uuid": "a8834ead-4bba-4405-40ec-40b7c7d8d8e4",
                "description": "[[Premier]]（{{Premier|E7A3}}）のエリートディビジョンで優勝する",
                "relation": ["E7A3", "エリート"]
            },
            {
                "uuid": "deed2aa7-4466-4df9-3fd8-edb372871d51",
                "description": "[[Premier]]（{{Premier|E7A3}}）のコンテンダーディビジョンで優勝する",
                "relation": ["E7A3", "コンテンダー"]
            },
        ]
        for d in premier:
            d["relation"].append("Premier")
            dictionary[d["uuid"]]["relation"] = d["relation"]
            dictionary[d["uuid"]]["description"] = d["description"]
            buddies = API.remove_list_from_uuid(buddies, d["uuid"])
            row["Competitive"].append(d["uuid"])

        # misc
        misc = [
            {
                "uuid": "ad508aeb-44b7-46bf-f923-959267483e78",
                "description": "Riot Gamesの社員から与えられる特別なガンバディー"
            },
            {
                "uuid": "d12a80c0-44a0-0549-cc1f-eeb83f7ad248",
                "description": "中東地域でのVALORANTリリース記念"
            },
            {
                "uuid": "e4267845-4725-ff8e-6c71-ae933844565f",
                "description": "{{Patch|1.14}}で[[スノーボールファイト]]をプレイする"
            },
            {
                "uuid": "9e601160-4679-d2df-261b-56a398248271",
                "description": "[[BLAST Spike Nations 2021]]（2021年10月9日）の視聴報酬"
            },
            {
                "uuid": "912110cb-4f40-ada7-e338-518244fff9b2",
                "description": "Arcaneプレミア（2021年11月7日）の視聴報酬"
            },
            {
                "uuid": "237f36ef-40d5-410a-84be-6c896aad6fde",
                "description": "RiotX Arcaneのサイト上で特定のミッションをクリア"
            },
            {
                "uuid": "e2e5ab96-4103-8473-14a7-8d8321a3ae6e",
                "description": "[[VALORANT Champions 2021]]の決勝戦（2021年12月12日）の視聴報酬"
            },
            {
                "uuid": "ada5f921-4d81-f439-0017-0e86877a02bd",
                "description": "2021年12月15日以降にログイン"
            },
            {
                "uuid": "c14745d0-4958-26d9-60e6-7c863080fef1",
                "description": "二要素認証を有効化する"
            },
            {
                "uuid": "86e61d30-4f29-ef14-e880-ef89f53eff09",
                "description": "2022年12月中にRiotアカウントとXboxプロフィールをリンクする"
            },
            {
                "uuid": "d2b317f7-4f19-7052-cd50-33a32f210da0",
                "description": "[[VCT 2023: LOCK//IN São Paulo]]の決勝戦（2023年3月4日）の視聴報酬"
            },
            {
                "uuid": "ba57ccb8-4536-1859-22ca-419eeda037d2",
                "description": "[[VCT 2023: Champions Los Angeles]]の現地会場にてVerizonが実施したキャンペーンの報酬"
            },
            {
                "uuid": "8eec6c97-4765-f374-c37e-0e9a9b02eed5",
                "description": "[[VCT 2023: Game Changers Championship]]の決勝戦（2023年12月4日）の視聴報酬"
            },
            {
                "uuid": "6364afb1-4ae0-3c71-f5a8-89b7f863c14e",
                "description": "コミュニティーチャレンジの達成報酬"
            }
        ]
        for d in misc:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = d["description"]
            buddies = API.remove_list_from_uuid(buddies, d["uuid"])
            row["Misc"].append(d["uuid"])
        
        # competitive
        episodes = API.get_episode_list()
        for tier in competitivetiers["tiers"]:
            for i in range(len(episodes)):
                for buddy in buddies:
                    if buddy["displayName"]["en-US"]==f"EP{i+1}: " + tier["divisionName"]["en-US"].capitalize() + f" Buddy":
                        dictionary[buddy["uuid"]]["relation"].append("コンペティティブ")
                        dictionary[buddy["uuid"]]["relation"].append(f"Episode {i+1}")
                        dictionary[buddy["uuid"]]["relation"].append(tier["divisionName"]["ja-JP"])
                        buddies = API.remove_list_from_uuid(buddies, buddy["uuid"])
                        row["Competitive"].append(buddy["uuid"])
        
        # unused
        for d in buddies:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = "未使用"
            row["Misc"].append(d["uuid"])

        #JSON.save("output/lists/buddies.json", dictionary)
        #JSON.save("output/lists/remain_buddies.json", buddies)
        return dictionary, row

class Weapon_Skin():
    def make_list(weapon):
        skins = weapon["skins"]
        offer = JSON.read("api/offer.json")
        dictionary: dict = {}
        row: list = []

        # data
        dictionary = {}
        for skin in skins:
            name = skin["displayName"]["ja-JP"]
            name_us = skin["displayName"]["en-US"]
            weapon_name = weapon["displayName"]["en-US"]
            tier = API.contenttier_by_uuid(skin["contentTierUuid"])
            if tier!=None:
                tier = tier["devName"].lower()
            else:
                tier = ""
                
            bundle = FileName.bundle_from_theme(skin["themeUuid"], "ja-JP")

            dictionary[skin["uuid"]] = {
                "name": name_us,
                "localized_name": name,
                "uuid": skin["uuid"],
                "weapon": weapon["displayName"]["ja-JP"],
                "image": FileName.weapon(skin, "icon", WikiString.wiki_format(skin.get("displayName", {})["en-US"]), weapon["displayName"]["en-US"]),
                "bundle": bundle,
                "tier": tier,
                "vp": offer.get(skin["levels"][0]["uuid"], {}).get("vp", 0),
                "swatch": "",
                "video": "",
                "level_upgrade": [],
                "level_image": [],
                "level_swatch": [],
                "level_video": [],
                "level_description": []
            }
            row.append(skin["uuid"])

            # levels
            for level in skin["levels"]:

                if level["displayName"]["ja-JP"]!=name:
                    if level.get("levelItem")!=None:
                        dictionary[skin["uuid"]]["level_upgrade"].append(level["levelItem"].replace("EEquippableSkinLevelItem::", ""))
                    else:
                        dictionary[skin["uuid"]]["level_upgrade"].append("")

                    if level["streamedVideo"]!=None:
                        dictionary[skin["uuid"]]["level_video"].append(FileName.weapon(level, "level_video", name_us))
                    else:
                        dictionary[skin["uuid"]]["level_video"].append("")
                    
                    dictionary[skin["uuid"]]["level_image"].append("")
                    dictionary[skin["uuid"]]["level_swatch"].append("")

                    # description
                    suffix: str = ""
                    try:
                        suffix = level["displayName"]["ja-JP"].splitlines()[1]
                    except IndexError:
                        pass
                    dictionary[skin["uuid"]]["level_description"].append(suffix.replace("(", "").replace(")", ""))

                else:
                    if level["streamedVideo"]!=None:
                        dictionary[skin["uuid"]]["video"] = FileName.weapon(level, "level_video", name_us)
            
            # chromas
            swatch_exception = [
                "34919680-4f00-554b-0c2b-95acca7d0d36", # VALORANT GO! Ghost
                "9103fdf7-4361-5ac5-37ae-7cb51f13f45d", # Raze Gear
                "4725c2c4-45b7-d9ab-ff4f-a79c3b2dd9ec", # Astra Gear
            ]
            for chroma in skin["chromas"]:
                if chroma["displayName"]["ja-JP"]!=name and chroma["displayName"]["ja-JP"]!="Standard":
                    # video
                    if chroma["streamedVideo"]!=None:
                        dictionary[skin["uuid"]]["level_video"].append(FileName.weapon(chroma, "level_video", name_us))
                    else:
                        dictionary[skin["uuid"]]["level_video"].append("")

                    # upgrade
                    dictionary[skin["uuid"]]["level_upgrade"].append("variant")
                    
                    # image
                    dictionary[skin["uuid"]]["level_image"].append(FileName.weapon(chroma, "icon", name_us))

                    # swatch
                    if chroma["swatch"]!=None and (not skin["uuid"] in swatch_exception):
                        dictionary[skin["uuid"]]["level_swatch"].append(FileName.weapon(chroma, "swatch", name_us, weapon_name, skin["themeUuid"]))
                    else:
                        dictionary[skin["uuid"]]["level_swatch"].append("")

                    # description
                    suffix: str = ""
                    try:
                        suffix = chroma["displayName"]["ja-JP"].splitlines()[1]
                    except IndexError:
                        pass
                    dictionary[skin["uuid"]]["level_description"].append(suffix.replace("(", "").replace(")", ""))

                else:
                    # swatch
                    if chroma["swatch"]!=None and (not skin["uuid"] in swatch_exception):
                        dictionary[skin["uuid"]]["swatch"] = FileName.weapon(chroma, "swatch", name_us, weapon_name, skin["themeUuid"])

        #JSON.save("output/lists/sprays.json", dictionary)
        #JSON.save("output/lists/remain_sprays.json", sprays)
        return dictionary, row
    
class Levelborder():
    def make_list():
        borders = JSON.read("api/levelborders.json")
        dictionary: dict = {}
        row: list = []

        # data
        for border in borders:
            level = border["startingLevel"]
            dictionary[border["uuid"]] = {
                "level": level,
                "localized_name": f"レベル{level}ボーダー",
                "uuid": border["uuid"],
                "border": FileName.levelborder(border, "levelNumberAppearance"),
                "frame": FileName.levelborder(border, "smallPlayerCardAppearance")
            }
            row.append(border["uuid"])

        return dictionary, row

class Playertitle():
    def make_list():
        playertitles = JSON.read("api/playertitles.json")
        dictionary: dict = {}
        row: dict = {
            "Gear": [],
            "Battlepass": [],
            "Eventpass": [],
            "Bundle": [],
            "Misc": [],
        }

        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/07.12.00.2164217/bundles2.json")

        # data
        dictionary = {}
        for d in playertitles:
            if d["displayName"]!=None:
                dictionary[d["uuid"]] = {
                    "name": d["displayName"]["en-US"],
                    "localized_name": d["displayName"]["ja-JP"],
                    "uuid": d["uuid"],
                    "title": d["titleText"]["ja-JP"],
                    "relation": [],
                    "bundle": "",
                    "description": ""
                }

        # agent gear
        for agent in sorted(agents, key=lambda x: x["displayName"]["ja-JP"]):
            agent_uuid = agent["uuid"]

            for contract in contracts:
                if contract["content"]["relationType"] == "Agent" and contract["content"].get("relationUuid")==agent_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Title":
                                dictionary[level["reward"]["uuid"]]["relation"].append("エージェントギア")
                                if contract["displayName"]["ja-JP"]=="オーメンの契約書":
                                    contract["displayName"]["ja-JP"] = "オーメンのギア"
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                playertitles = API.remove_list_from_uuid(playertitles, level["reward"]["uuid"])
                                row["Gear"].append(level["reward"]["uuid"])

        # battlepass
        act: int = 1
        episode: int = 1
        for season_uuid in API.get_act_list():
            for contract in contracts:
                if contract["content"]["relationType"] == "Season" and contract["content"].get("relationUuid")==season_uuid:

                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Title":
                                dictionary[level["reward"]["uuid"]]["relation"].append("バトルパス")
                                dictionary[level["reward"]["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                playertitles = API.remove_list_from_uuid(playertitles, level["reward"]["uuid"])
                                row["Battlepass"].append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Title":
                                    dictionary[free_level["uuid"]]["relation"].append("バトルパス")
                                    dictionary[free_level["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    playertitles = API.remove_list_from_uuid(playertitles, free_level["uuid"])
                                    row["Battlepass"].append(free_level["uuid"])
            
            if act==3:
                act = 1
                episode = episode + 1
            else:
                act = act+1
        
        # eventpass
        for eventpass_uuid in API.get_eventpass_list():
            for contract in contracts:
                if contract["uuid"] == eventpass_uuid:
                    for chapter in contract["content"]["chapters"]:
                        for level in chapter["levels"]:
                            if level["reward"]["type"]=="Title":
                                dictionary[level["reward"]["uuid"]]["relation"].append("イベントパス")
                                dictionary[level["reward"]["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                playertitles = API.remove_list_from_uuid(playertitles, level["reward"]["uuid"])
                                row["Eventpass"].append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Title":
                                    dictionary[free_level["uuid"]]["relation"].append("イベントパス")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    playertitles = API.remove_list_from_uuid(playertitles, free_level["uuid"])
                                    row["Eventpass"].append(free_level["uuid"])
        
        # bundle
        addition = {
            "bf987f36-4a33-45e4-3c49-1ab9a2502607": [{"name": "Champion Title", "uuid": "58e5f5db-4b18-cf8a-afa2-b49574b34456"}], #champion
            "2270b116-4255-8a14-4486-db9de4979b89": [{"name": "Jinx Title", "uuid": "8b426759-4e32-0c61-51cc-289dc0a33073"}], #jinx
            "7b6b00f0-4fb9-7395-067d-44bcb4e20d9a": [
                {"name": "Proud Title", "uuid": "c70f542b-4880-c65f-485e-ec8ffd055243", "description": "特定のコードを入力で入手（2021年）・2022年以降はスキンセットで入手可能<ref name=\"2021 Pride\">{{Cite|url=https://playvalorant.com/ja-jp/news/announcements/show-your-pride-in-valorant/|title=VALORANTでプライドを示そう|website=VALORANT|author=JEFF LANDA|date=2021-06-04}}</ref>}}"},
                {"name": "Ally Title", "uuid": "f3bf3c15-4e3b-6e58-64a3-8f9995f39370", "description": "特定のコードを入力で入手（2021年）・2022年以降はスキンセットで入手可能<ref name=\"2021 Pride\">{{Cite|url=https://playvalorant.com/ja-jp/news/announcements/show-your-pride-in-valorant/|title=VALORANTでプライドを示そう|website=VALORANT|author=JEFF LANDA|date=2021-06-04}}</ref>}}"},
                {"name": "Proud and Fierce", "uuid": "4ef6afa5-41de-2d89-2bec-adb0feeecfad"}
            ],
            "3bd7465d-4257-8583-c563-188ae47cc7c6": [
                {"name": "Fire-Born Title", "uuid": "47aca56d-49bc-d79f-ba3f-3389899c74ed"},
                {"name": "Flex Title", "uuid": "e68c6e48-4c1e-5144-2ad8-59a32f3ca499"}
            ],
            "a042042c-40f3-df48-dbaa-4bbbd6324ba7": [{"name": "Outlaw Title", "uuid": "e4a373f9-49cd-4645-4b4f-3796303175c3"}], #Throwback Pack: Outlaw

        }
        for uuid,values in addition.items():
            if not uuid in bundles:
                b = API.bundle_by_uuid(uuid)
                b["titles"] = values
                bundles.append(b)

        for bundle in bundles:
            for bundle_playertitle in bundle.get("titles", []):
                for d in playertitles:
                    if bundle_playertitle["uuid"]==d["uuid"]:
                        dictionary[d["uuid"]]["relation"].append("スキンセット")
                        dictionary[d["uuid"]]["bundle"] = API.get_bundle_name(bundle["uuid"])
                        if bundle_playertitle.get("description")!=None:
                            dictionary[d["uuid"]]["description"] = bundle_playertitle["description"]
                        playertitles = API.remove_list_from_uuid(playertitles, d["uuid"])
                        row["Bundle"].append(d["uuid"])

        # prime gaming drops
        for d in API.get_prime_gaming_reward():
            if d["type"]=="playertitles":
                dictionary[d["uuid"]]["relation"].append("Prime Gaming")
                dictionary[d["uuid"]]["description"] = d["date"]
                playertitles = API.remove_list_from_uuid(playertitles, d["uuid"])
                row["Misc"].append(d["uuid"])

        # premier
        premier = [
            # beta
            {
                "uuid": "302f332d-4a9a-1f2c-9331-779b338fdcc7",
                "description": "[[Premier]]（{{Premier|オープンベータ}}）に1試合以上参加する",
                "relation": ["オープンベータ"]
            },
            {
                "uuid": "c3ea6ac6-4dad-98d4-99a3-f7813edbc431",
                "description": "[[Premier]]（{{Premier|オープンベータ}}）で優勝する",
                "relation": ["オープンベータ"]
            },

            #ignition
            {
                "uuid": "c8be8fda-46a8-9843-87bc-ecbf9672c227",
                "description": "[[Premier]]（{{Premier|イグニッション}}）で優勝する",
                "relation": ["イグニッション"]
            },

            # release
            {
                "uuid": "2fbbc891-44cd-b604-e35a-f9ae5436ab76",
                "description": "[[Premier]]（{{Premier|リリース}}）のオープンディビジョンで優勝する",
                "relation": ["リリース", "オープン"]
            },
            {
                "uuid": "58a13ac0-4329-ea83-1235-16905766475d",
                "description": "[[Premier]]（{{Premier|リリース}}）のインターミディエイトディビジョンで優勝する",
                "relation": ["リリース", "インターミディエイト"]
            },
            {
                "uuid": "580557bc-43da-8548-741a-34a0da3785bd",
                "description": "[[Premier]]（{{Premier|リリース}}）のアドバンスドディビジョンで優勝する",
                "relation": ["リリース", "アドバンスド"]
            },
            {
                "uuid": "a235f017-4225-70fa-e5fe-9ca460ce1053",
                "description": "[[Premier]]（{{Premier|リリース}}）のエリートディビジョンで優勝する",
                "relation": ["リリース", "エリート"]
            },
            {
                "uuid": "cb5cce68-434b-7022-e18b-56bb5257b4f8",
                "description": "[[Premier]]（{{Premier|リリース}}）のコンテンダーディビジョンで優勝する",
                "relation": ["リリース", "コンテンダー"]
            },

            # ep7act3
            {
                "uuid": "c2713143-4579-f890-c512-d2ab8caa27be",
                "description": "[[Premier]]（{{Premier|E7A3}}）のオープンディビジョンで優勝する",
                "relation": ["E7A3", "オープン"]
            },
            {
                "uuid": "6c468c03-434f-c305-b947-4e900102a4e2",
                "description": "[[Premier]]（{{Premier|E7A3}}）のインターミディエイトディビジョンで優勝する",
                "relation": ["E7A3", "インターミディエイト"]
            },
            {
                "uuid": "b2446a1e-4e07-b483-662e-4db0ddf23535",
                "description": "[[Premier]]（{{Premier|E7A3}}）のアドバンスドディビジョンで優勝する",
                "relation": ["E7A3", "アドバンスド"]
            },
            {
                "uuid": "f19a9088-49d0-2a25-4256-04b9b16762ba",
                "description": "[[Premier]]（{{Premier|E7A3}}）のエリートディビジョンで優勝する",
                "relation": ["E7A3", "エリート"]
            },
            {
                "uuid": "b8b1c163-4902-719f-cbdc-a09b2ed3a4bc",
                "description": "[[Premier]]（{{Premier|E7A3}}）のコンテンダーディビジョンで優勝する",
                "relation": ["E7A3", "コンテンダー"]
            },
        ]
        for d in premier:
            d["relation"].append("Premier")
            dictionary[d["uuid"]]["relation"] = d["relation"]
            dictionary[d["uuid"]]["description"] = d["description"]
            playertitles = API.remove_list_from_uuid(playertitles, d["uuid"])
            row["Misc"].append(d["uuid"])

        # event winner
        winner = [
            {
                "uuid": "f0751060-4d86-39e8-b881-469f52058b3f", #VCT Regional Masters
                "description": "[[VCT 2021: Stage 1 Masters]]に優勝"
            },
            {
                "uuid": "cd19dad9-4975-7e7d-c511-c6a851589c15", #VCT Masters Reykjavik
                "description": "[[VCT 2021: Stage 2 Masters Reykjavík]]に優勝"
            },
            {
                "uuid": "00031857-43a9-9545-4e05-58ad0a62b79d", #VCT Masters Berlin
                "description": "[[VCT 2021: Stage 3 Masters Berlin]]に優勝"
            },
            {
                "uuid": "1ba98f24-4989-8778-f8a6-b7af353a1625", #2021 VCT Champion
                "description": "[[VCT 2021: Champions Berlin]]に優勝"
            },
            {
                "uuid": "d9c1a80f-4531-8c05-9841-4aafd417df8c", #VCT Masters Reykjavik
                "description": "[[VCT 2022: Stage 1 Masters Reykjavík]]に優勝"
            },
            {
                "uuid": "75aaadc3-427a-e194-e8d0-fd8b76b4540f", #VCT Masters Copenhagen
                "description": "[[VCT 2022: Stage 2 Masters Copenhagen]]に優勝"
            },
            {
                "uuid": "a6d9e243-4046-b025-358e-0087b4b7fcf3", #2022 VCT Champion
                "description": "[[VCT 2022: Champions Istanbul]]に優勝"
            },
            {
                "uuid": "2c4634dd-40bd-052e-bf3c-92a7aca4f084", #2022 Game Changers
                "description": "[[VCT 2022: Game Changers Championship]]に優勝"
            },
            {
                "uuid": "ce6f4f24-402c-d24d-c28c-4db1aa89dc9b", #VCT LOCK//IN
                "description": "[[VCT 2023: LOCK//IN São Paulo]]に優勝"
            },
            {
                "uuid": "cc33f13b-4b66-56da-f80a-e9be7271b163", #VCT Masters Tokyo
                "description": "[[VCT 2023: Masters Tokyo]]に優勝"
            },
            {
                "uuid": "05f48085-4f2a-5726-cf11-dc958e154675", #2023 VCT Champion
                "description": "[[VCT 2023: Champions Los Angeles]]に優勝"
            },
            {
                "uuid": "a5d0a0db-47cf-d1c4-c441-2db1688457c8", #2023 Game Changers
                "description": "[[VCT 2023: Game Changers Championship]]に優勝"
            },
            
        ]
        for d in winner:
            dictionary[d["uuid"]]["relation"].append("大会優勝報酬")
            dictionary[d["uuid"]]["description"] = d["description"]
            playertitles = API.remove_list_from_uuid(playertitles, d["uuid"])
            row["Misc"].append(d["uuid"])

        # misc
        misc = [
            {
                "uuid": "f802662f-7a82-43d9-a626-335d65df08c5", #pioneer
                "description": "特定のコードを入力で入手（ベトナムでのリリース記念）"
            },
            {
                "uuid": "6966d46b-4fd1-3287-fd00-a790c9e7a3d8", #fire
                "description": "[[VCT 2022: Champions Istanbul]]の視聴報酬（2022年8月31日～9月13日）"
            },
            {
                "uuid": "a7d5ae34-4907-072c-13f9-67af86ec737c", #game changer
                "description": "[[VCT 2022: Game Changers Championship]]（2022年11月15日～20日）の視聴報酬"
            },
            {
                "uuid": "d11e42f8-45e9-7d71-720b-8c9c54c3b808", #vct game changer
                "description": "Game Changersに参加した選手やその他の関係者に与えられる"
            },
            {
                "uuid": "08ac32fb-450a-34b8-4aef-d88e50ebd3cb", #clutch
                "description": "[[Red Bull Home Ground 2022]]（2022年12月10日）・[[Red Bull Campus Clutch 2022]]の決勝戦（2022年12月15日）の視聴報酬"
            },
            {
                "uuid": "39a0f753-4a86-9a32-5e1d-7687b13f6e7e", #one 2022
                "description": "[[Riot Games ONE 2022]]（2022年12月23～24日）の来場者特典"
            },
            {
                "uuid": "dd9b86b1-4661-1c98-65ac-c09b70a88e74", #locked in
                "description": "[[VCT 2023: LOCK//IN São Paulo]]（2023年2月14日～3月4日）の視聴報酬"
            },
            {
                "uuid": "af85e868-4c20-2e15-7b2e-51b6721ed93e", #unpredictable
                "description": "[[VCT 2023: Masters Tokyo]]（2023年6月11日～6月25日）の視聴報酬"
            },
            {
                "uuid": "ede4ce31-433f-edff-8bf2-a0b7a99e2193", #louder
                "description": "[[VCT 2023: Game Changers Championship]]の決勝戦（2023年11月29日～12月3日）の視聴報酬"
            },
            {
                "uuid": "e8c04a61-49a8-8d0a-501c-13b26f20110a", #lowrider
                "description": "[[VCT 2023: Champions Los Angeles]]（2023年8月6日～8月23日）の視聴報酬"
            },
            

        ]
        for d in misc:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = d["description"]
            playertitles = API.remove_list_from_uuid(playertitles, d["uuid"])
            row["Misc"].append(d["uuid"])
        
        
        # unused
        for d in playertitles:
            if d["uuid"]!="d13e579c-435e-44d4-cec2-6eae5a3c5ed4":
                dictionary[d["uuid"]]["relation"].append("その他")
                dictionary[d["uuid"]]["description"] = "未使用"
                row["Misc"].append(d["uuid"])

        return dictionary, row

class Contract():
    def get_item_detail(type: str, uuid: str):
        if type=="PlayerCard" or type=="playercards":
            data = API.playercard_by_uuid(uuid)
            return data["displayName"]["ja-JP"], "playercard"
        elif type=="EquippableSkinLevel":
            data = API.skin_by_skinlevel_uuid(uuid)
            return data["displayName"]["ja-JP"], "skin"
        elif type=="skins":
            data = API.skin_by_uuid(uuid)
            return data["displayName"]["ja-JP"], "skin"
        elif type=="Title" or type=="playertitles":
            data = API.playertitle_by_uuid(uuid)
            return data["displayName"]["ja-JP"], "playertitle"
        elif type=="Spray" or type=="sprays":
            data = API.spray_by_uuid(uuid)
            return data["displayName"]["ja-JP"], "spray"
        elif type=="EquippableCharmLevel":
            data = API.buddy_by_charmlevel_uuid(uuid)
            return data["displayName"]["ja-JP"], "buddy"
        elif type=="buddies":
            data = API.buddy_by_uuid(uuid)
            return data["displayName"]["ja-JP"], "buddy"
        elif type=="Currency" or type=="currencies":
            data = API.currency_by_uuid(uuid)
            if uuid=="85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741": #VP
                return "ヴァロラントポイント", "currency"
            elif uuid=="85ca954a-41f2-ce94-9b45-8ca3dd39a00d": #KC
                return "キングダムクレジット", "currency"
            elif uuid=="f08d4ae3-939c-4576-ab26-09ce1f23bb37": #Free Agent
                return "フリーエージェント", "currency"
            elif uuid=="e59aa87c-4cbf-517a-5983-6e81511be9b7": #RP
                return "レディアナイトポイント", "currency"
        elif type=="Agent" or type=="agents":
            data = API.agent_by_uuid(uuid)
            return data["displayName"]["ja-JP"], "agent"

    def make_list_parent(contracts):
        ret: list = []
        
        for contract in contracts:
            dictionary: dict
            if contract["displayName"]["ja-JP"] == "オーメンの契約書":
                contract["displayName"]["ja-JP"]="オーメンのギア"
                contract["displayName"]["en-US"]="Omen Gear"
            
            dictionary = {
                "name": contract["displayName"]["en-US"],
                "localized_name": contract["displayName"]["ja-JP"],
                "uuid": contract["uuid"],
                "start": "",
                "end": "",
                "relation": "",
                "relation_type": "",
            }

            if contract["content"]["relationType"]=="Agent":
                dictionary["relation_type"] = "agent"
                dictionary["relation"] = API.agent_by_uuid(contract["content"]["relationUuid"])["displayName"]["ja-JP"]
            
            elif contract["content"]["relationType"]=="Event":
                dictionary["relation_type"] = "event"
                uuid = contract["content"]["relationUuid"]
                if uuid=="96682481-4f7b-6322-18bb-f1a76f91a35f":
                    dictionary["relation"] = "VCT 2022: Champions Istanbul"
                elif uuid=="024d36a7-46e3-8a29-30c6-09a7fb81bebe":
                    dictionary["relation"] = "旧正月"
                elif uuid=="de4b227a-479a-a885-c2e3-7c9f066b8492":
                    dictionary["relation"] = "VCT 2022: Champions Los Angeles"
                elif uuid=="cee09894-41d6-7000-848b-ea9de6c28f44":
                    dictionary["relation"] = "Arcane"
                
                event = API.event_by_uuid(uuid)
                start = dateutil.parser.parse(event["startTime"]).astimezone(timezone('Asia/Tokyo'))
                end = dateutil.parser.parse(event["endTime"]).astimezone(timezone('Asia/Tokyo'))
                dictionary["start"] = datetime.datetime.strftime(start, "%Y-%m-%d")
                dictionary["end"] = datetime.datetime.strftime(end, "%Y-%m-%d")
            
            elif contract["content"]["relationType"]==None:
                dictionary["relation_type"] = "event"
            
            elif contract["content"]["relationType"]=="Season":
                if contract["uuid"]=="4ef7ddda-4b73-c349-ee84-e8a9794613b5":
                    dictionary["relation_type"] = "event"
                else:
                    dictionary["relation_type"] = "season"

                season = API.season_by_uuid(contract["content"]["relationUuid"])
                start = dateutil.parser.parse(season["startTime"]).astimezone(timezone('Asia/Tokyo'))
                end = dateutil.parser.parse(season["endTime"]).astimezone(timezone('Asia/Tokyo'))
                dictionary["start"] = datetime.datetime.strftime(start, "%Y-%m-%d")
                dictionary["end"] = datetime.datetime.strftime(end, "%Y-%m-%d")
                dictionary["relation"] = FileName.season(contract["content"]["relationUuid"])
            
            ret.append(dictionary)

        return ret
                

    def make_list(contract):
        dictionary: list = []

        if contract["displayName"]["ja-JP"] == "オーメンの契約書":
            contract["displayName"]["ja-JP"]="オーメンのギア"

        # data
        idx = 1

        i = 0
        j = 0
        for chapter in contract["content"]["chapters"]:
            epilogue = chapter["isEpilogue"]
            levels = chapter["levels"]
            free_rewards = chapter["freeRewards"]


            for level in levels:
                tier: int
                if epilogue:
                    j+=1
                    tier = j
                else:
                    i+=1
                    tier = i

                reward = level["reward"] 
                item, tp = Contract.get_item_detail(reward["type"], reward["uuid"])
                amount = reward["amount"]

                if reward["uuid"]=="e59aa87c-4cbf-517a-5983-6e81511be9b7" and tp=="currency":
                    amount *= 10

                vp = 0
                kc = 0
                xp = 0
                if level["isPurchasableWithVP"]:
                    if contract["content"]["relationType"]=="Season" and not epilogue and tier>1:
                        vp = 300
                    else:
                        vp = level["vpCost"]
                if level["isPurchasableWithDough"]:
                    kc = level["doughCost"]
                if contract["content"]["relationType"]!="Agent":
                    xp = level["xp"]
                
                dictionary.append({
                    "idx": str(idx),
                    "name": item,
                    "type": tp,
                    "amount": str(amount),
                    "tier": str(tier),
                    "free": False,
                    "epilogue": epilogue,
                    "xp": str(xp),
                    "vp": str(vp),
                    "kc": str(kc),
                    "contract": contract["displayName"]["ja-JP"]
                })
                idx += 1
            
            if free_rewards!=None:
                for free_reward in free_rewards:
                    item, tp = Contract.get_item_detail(free_reward["type"], free_reward["uuid"])

                    if free_reward["uuid"]=="e59aa87c-4cbf-517a-5983-6e81511be9b7" and tp=="currency":
                        amount *= 10

                    dictionary.append({
                        "idx": str(idx),
                        "name": item,
                        "type": tp,
                        "amount": str(free_reward["amount"]),
                        "tier": str(tier),
                        "free": True,
                        "epilogue": epilogue,
                        "xp": str(0),
                        "vp": str(0),
                        "kc": str(0),
                        "contract": contract["displayName"]["ja-JP"]
                    })
                    idx += 1

        return dictionary

class Season():
    def make_list():
        dictionary: list = []

        seasons = JSON.read("api/seasons.json")
        for season in seasons:
            d = {}
            d["uuid"] = season["uuid"]
            d["page"] = FileName.season(season["uuid"])
            start = dateutil.parser.parse(season["startTime"]).astimezone(timezone('Asia/Tokyo'))
            end = dateutil.parser.parse(season["endTime"]).astimezone(timezone('Asia/Tokyo'))
            d["start"] = datetime.datetime.strftime(start, "%Y-%m-%d")
            d["end"] = datetime.datetime.strftime(end, "%Y-%m-%d")


            if season["uuid"]=="0df5adb9-4dcb-6899-1306-3e9860661dd3":
                d["name"] = "クローズドベータ"
                d["episode"] = "0"
                d["act"] = ""
                d["parent"] = ""
            
            else:
                if season["parentUuid"]==None: #episode
                    episode = int(re.findall("EPISODE (.*)", season["displayName"]["en-US"])[0])
                    d["name"] = f"Episode {episode}"
                    d["episode"] = str(episode)
                    d["act"] = ""
                    d["parent"] = ""

                else: #act
                    season_ep = API.season_by_uuid(season["parentUuid"])
                    episode = int(re.findall("EPISODE (.*)", season_ep["displayName"]["en-US"])[0])
                    act = int(re.findall("ACT (.*)", season["displayName"]["en-US"])[0])
                    d["name"] = f"Episode {episode}: Act {act}"
                    d["episode"] = str(episode)
                    d["act"] = str(act)
                    d["parent"] = f"Episode {episode}"
            dictionary.append(d)
        return dictionary
    
class CompetitiveTier():
    def make_list():
        dictionary: list = []

        tiers = JSON.read("api/competitivetiers.json")[-1]["tiers"]
        for tier in tiers:
            d = {}
            d["tier"] = tier["tier"]
            d["name"] = tier["tierName"]["en-US"]
            d["localized_name"] = tier["tierName"]["ja-JP"]
            d["division_name"] = tier["divisionName"]["en-US"]
            d["localized_division_name"] = tier["divisionName"]["ja-JP"]
            d["image"] = FileName.competitive_tier(tier, "large")
            d["triangle_down"] = FileName.competitive_tier(tier, "rankTriangleDown")
            d["triangle_up"] = FileName.competitive_tier(tier, "rankTriangleUp")

            if d["image"]==None:
                d["image"] = ""
            if d["triangle_down"]==None:
                d["triangle_down"] = ""
            if d["triangle_up"]==None:
                d["triangle_up"] = ""

            dictionary.append(d)
        return dictionary