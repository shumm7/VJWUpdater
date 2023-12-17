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
        row: list = []

        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/bundles2.json")

        # data
        dictionary = {}
        for d in sprays:
            dictionary[d["uuid"]] = {
                "name": d["displayName"]["en-US"],
                "title": d["displayName"]["ja-JP"],
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
                                row.append(level["reward"]["uuid"])

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
                                row.append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Spray":
                                    dictionary[free_level["uuid"]]["relation"].append("バトルパス")
                                    dictionary[free_level["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    sprays = API.remove_list_from_uuid(sprays, free_level["uuid"])
                                    row.append(free_level["uuid"])
            
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
                                row.append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="Spray":
                                    dictionary[free_level["uuid"]]["relation"].append("イベントパス")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    sprays = API.remove_list_from_uuid(sprays, free_level["uuid"])
                                    row.append(free_level["uuid"])
        
        # bundle
        for bundle in sorted(bundles, key=lambda x: (x["last_seen"] is None, x["last_seen"])):
            if bundle["uuid"]=="2ed936df-4959-acc7-9aca-358d34a50619": #doodle buds
                bundle["sprays"].append({"name": "Doodle Buds // Tactifriends Spray", "uuid": "8f9caa22-4dd6-5649-1007-0bbaf7001c04"})
                bundle["sprays"].append({"name": "Doodle Buds // League of Legends Spray", "uuid": "bbdcf328-4f71-3c0c-7830-568913236d35"})
            elif bundle["uuid"]=="2116a38e-4b71-f169-0d16-ce9289af4bfa": #prime
                bundle["sprays"].append({"name": "Prime Brick Spray", "uuid": "880d5de5-4268-769d-5407-55921ad2db12"})
            elif bundle["uuid"]=="e6032bbf-403e-47e4-8fbc-a1b212d966e7": #imperium
                bundle["sprays"].append({"name": "Imperium Spray", "uuid": "229d49b4-4e8f-cb5a-12c9-39a5ed45e7ed"})
            elif bundle["uuid"]=="3d580e29-435b-8e65-22f4-3c8b8974f5fd": #gaia's ep7
                bundle["sprays"].append({"name": "Gaia's Vengeance, Ep 7 Spray", "uuid": "a418d89e-49af-141e-4edd-de9ec79c34da"})

            for bundle_spray in bundle["sprays"]:
                for spray in sprays:
                    if bundle_spray["uuid"]==spray["uuid"]:
                        dictionary[spray["uuid"]]["relation"].append("スキンセット")
                        dictionary[spray["uuid"]]["bundle"] = API.get_bundle_name(bundle["uuid"])
                        sprays = API.remove_list_from_uuid(sprays, spray["uuid"])
                        row.append(spray["uuid"])
        
        # prime gaming drops
        for d in API.get_prime_gaming_reward():
            if d["type"]=="sprays":
                dictionary[d["uuid"]]["relation"].append("Prime Gaming")
                dictionary[d["uuid"]]["description"] = d["date"]
                sprays = API.remove_list_from_uuid(sprays, d["uuid"])
                row.append(d["uuid"])

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
            }
        ]
        for d in misc:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = d["description"]
            sprays = API.remove_list_from_uuid(sprays, d["uuid"])
            row.append(d["uuid"])
        
        for d in sprays:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = "未使用"
            row.append(d["uuid"])

        #JSON.save("output/lists/sprays.json", dictionary)
        #JSON.save("output/lists/remain_sprays.json", sprays)
        return dictionary, row

class Playercard():
    def make_list():
        playercards = JSON.read("api/playercards.json")
        dictionary: dict = {}
        row: list = []

        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/bundles2.json")

        # data
        dictionary = {}
        for d in playercards:
            dictionary[d["uuid"]] = {
                "name": d["displayName"]["en-US"],
                "title": d["displayName"]["ja-JP"],
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
                                row.append(level["reward"]["uuid"])

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
                                row.append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="PlayerCard":
                                    dictionary[free_level["uuid"]]["relation"].append("バトルパス")
                                    dictionary[free_level["uuid"]]["relation"].append(f"Episode {episode}: Act {act}")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    playercards = API.remove_list_from_uuid(playercards, free_level["uuid"])
                                    row.append(free_level["uuid"])
            
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
                                row.append(level["reward"]["uuid"])

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="PlayerCard":
                                    dictionary[free_level["uuid"]]["relation"].append("イベントパス")
                                    dictionary[free_level["uuid"]]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[free_level["uuid"]]["description"] = "無料報酬"
                                    playercards = API.remove_list_from_uuid(playercards, free_level["uuid"])
                                    row.append(free_level["uuid"])
        
        # bundle
        for bundle in sorted(bundles, key=lambda x: (x["last_seen"] is None, x["last_seen"])):
            if bundle["uuid"]=="e6032bbf-403e-47e4-8fbc-a1b212d966e7": #imperium
                bundle["cards"].append({"name": "Imperium Card", "uuid": "13b0954b-4347-6698-1141-4589e6ef726d"})
            elif bundle["uuid"]=="3d580e29-435b-8e65-22f4-3c8b8974f5fd": #gaia's ep7
                bundle["cards"].append({"name": "Gaia's Vengeance, Ep 7 Card", "uuid": "e6773d10-4a98-1ddf-d2c8-0783708dffb5"})
            elif bundle["uuid"]=="d84cd2bf-42e5-34e8-062f-cba8d2c66fb2": #undercity
                bundle["cards"].append({"name": "Undercity Card", "uuid": "02096add-4c34-b916-af22-50b3791da2f4"})
            elif bundle["uuid"]=="54f8793c-4daa-6e45-bcfd-e9bfc742dc30": #origin
                bundle["cards"].append({"name": "Origin Card", "uuid": "3c930c58-4f56-1a14-6397-c3bd42f31955"})

            for bundle_card in bundle["cards"]:
                for d in playercards:
                    if bundle_card["uuid"]==d["uuid"]:
                        dictionary[d["uuid"]]["relation"].append("スキンセット")
                        dictionary[d["uuid"]]["bundle"] = API.get_bundle_name(bundle["uuid"])
                        playercards = API.remove_list_from_uuid(playercards, d["uuid"])
                        row.append(d["uuid"])
        
        # prime gaming drops
        for d in API.get_prime_gaming_reward():
            if d["type"]=="playercards":
                dictionary[d["uuid"]]["relation"].append("Prime Gaming")
                dictionary[d["uuid"]]["description"] = d["date"]
                playercards = API.remove_list_from_uuid(playercards, d["uuid"])
                row.append(d["uuid"])

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
            row.append(d["uuid"])

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
        ]
        for d in misc:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = d["description"]
            playercards = API.remove_list_from_uuid(playercards, d["uuid"])
            row.append(d["uuid"])
        
        
        # unused
        for d in playercards:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = "未使用"
            row.append(d["uuid"])

        #JSON.save("output/lists/playercards.json", dictionary)
        #JSON.save("output/lists/remain_playercards.json", playercards)
        return dictionary, row

class Buddy():
    def make_list():
        buddies = JSON.read("api/buddies.json")
        dictionary: dict = {}
        row: list = []

        agents = JSON.read("api/agents.json")
        contracts = JSON.read("api/contracts.json")
        bundles = JSON.read("api/bundles2.json")
        competitivetiers = JSON.read("api/competitivetiers.json")[-1]

        # data
        for d in buddies:
            dictionary[d["uuid"]] = {
                "name": d["displayName"]["en-US"],
                "title": d["displayName"]["ja-JP"],
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
                                row.append(uuid)

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
                                row.append(uuid)

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="EquippableCharmLevel":
                                    uuid = API.buddy_by_charmlevel_uuid(free_level["uuid"])["uuid"]
                                    dictionary[uuid]["relation"].append("バトルパス")
                                    dictionary[uuid]["relation"].append(f"Episode {episode}: Act {act}")
                                    dictionary[uuid]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[uuid]["description"] = "無料報酬"
                                    buddies = API.remove_list_from_uuid(buddies, uuid)
                                    row.append(uuid)
            
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
                                row.append(uuid)

                        if chapter["freeRewards"]!=None:
                            for free_level in chapter["freeRewards"]:
                                if free_level["type"]=="EquippableCharmLevel":
                                    uuid = API.buddy_by_charmlevel_uuid(free_level["uuid"])["uuid"]
                                    dictionary[uuid]["relation"].append("イベントパス")
                                    dictionary[uuid]["bundle"] = contract["displayName"]["ja-JP"]
                                    dictionary[uuid]["description"] = "無料報酬"
                                    buddies = API.remove_list_from_uuid(buddies, uuid)
                                    row.append(uuid)
        
        # bundle
        for bundle in sorted(bundles, key=lambda x: (x["last_seen"] is None, x["last_seen"])):
            if bundle["uuid"]=="e6032bbf-403e-47e4-8fbc-a1b212d966e7": #imperium
                bundle["buddies"].append({"name": "Imperium Buddy", "uuid": "8f32610e-48f1-4d6f-46ad-90911845dad3"})
            elif bundle["uuid"]=="3d580e29-435b-8e65-22f4-3c8b8974f5fd": #gaia's ep7
                bundle["buddies"].append({"name": "Gaia's Vengeance, Ep 7 Buddy", "uuid": "6bdc0477-4b5a-94ed-b944-f284de3b4bd8"})
            elif bundle["uuid"]=="f7f37856-4af7-9b0e-08aa-91a5207c0439": #spectrum
                bundle["buddies"].append({"name": "Zedd Buddy", "uuid": "70963a6d-45b7-8fd4-c6aa-62b2155715aa"})


            for bundle_buddy in bundle["buddies"]:
                for d in buddies:
                    if bundle_buddy["uuid"]==d["uuid"]:
                        dictionary[d["uuid"]]["relation"].append("スキンセット")
                        dictionary[d["uuid"]]["bundle"] = API.get_bundle_name(bundle["uuid"])
                        buddies = API.remove_list_from_uuid(buddies, d["uuid"])
                        row.append(d["uuid"])
        
        # prime gaming drops
        for d in API.get_prime_gaming_reward():
            if d["type"]=="buddies":
                dictionary[d["uuid"]]["relation"].append("Prime Gaming")
                dictionary[d["uuid"]]["description"] = d["date"]
                buddies = API.remove_list_from_uuid(buddies, d["uuid"])

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
            row.append(d["uuid"])

        # event winner
        premier = [
            {
                "uuid": "ac306edc-49bd-0f04-0104-afa2ae783b99",
                "description": "[[Premier]] イグニッションステージで優勝する"
            },
            {
                "uuid": "d3a6c031-4090-e50e-03a4-b2b4afbf141e",
                "description": "[[Premier]]（オープンディビジョン）で優勝する"
            },
            {
                "uuid": "8ef76df3-4f31-4a8b-534b-b29be6f68bed",
                "description": "[[Premier]]（インターミディエイトディビジョン）で優勝する"
            },
            {
                "uuid": "8d6f45c8-4031-7104-6079-1f934c30917e",
                "description": "[[Premier]]（アドバンスドディビジョン）で優勝する"
            },
            {
                "uuid": "a1bc1340-4884-7eb2-ceeb-aebea6ff5e3b",
                "description": "[[Premier]]（エリートディビジョン）で優勝する"
            },
            {
                "uuid": "ffde61af-4686-0d77-11c2-9ea357381b87",
                "description": "[[Premier]]（コンテンダーディビジョン）で優勝する"
            },
        ]
        for d in premier:
            dictionary[d["uuid"]]["relation"].append("Premier")
            dictionary[d["uuid"]]["description"] = d["description"]
            buddies = API.remove_list_from_uuid(buddies, d["uuid"])
            row.append(d["uuid"])

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
        ]
        for d in misc:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = d["description"]
            buddies = API.remove_list_from_uuid(buddies, d["uuid"])
            row.append(d["uuid"])
        
        # competitive
        episodes = API.get_episode_list()
        for tier in competitivetiers["tiers"]:
            for i in range(len(episodes)):
                for buddy in buddies:
                    if buddy["displayName"]["en-US"]==f"EP{i+1}: " + tier["divisionName"]["en-US"].capitalize() + f" Buddy":
                        dictionary[buddy["uuid"]]["relation"].append("コンペティティブ")
                        dictionary[buddy["uuid"]]["relation"].append(f"Episode {i+1}")
                        buddies = API.remove_list_from_uuid(buddies, buddy["uuid"])
                        row.append(buddy["uuid"])
        
        # unused
        for d in buddies:
            dictionary[d["uuid"]]["relation"].append("その他")
            dictionary[d["uuid"]]["description"] = "未使用"
            row.append(d["uuid"])

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
                "title": name,
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
    
