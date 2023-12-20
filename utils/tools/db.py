import os
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
                "description": "RiotX Arcaneのサイト上で特定のミッションをクリア<ref>{{Cite|title=限定特典「ARCANE ポロ バディー」、「暴走キャノン スプレー」が配布中、「RiotX Arcane」特設サイトのミッション完了でゲット|url=https://www.valorant4jp.com/2021/11/arcane_20.html|website=VALORANT4JP|date=2021-11-20}}</ref>"
            },
            {
                "uuid": "f9bcf120-42b6-6986-2acd-6aa87bab4089",
                "description": "[[VCT 2021: Champions Berlin|Champions 2021]]（2021年12月1日～11日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/champions-items-and-drops-are-coming/|title=CHAMPIONSアイテムと観戦報酬が間もなく登場！|website=VALORANT Esports|quote=あなたのVALORANTアカウントをYouTube、Twitch、AfreecaTV、またはTrovoアカウントにリンクすると、Championsガンバディーやスプレーを含むゲーム内報酬を受け取れます！|date=2021-11-24}}</ref>"
            },
            {
                "uuid": "be8eeab6-43eb-d0b7-7b38-f6bb25ef7547",
                "description": "エイプリルフール（2022年4月1日～9日の間にログイン）<ref>{{Cite|url=https://www.youtube.com/watch?v=8nbvUWiNLaI|title=GO WIDE // 「ワイドジョイ」モード 発表トレーラー - VALORANT|website=YouTube|quote=「芸術の復興 スプレー」は日本時間4月1日21時00分～4月9日15時59分まで入手可能です。|author=VALORANT // JAPAN|date=2022-04-01}}</ref>"
            },
            {
                "uuid": "a7b00f01-49ee-c0c2-a910-4d9ae605dbe1",
                "description": "[[VCT 2022: Champions Istanbul|Champions 2022]]の視聴報酬（2022年9月16～17日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2022/ja-jp|title=CHAMPIONS 2022期間中に試合を観戦＆プレイして、アイテムを獲得しよう|quote=Champions期間中、下記の指定時間にDropsが有効なチャンネルでVALORANTの試合を観戦すれば、報酬を獲得できます。|website=VALORANT Esports|date=2022-08-19}}</ref>"
            },
            {
                "uuid": "6aff01b3-443c-d98c-820e-05852efc075f",
                "description": "[[BLAST Spike Nations 2022]]の決勝戦の視聴報酬（2022年10月16日）<ref>{{Cite|url=https://www.spikenations.gg/drops/|title=Drops|website=Spike Nations|quote=Viewers who tune into BLAST’s broadcast for the finals on the 16th of October will be eligible to earn a unique Shreddy Teddy Spray, exclusively available to viewers of this event!}}</ref>"
            },
            {
                "uuid": "890c4f6d-4794-3d88-617b-1b906c7a8ea6",
                "description": "[[Red Bull Home Ground 2022]]（2022年12月11日）・[[Red Bull Campus Clutch 2022]]の決勝戦（2022年12月16日）の視聴報酬、[[Red Bull Home Ground 2023]]（2023年11月3～5日）のキャンペーン報酬。"
            },
            {
                "uuid": "32df08b6-4d6e-d642-b57c-fc915063418b",
                "description": "エイプリルフール（2023年4月1日～8日の間にログイン）<ref>{{Cite|url=https://www.youtube.com/watch?v=F5ulYOASiAE|title=チェックメイト // 「サイファーの復讐」ゲームモードトレーラー - VALORANT|website=YouTube|quote=日本時間4月1日22時00分～4月8日21時59分までの間にログインして、限定の「俺はここだ」スプレーを手に入れましょう。 |author=VALORANT // JAPAN|date=2023-04-01}}</ref>"
            },
            {
                "uuid": "8080ba65-4089-3487-dcf5-f298be03a470",
                "description": "[[VCT 2023: Champions Los Angeles|Champions 2023]]の視聴報酬（2023年8月17日～26日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2023/|title=CHAMPIONS 2023期間中に試合を観戦＆プレイして、アイテムを獲得しよう|website=VALORANT Esports|author=ANTON “JOKRCANTSPELL” FERRARO|date=2023-07-29}}</ref>"
            },
            {
                "uuid": "41450726-4566-aca7-6b98-8d9fcd9105d7",
                "description": "コミュニティーチャレンジの達成報酬<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1735781786523676765|title=OK、ウィングマン。これからも助けてくれるなら、持ってていいよ。3週目、そして最後のコミュニティーチャレンジが完了しました！ 報酬コード：CC-VLRNT-CCHAL-00003 shop.riotgames.com/ja-jp/redeem/より2023年12月31日まで引き換え可能です。|author=@VALORANTjp|website=X|date=2023-12-16}}</ref>"
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
                "description": "[[Premier]] オープンベータで1試合参加する"
            },
            {
                "uuid": "3f77186a-40a9-7abc-9ac6-5a988d279dad",
                "description": "[[Premier]] オープンベータのプレイオフで勝利する"
            },
            {
                "uuid": "29f89efd-4613-c244-fc54-8fb6da4f88e3",
                "description": "[[Premier]] イグニッションステージで1試合参加する"
            },
            {
                "uuid": "f32449d4-4787-7344-6559-cdb30e63f70c",
                "description": "[[Premier]]で1試合参加する"
            },
            {
                "uuid": "ffeb645c-40e0-2e87-123f-4783a7db4b92",
                "description": "[[Premier]] ({{Act|7|3}})で1試合参加する"
            },
        ]
        for d in premier:
            dictionary[d["uuid"]]["relation"].append("Premier")
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
                "description": "クローズドベータへのアクセス権を入手したプレイヤーに与えられた（2020年6月2日）<ref>{{Cite|url=https://playvalorant.com/ja-jp/news/announcements/valorant-closed-beta-ends-may-28/|title=VALORANTのクローズドベータが5月29日（日本時間）に終了|website=VALORANT|quote=獲得権利があったにもかかわらずクローズドベータのアクセス権を受け取り損ねてしまった方には、限定のTwitch/VALORANTプレイヤーカードをお贈りします。VALORANTが正式リリースされる6月2日に、インベントリーから受け取りが可能になります。|author=CHRIS “PWYFF” TOM|date=2020-05-23}}</ref>"
            },
            {
                "uuid": "e17c2e94-44fb-9486-8497-9dab8b942b3d",
                "description": "[[AfreecaTV Asia Showdown]]の視聴報酬（60分以上）<ref>{{Cite|url=https://playvalorant.com/ko-kr/news/esports/asia-valorant-showdown-announcement/|title=‘아시아 발로란트 쇼다운’ 개막 안내|website=VALORANT|quote=아프리카TV에서 AVS를 시청하시는 분들께 특별한 플레이어 카드를 선물해 드립니다. 보상을 받는 방법은 아래와 같습니다.|date=2020-09-15}}</ref>"
            },
            {
                "uuid": "bb5cedcd-4ed9-ee2e-f129-48bf60a8e540",
                "description": "[[DUALITY]]の公開記念で48時間の限定配布がなされたが、コード交換サイトの接続不具合により2021年6月8日に存在する全アカウントに配布された<ref>{{Cite|url=https://twitter.com/PlayVALORANT/status/1402037655307702274|title=Due to the issues with our code redemption process, we're granting all players the Duality player card! You should see the card appear in your inventory soon. ICYMI, take a look at the Duality cinematic and dive deeper into the lore of VALORANT:|author=@PlayVALORANT|website=Twitter|date=2021-06-08}}</ref>"
            },
            {
                "uuid": "bab9caaa-4913-2704-833e-8c89e2128eb9",
                "description": "2021年6月10日に存在するアカウントに与えられた<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1402762436730572803|title=VALORANTの1周年を記念して、プレイヤーカード「EP 1 // IGNITION」を皆さんにプレゼント🎉 ゲーム内のインベントリをチェックしてみてください。|website=Twitter|author=@VALORANTjp|date=2021-06-10}}</ref>"
            },
            {
                "uuid": "f67a7c8f-4d3f-b76f-2921-478a4da44109",
                "description": "2021年11月24日に存在するアカウントに与えられた（[[VALORANT Champions 2021]]開催記念）<ref>{{Cite|url=https://valorantesports.com/news/champions-items-and-drops-are-coming/|title=CHAMPIONSアイテムと観戦報酬が間もなく登場！|quote=初のChampionsイベントを記念して、VALORANTの全アクティブアカウントに対し、Champions 2021プレイヤーカードが贈られます。|website=VALORANT Esports|author=RILEY YURK|date=2021-11-24}}</ref>"
            },
            {
                "uuid": "68b0c8c2-4158-7b21-658d-b4ae86f137ce",
                "description": "2022年7月14日以降にログイン<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1547234407991222272|title=アルファの脅威が迫っている。ログインして、コミックの表紙がテーマのプレイヤーカードを入手しよう。なお、このカードはオメガアースの厚意により無料です。|website=Twitter|author=@VALORANTjp|date=2022-07-14}}</ref>"
            },
            {
                "uuid": "9e9c4c4a-4d53-6c37-4e48-85b771b9dd4e",
                "description": "2022年8月12日～20日にログイン<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1557834240896614400|title=もっとコミックブックのアイテムが欲しい！そんなあなたに。日本時間8月12日6時00分～8月20日6時00分までの間にログインすると、「戦友たち」プレイヤーカードが無料で手に入ります。|website=Twitter|author=@VALORANTjp|date=2022-08-12}}</ref>"
            },
            {
                "uuid": "c87737f8-44bc-1b71-8424-c18d9cd6336a",
                "description": "[[VALORANT Champions 2022]]の決勝（2022年9月18日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2022/ja-jp|title=CHAMPIONS 2022期間中に試合を観戦＆プレイして、アイテムを獲得しよう|quote=Champions期間中、下記の指定時間にDropsが有効なチャンネルでVALORANTの試合を観戦すれば、報酬を獲得できます。|website=VALORANT Esports|date=2022-08-19}}</ref>"
            },
            {
                "uuid": "6a578461-430d-e0a9-d67e-4c967e0bdf1a",
                "description": "[[Game Changers 2022 Championship]]の決勝（2022年11月21日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/valorant-game-changers-championship-everything-you-need-to-know/ja-jp|title=VALORANT GAME CHANGERS CHAMPIONSHIP ：知っておくべきすべて|quote=日本時間11月21日にグランドファイナルのライブ配信を視聴すると「2022 Game Changers Championship カード」を獲得可能。|website=VALORANT Esports|author=JEN NEALE|date=2022-11-08}}</ref>"
            },
            {
                "uuid": "cb7157ed-4fc7-a5c9-714b-1786ca3949f1",
                "description": "[[Riot Games ONE]]の来場者特典<ref>{{Cite|url=https://twitter.com/RiotGamesJapan/status/1595258348101931008|title=🎁来場者特典・全員 プレイヤーカード「VERSUS // ヨル + フェニックス」 ONE限定タイトル「ONE // 2022」・抽選（一日1,000名様） Riot Games ONE限定VALORANT オリジナルキーリング|website=Twitter|author=@RiotGamesJapan|date=2022-11-23}}</ref>"
            },
            {
                "uuid": "0c196ea1-48ac-97eb-5362-c884937c016f",
                "description": "[[VCT 2023: Masters Tokyo]]の決勝戦の視聴報酬（6月25日）<ref>{{Cite|url=https://valorantesports.com/news/watch-vct-masters-earn-drops|title=VCT MASTERSを観戦してDROPSを獲得しよう|date=2023-06-08|author=ANTON “JOKRCANTSPELL” FERRARO|website=VALORANT Esports}}</ref>"
            },
            {
                "uuid": "01aa3a02-4ab1-0739-83fd-f3b37eba01db",
                "description": "[[VCT 2023: Champions Los Angeles]]の決勝戦の視聴報酬（8月26日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2023|title=CHAMPIONS 2023期間中に試合を観戦＆プレイして、アイテムを獲得しよう|date=2023-07-29|author=ANTON “JOKRCANTSPELL” FERRARO|website=VALORANT Esports}}</ref>"
            },
            {
                "uuid": "c3e4a7e3-48c4-8476-6bf5-39892718e1f2",
                "description": "[[Red Bull Home Ground 2023]]（2023年11月3～5日）の視聴報酬。"
            },
            {
                "uuid": "bf8a808a-48a5-8c66-cc66-39b49049f7b4",
                "description": "2023年11月29日以降にログインすることで入手"
            },
            {
                "uuid": "17712b8a-4555-8b65-2bbe-75a288069420",
                "description": "コミュニティーチャレンジの達成報酬<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1733260166517190697|title=カードは配られた──500,300,100キル達成。プレイヤーカード2種が引き換え可能になりました。 報酬コード：CC-VLRNT-CCHAL-VAL02 shop.riotgames.com/ja-jp/redeem/ より2023年12月31日まで引き換え可能です。|website=X|date=2023-12-09|author=@VALORANTjp}}</ref>"
            },
            {
                "uuid": "260c7a79-4d04-36d5-9b68-a097519459cd",
                "description": "コミュニティーチャレンジの達成報酬<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1733260166517190697|title=カードは配られた──500,300,100キル達成。プレイヤーカード2種が引き換え可能になりました。 報酬コード：CC-VLRNT-CCHAL-VAL02 shop.riotgames.com/ja-jp/redeem/ より2023年12月31日まで引き換え可能です。|website=X|date=2023-12-09|author=@VALORANTjp}}</ref>"
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
                "description": "[[VCT 2022: Game Changers Championship]]の優勝報酬"
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
                "description": "[[Premier]] イグニッションステージで優勝する"
            },

            # release
            {
                "uuid": "d3a6c031-4090-e50e-03a4-b2b4afbf141e",
                "description": "[[Premier]]（リリースステージ）のオープンディビジョンで優勝する"
            },
            {
                "uuid": "8ef76df3-4f31-4a8b-534b-b29be6f68bed",
                "description": "[[Premier]]（リリースステージ）のインターミディエイトディビジョンで優勝する"
            },
            {
                "uuid": "8d6f45c8-4031-7104-6079-1f934c30917e",
                "description": "[[Premier]]（リリースステージ）のアドバンスドディビジョンで優勝する"
            },
            {
                "uuid": "a1bc1340-4884-7eb2-ceeb-aebea6ff5e3b",
                "description": "[[Premier]]（リリースステージ）のエリートディビジョンで優勝する"
            },
            {
                "uuid": "ffde61af-4686-0d77-11c2-9ea357381b87",
                "description": "[[Premier]]（リリースステージ）のコンテンダーディビジョンで優勝する"
            },

            # ep7act3
            {
                "uuid": "46473ed2-4e80-0066-4a0d-a9b7905d93fa",
                "description": "[[Premier]]（{{Act|7|3}}）のオープンディビジョンで優勝する"
            },
            {
                "uuid": "68f6dbbb-422b-428b-9ef0-3d926312e7cb",
                "description": "[[Premier]]（{{Act|7|3}}）のインターミディエイトディビジョンで優勝する"
            },
            {
                "uuid": "b13a445f-4ff4-fd0e-01fa-c786e00e1bdb",
                "description": "[[Premier]]（{{Act|7|3}}）のアドバンスドディビジョンで優勝する"
            },
            {
                "uuid": "a8834ead-4bba-4405-40ec-40b7c7d8d8e4",
                "description": "[[Premier]]（{{Act|7|3}}）のエリートディビジョンで優勝する"
            },
            {
                "uuid": "deed2aa7-4466-4df9-3fd8-edb372871d51",
                "description": "[[Premier]]（{{Act|7|3}}）のコンテンダーディビジョンで優勝する"
            },
        ]
        for d in premier:
            dictionary[d["uuid"]]["relation"].append("Premier")
            dictionary[d["uuid"]]["description"] = d["description"]
            buddies = API.remove_list_from_uuid(buddies, d["uuid"])
            row["Competitive"].append(d["uuid"])

        # misc
        misc = [
            {
                "uuid": "ad508aeb-44b7-46bf-f923-959267483e78",
                "description": "Riot Gamesの社員などから与えられる特別なガンバディー<ref>{{Cite|url=https://support-valorant.riotgames.com/hc/ja/articles/6708651826579-%E3%83%A9%E3%82%A4%E3%82%A2%E3%83%83%E3%83%88-%E3%82%AC%E3%83%B3%E3%83%90%E3%83%87%E3%82%A3%E3%83%BC%E3%81%AE%E5%85%A5%E6%89%8B%E6%96%B9%E6%B3%95|title=ライアット ガンバディーの入手方法|author=DullMoment|website=VALORANT Support|date=2022-07-15}}</ref>"
            },
            {
                "uuid": "d12a80c0-44a0-0549-cc1f-eeb83f7ad248",
                "description": "中東地域でのVALORANTリリース記念<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1326057002322124803|title=中東地域でのVALORANTのリリースを記念して無料のガンバディーをプレゼント カフワカップで一緒にお祝いしましょう|author=@VALORANTjp|website=Twitter|date=2020-11-10}}</ref>"
            },
            {
                "uuid": "e4267845-4725-ff8e-6c71-ae933844565f",
                "description": "{{Patch|1.14}}で[[スノーボールファイト]]をプレイする<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1343361023085064193|title=「スノーブラザーバディー」をゲットできるのは12月29日まで！期間限定モード「スノーボールファイト」をプレイして手に入れるのをお忘れなく|website=Twitter|author=@VALORANTjp|date=2020-12-28}}</ref>"
            },
            {
                "uuid": "9e601160-4679-d2df-261b-56a398248271",
                "description": "[[BLAST Spike Nations 2021]]の視聴報酬（60分以上）"
            },
            {
                "uuid": "237f36ef-40d5-410a-84be-6c896aad6fde",
                "description": "RiotX Arcaneのサイト上で特定のミッションをクリア<ref>{{Cite|title=限定特典「ARCANE ポロ バディー」、「暴走キャノン スプレー」が配布中、「RiotX Arcane」特設サイトのミッション完了でゲット|url=https://www.valorant4jp.com/2021/11/arcane_20.html|website=VALORANT4JP|date=2021-11-20}}</ref>"
            },
            {
                "uuid": "912110cb-4f40-ada7-e338-518244fff9b2",
                "description": "Arcaneプレミアの視聴報酬<ref>{{Cite|url=https://www.riotgames.com/ja/news/welcome-to-riotx-arcane-ja|title=ようこそ、「RiotX Arcane」へ。|quote=11月7日はRiotアカウントをTwitchにリンクして、私たちと一緒に、またはお好きな配信者と一緒にArcaneプレミアを視聴してゲーム内アイテムをゲットしましょう。|website=Riot Games|date=2021-11-01}}</ref>"
            },
            {
                "uuid": "e2e5ab96-4103-8473-14a7-8d8321a3ae6e",
                "description": "[[VALORANT Champions 2021]]の決勝戦（2021年12月12日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/champions-items-and-drops-are-coming/|title=CHAMPIONSアイテムと観戦報酬が間もなく登場！|website=VALORANT Esports|quote=あなたのVALORANTアカウントをYouTube、Twitch、AfreecaTV、またはTrovoアカウントにリンクすると、Championsガンバディーやスプレーを含むゲーム内報酬を受け取れます！|date=2021-11-24}}</ref>"
            },
            {
                "uuid": "ada5f921-4d81-f439-0017-0e86877a02bd",
                "description": "2021年12月15日以降にログイン<ref>{{Cite|url=https://twitter.com/PlayVALORANT/status/1470785666330071045|title=‘Tis the season for giving and we’re ready to start it off right. Get your Exquisitely Wrapped Gun Buddy by logging in to your VALORANT account. It’ll take a bit for us to deliver to everyone’s inventory, but you’ll see it soon.|website=Twitter|author=@PlayVALORANT|date=2021-12-15|}}</ref>"
            },
            {
                "uuid": "c14745d0-4958-26d9-60e6-7c863080fef1",
                "description": "二要素認証を有効化する<ref>{{Cite|title=二要素認証の導入で報酬を獲得|url=https://www.riotgames.com/ja/news/get-rewarded-for-enabling-2fa-ja|website=Riot Games|quote=そして今回、二要素認証を導入していただいた方を対象に、限定のゲーム内報酬をお贈りすることとなりました。これから新たに導入される方、すでに導入済みの方のどちらも対象となります。|date=2022-10-17}}</ref>"
            },
            {
                "uuid": "86e61d30-4f29-ef14-e880-ef89f53eff09",
                "description": "2022年12月中にRiotアカウントとXboxプロフィールをリンクする<ref>{{Cite|url=https://twitter.com/riotgames/status/1600958902253789207|title=We’re coming to #XboxGamePass in 4 days! Starting today, link your Riot account and Xbox profile to prepare for #TheUnlock and for a limited time, get these extra in-game rewards across all titles. 👉 Here’s how https://riot.com/3W3R0KR|website=Twitter|author=@riotgames|date=2022-12-09}}</ref>"
            },
            {
                "uuid": "d2b317f7-4f19-7052-cd50-33a32f210da0",
                "description": "[[VCT 2023: LOCK//IN São Paulo]]の決勝戦（2023年3月4日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/watch-vct-lock-in-earn-drops|title=VCT23 LOCK//INを観戦してDROPSを獲得しよう|quote=3月4日にグランドファイナルの試合をライブ配信で観戦すると獲得できます|website=VALORANT Esports|date=2023-02-08}}</ref>"
            },
            {
                "uuid": "ba57ccb8-4536-1859-22ca-419eeda037d2",
                "description": "[[VCT 2023: Champions Los Angeles]]の現地会場にてVerizonが実施したキャンペーンの報酬"
            },
            {
                "uuid": "8eec6c97-4765-f374-c37e-0e9a9b02eed5",
                "description": "[[VCT 2023: Game Changers Championship]]の決勝戦（2023年12月4日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/watch-and-earn-during-game-changers-championship-2023/|title=GAME CHANGERS CHAMPIONSHIP 2023を観戦して報酬を獲得|website=VALORANT Esports|author=Anton “JokrCantSpell” Ferraro|date=2023-11-28}}</ref>"
            },
            {
                "uuid": "6364afb1-4ae0-3c71-f5a8-89b7f863c14e",
                "description": "コミュニティーチャレンジの達成報酬<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1730647957543022886|title=皆さん全員に“お墨付き”を。「アザラシのお墨付き」ガンバディーが獲得可能になりました！ 報酬コード：CC-VLRNT-CCHAL-00001 shop.riotgames.com/ja-jp/redeem/ より2023年12月31日まで引き換え可能です。|website=X|date=2023-12-02|author=@VALORANTjp}}</ref>"
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
                    dictionary[skin["uuid"]]["level_description"].append("")

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
                        suffix = WikiString.wiki_format(name.splitlines()[1])
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
                {"name": "Proud Title", "uuid": "c70f542b-4880-c65f-485e-ec8ffd055243", "description": "特定のコードを入力で入手（2021年）・2022年以降はスキンセットで入手可能<ref name=\"2021 Pride\">{{Cite|url=https://playvalorant.com/ja-jp/news/announcements/show-your-pride-in-valorant/|title=VALORANTでプライドを示そう|website=VALORANT|author=JEFF LANDA|date=2021-06-04}}</ref>"},
                {"name": "Ally Title", "uuid": "f3bf3c15-4e3b-6e58-64a3-8f9995f39370", "description": "特定のコードを入力で入手（2021年）・2022年以降はスキンセットで入手可能<ref name=\"2021 Pride\">{{Cite|url=https://playvalorant.com/ja-jp/news/announcements/show-your-pride-in-valorant/|title=VALORANTでプライドを示そう|website=VALORANT|author=JEFF LANDA|date=2021-06-04}}</ref>"},
                {"name": "Proud and Fierce", "uuid": "4ef6afa5-41de-2d89-2bec-adb0feeecfad"}
            ],
            "3bd7465d-4257-8583-c563-188ae47cc7c6": [
                {"name": "Fire-Born Title", "uuid": "47aca56d-49bc-d79f-ba3f-3389899c74ed"},
                {"name": "Flex Title", "uuid": "e68c6e48-4c1e-5144-2ad8-59a32f3ca499"}
            ]
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
                "description": "[[Premier]]（オープンベータ）に1試合以上参加する"
            },
            {
                "uuid": "c3ea6ac6-4dad-98d4-99a3-f7813edbc431",
                "description": "[[Premier]]（オープンベータ）で優勝する"
            },

            #ignition
            {
                "uuid": "c8be8fda-46a8-9843-87bc-ecbf9672c227",
                "description": "[[Premier]]（イグニッションステージ）で優勝する"
            },

            # release
            {
                "uuid": "2fbbc891-44cd-b604-e35a-f9ae5436ab76",
                "description": "[[Premier]]（リリースステージ）のオープンディビジョンで優勝する"
            },
            {
                "uuid": "58a13ac0-4329-ea83-1235-16905766475d",
                "description": "[[Premier]]（リリースステージ）のインターミディエイトディビジョンで優勝する"
            },
            {
                "uuid": "580557bc-43da-8548-741a-34a0da3785bd",
                "description": "[[Premier]]（リリースステージ）のアドバンスドディビジョンで優勝する"
            },
            {
                "uuid": "a235f017-4225-70fa-e5fe-9ca460ce1053",
                "description": "[[Premier]]（リリースステージ）のエリートディビジョンで優勝する"
            },
            {
                "uuid": "cb5cce68-434b-7022-e18b-56bb5257b4f8",
                "description": "[[Premier]]（リリースステージ）のコンテンダーディビジョンで優勝する"
            },

            # ep7act3
            {
                "uuid": "c2713143-4579-f890-c512-d2ab8caa27be",
                "description": "[[Premier]]（{{Act|7|3}}）のオープンディビジョンで優勝する"
            },
            {
                "uuid": "6c468c03-434f-c305-b947-4e900102a4e2",
                "description": "[[Premier]]（{{Act|7|3}}）のインターミディエイトディビジョンで優勝する"
            },
            {
                "uuid": "b2446a1e-4e07-b483-662e-4db0ddf23535",
                "description": "[[Premier]]（{{Act|7|3}}）のアドバンスドディビジョンで優勝する"
            },
            {
                "uuid": "f19a9088-49d0-2a25-4256-04b9b16762ba",
                "description": "[[Premier]]（{{Act|7|3}}）のエリートディビジョンで優勝する"
            },
            {
                "uuid": "b8b1c163-4902-719f-cbdc-a09b2ed3a4bc",
                "description": "[[Premier]]（{{Act|7|3}}）のコンテンダーディビジョンで優勝する"
            },
        ]
        for d in premier:
            dictionary[d["uuid"]]["relation"].append("Premier")
            dictionary[d["uuid"]]["description"] = d["description"]
            playertitles = API.remove_list_from_uuid(playertitles, d["uuid"])
            row["Misc"].append(d["uuid"])

        # event winner
        winner = [
            {
                "uuid": "f0751060-4d86-39e8-b881-469f52058b3f", #VCT Regional Masters
                "description": "[[VCT 2021 Stage 1: Masters]]に優勝（[[Acend]]・[[Australs]]・[[Crazy Raccoon]]・[[FUT Esports]]・[[Gambit Esports]]・[[LDM Esports]]・[[Sentinels]]・[[Team Vikings]]・[[Vision Strikers]]・[[X10 Esports]]）"
            },
            {
                "uuid": "cd19dad9-4975-7e7d-c511-c6a851589c15", #VCT Masters Reykjavik
                "description": "[[VCT 2021 Stage 2: Masters Reykjavík]]に優勝（[[Sentinels]]）"
            },
            {
                "uuid": "00031857-43a9-9545-4e05-58ad0a62b79d", #VCT Masters Berlin
                "description": "[[VCT 2021 Stage 3: Masters Berlin]]に優勝（[[Gambit Esports]]）"
            },
            {
                "uuid": "1ba98f24-4989-8778-f8a6-b7af353a1625", #2021 VCT Champion
                "description": "[[VALORANT Champions 2021]]に優勝（[[Acend]]）"
            },
            {
                "uuid": "d9c1a80f-4531-8c05-9841-4aafd417df8c", #VCT Masters Reykjavik
                "description": "[[VCT 2022 Stage 1: Masters Reykjavík]]に優勝（[[OpTic Gaming]]）"
            },
            {
                "uuid": "75aaadc3-427a-e194-e8d0-fd8b76b4540f", #VCT Masters Copenhagen
                "description": "[[VCT 2022 Stage 2: Masters Copenhagen]]に優勝（[[FunPlus Phoenix]]）"
            },
            {
                "uuid": "a6d9e243-4046-b025-358e-0087b4b7fcf3", #2022 VCT Champion
                "description": "[[VALORANT Champions 2022]]に優勝（[[LOUD]]）"
            },
            {
                "uuid": "2c4634dd-40bd-052e-bf3c-92a7aca4f084", #2022 Game Changers
                "description": "[[VCT 2022: Game Changers Championship]]に優勝（[[G2 Gozen]]）"
            },
            {
                "uuid": "ce6f4f24-402c-d24d-c28c-4db1aa89dc9b", #VCT LOCK//IN
                "description": "[[VCT 2023: LOCK//IN São Paulo]]に優勝（[[Fnatic]]）"
            },
            {
                "uuid": "cc33f13b-4b66-56da-f80a-e9be7271b163", #VCT Masters Tokyo
                "description": "[[VCT 2023: Masters Tokyo]]に優勝（[[Fnatic]]）"
            },
            {
                "uuid": "05f48085-4f2a-5726-cf11-dc958e154675", #2023 VCT Champion
                "description": "[[VCT 2023: Champions Los Angeles]]に優勝（[[Evil Geniuses]]）"
            },
            {
                "uuid": "a5d0a0db-47cf-d1c4-c441-2db1688457c8", #2023 Game Changers
                "description": "[[VCT 2023: Game Changers Championship]]に優勝（[[Shopify Rebellion]]）"
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
                "description": "特定のコードを入力で入手（ベトナムでのリリース記念）<ref>{{Cite|url=https://twitter.com/VALORANTjp/status/1379250161008828425|title=本日、ついにVALORANTがベトナムで正式リリースを迎えました。また全プレイヤーを対象に、この日を記念した特別なゲーム内タイトル、「パイオニア」をご用意しています。|website=X|author=@VALORANTjp|date=2021-04-06}}</ref>"
            },
            {
                "uuid": "6966d46b-4fd1-3287-fd00-a790c9e7a3d8", #fire
                "description": "[[VALORANT Champions 2022]]の視聴報酬（2022年8月31日～9月13日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2022/ja-jp|title=CHAMPIONS 2022期間中に試合を観戦＆プレイして、アイテムを獲得しよう|website=VALORANT Esports|quote=Champions期間中、下記の指定時間にDropsが有効なチャンネルでVALORANTの試合を観戦すれば、報酬を獲得できます。|date=2022-08-19}}</ref>"
            },
            {
                "uuid": "a7d5ae34-4907-072c-13f9-67af86ec737c", #game changer
                "description": "[[Game Changers 2022 Championship]]の視聴報酬（2022年11月15日～20日）<ref>{{Cite|url=https://valorantesports.com/news/valorant-game-changers-championship-everything-you-need-to-know/ja-jp|title=VALORANT GAME CHANGERS CHAMPIONSHIP ：知っておくべきすべて|quote=日本時間11月15日～20日に試合のライブ配信を視聴すると「Game Changer タイトル」を獲得可能。|website=VALORANT Esports|author=JEN NEALE|date=2022-11-08}}</ref>"
            },
            {
                "uuid": "d11e42f8-45e9-7d71-720b-8c9c54c3b808", #vct game changer
                "description": "Game Changersに参加した選手やその他の関係者に与えられる"
            },
            {
                "uuid": "08ac32fb-450a-34b8-4aef-d88e50ebd3cb", #clutch
                "description": "[[Red Bull Home Ground]]（2022年12月10日）・[[Red Bull Campus Clutch 2022]]の決勝戦（2022年12月15日）の視聴報酬"
            },
            {
                "uuid": "39a0f753-4a86-9a32-5e1d-7687b13f6e7e", #one 2022
                "description": "[[Riot Games ONE 2022]]の来場者特典<ref>{{Cite|url=https://twitter.com/RiotGamesJapan/status/1595258348101931008|title=🎁来場者特典・全員 プレイヤーカード「VERSUS // ヨル + フェニックス」 ONE限定タイトル「ONE // 2022」・抽選（一日1,000名様） Riot Games ONE限定VALORANT オリジナルキーリング|website=Twitter|author=@RiotGamesJapan|date=2022-11-23}}</ref>"
            },
            {
                "uuid": "dd9b86b1-4661-1c98-65ac-c09b70a88e74", #locked in
                "description": "[[VCT 2023: LOCK//IN São Paulo]]の視聴報酬（2023年2月14日～3月4日）<ref>{{Cite|url=https://valorantesports.com/news/watch-vct-lock-in-earn-drops|title=VCT23 LOCK//INを観戦してDROPSを獲得しよう|quote=2月14日～3月4日に試合をライブ配信で観戦すると獲得できます|website=VALORANT Esports|date=2023-02-08}}</ref>"
            },
            {
                "uuid": "af85e868-4c20-2e15-7b2e-51b6721ed93e", #unpredictable
                "description": "[[VCT 2023: Masters Tokyo]]の視聴報酬（2023年6月11日～6月25日）<ref>{{Cite|url=https://valorantesports.com/news/watch-vct-masters-earn-drops|title=VCT MASTERSを観戦してDROPSを獲得しよう|date=2023-06-08|author=ANTON “JOKRCANTSPELL” FERRARO|website=VALORANT Esports}}</ref>"
            },
            {
                "uuid": "ede4ce31-433f-edff-8bf2-a0b7a99e2193", #louder
                "description": "[[VCT 2023: Game Changers Championship]]の決勝戦（2023年11月29日～12月3日）の視聴報酬<ref>{{Cite|url=https://valorantesports.com/news/watch-and-earn-during-game-changers-championship-2023/|title=GAME CHANGERS CHAMPIONSHIP 2023を観戦して報酬を獲得|website=VALORANT Esports|author=Anton “JokrCantSpell” Ferraro|date=2023-11-28}}</ref>"
            },
            {
                "uuid": "e8c04a61-49a8-8d0a-501c-13b26f20110a", #lowrider
                "description": "[[VCT 2023: Champions Los Angeles]]の視聴報酬（8月6日～8月23日）<ref>{{Cite|url=https://valorantesports.com/news/watch-play-and-earn-during-champions-2023/|title=CHAMPIONS 2023期間中に試合を観戦＆プレイして、アイテムを獲得しよう|date=2023-07-29|author=ANTON “JOKRCANTSPELL” FERRARO|website=VALORANT Esports}}</ref>"
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
