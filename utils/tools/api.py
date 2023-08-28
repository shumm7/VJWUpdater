import requests, re, dateutil.parser
from utils.tools.json import JSON

class API:
    def version():
        url = 'https://valorant-api.com/v1/version'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/version.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/version.json")
    
    def agents():
        url = 'https://valorant-api.com/v1/agents?language=all&isPlayableCharacter=true'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/agents.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/agents.json")

    def buddies():
        url = 'https://valorant-api.com/v1/buddies?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/buddies.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/buddies.json")
    
    def bundles():
        # valorant-api.com
        url = 'https://valorant-api.com/v1/bundles?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/bundles.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/bundles.json")

        # api.valtracker.gg
        url = 'https://api.valtracker.gg/v1/bundles'

        resp2 = requests.get(url)
        if resp2.status_code == 200:
            JSON.save("api/bundles2.json", resp2.json()['data'])
        else:
            raise Exception("Failed to fetching: api/bundles2.json")
        
        # misc
        bundles = {}
        for bundle in resp.json()['data']:
            uuid = bundle["uuid"]
            bundles[uuid] = bundle

        for bundle2 in resp2.json()['data']:
            if bundle2["uuid"] in bundles:
                bundle = bundles[bundle2.get('uuid')]
                items = []
                default = {'amount': 1, 'discount': 0}
                for weapon in bundle2['weapons']:
                    items.append({
                        'uuid': weapon['levels'][0]['uuid'],
                        'type': 'EquippableSkinLevel',
                        'price': weapon.get('price'),
                        **default,
                    })
                for buddy in bundle2['buddies']:  #
                    items.append({
                        'uuid': buddy['levels'][0]['uuid'],
                        'type': 'EquippableCharmLevel',
                        'price': buddy.get('price'),
                        **default,
                    })
                for card in bundle2['cards']:  #
                    items.append({
                        'uuid': card['uuid'],
                        'type': 'PlayerCard',
                        'price': card.get('price'),
                        **default,
                    })
                for spray in bundle2['sprays']:
                    items.append({
                        'uuid': spray['uuid'],
                        'type': 'Spray',
                        'price': spray.get('price'),
                        **default,
                    })
                
                bundle['items'] = items
                bundle['price'] = bundle2['price']

        JSON.save("api/dict/bundles.json", bundles)
                    
    def competitivetiers():
        url = 'https://valorant-api.com/v1/competitivetiers?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/competitivetiers.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/competitivetiers.json")
    
    def contracts():
        url = 'https://valorant-api.com/v1/contracts?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/contracts.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/contracts.json")
    
    def currencies():
        url = 'https://valorant-api.com/v1/currencies?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/currencies.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/currencies.json")
    
    def events():
        url = 'https://valorant-api.com/v1/events?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/events.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/events.json")
    
    def gamemodes():
        url = 'https://valorant-api.com/v1/gamemodes?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/gamemodes.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/gamemodes.json")
    
    def gear():
        url = 'https://valorant-api.com/v1/gear?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/gear.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/gear.json")
    
    def levelborders():
        url = 'https://valorant-api.com/v1/levelborders?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/levelborders.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/levelborders.json")
    
    def maps():
        url = 'https://valorant-api.com/v1/maps?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/maps.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/maps.json")
    
    def playercards():
        url = 'https://valorant-api.com/v1/playercards?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/playercards.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/playercards.json")
    
    def playertitles():
        url = 'https://valorant-api.com/v1/playertitles?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/playertitles.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/playertitles.json")
    
    def seasons():
        url = 'https://valorant-api.com/v1/seasons?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/seasons.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/seasons.json")
    
    def sprays():
        url = 'https://valorant-api.com/v1/sprays?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/sprays.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/sprays.json")
    
    def weapons():
        url = 'https://valorant-api.com/v1/weapons?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/weapons.json", resp.json()['data'])
        else:
            raise Exception("Failed to fetching: api/weapons.json")
     
        
    def agent_by_uuid(uuid: str) -> dict:
        agents = JSON.read("api/agents.json")

        for agent in agents:
            if agent["uuid"] == uuid:
                return agent
        return None

    def bundle_by_uuid(uuid: str) -> dict:
        bundles = JSON.read("api/bundles.json")

        for bundle in bundles:
            if bundle["uuid"] == uuid:
                return bundle
        return None

    def buddy_by_uuid(uuid: str) -> dict:
        buddies = JSON.read("api/buddies.json")

        for buddy in buddies:
            if buddy["uuid"]==uuid:
                return buddy
        return None

    def buddy_by_charmlevel_uuid(uuid: str) -> dict:
        buddies = JSON.read("api/buddies.json")

        for buddy in buddies:
            for level in buddy["levels"]:
                if level["uuid"]==uuid:
                    return buddy
        return None
    
    def spray_by_uuid(uuid: str) -> dict:
        sprays = JSON.read("api/sprays.json")

        for spray in sprays:
            if spray["uuid"]==uuid:
                return spray
        return None

    def playercard_by_uuid(uuid: str) -> dict:
        playercards = JSON.read("api/playercards.json")

        for playercard in playercards:
            if playercard["uuid"]==uuid:
                return playercard
        return None

    def playertitle_by_uuid(uuid: str) -> dict:
        playertitles = JSON.read("api/playertitles.json")

        for playertitle in playertitles:
            if playertitle["uuid"]==uuid:
                return playertitle
        return None
    
    def skin_by_skinlevel_uuid(uuid: str) -> dict:
        url = f'https://valorant-api.com/v1/weapons/skinlevels/{uuid}?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()['data']
        else:
            return None
    
    def weapon_by_uuid(uuid: str) -> dict:
        url = f'https://valorant-api.com/v1/weapons/{uuid}?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()['data']
        else:
            return None
    
    def skin_by_uuid(uuid: str) -> dict:
        url = f'https://valorant-api.com/v1/weapons/skins/{uuid}?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()['data']
        else:
            return None
    
    def skin_by_skinchroma_uuid(uuid: str) -> dict:
        url = f'https://valorant-api.com/v1/weapons/skinchromas/{uuid}?language=all'

        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()['data']
        else:
            return None
        

    def type_by_item_type_id(uuid: str) -> str:
        if uuid=="d5f120f8-ff8c-4aac-92ea-f2b5acbe9475":
            return "sprays"
        elif uuid=="3f296c07-64c3-494c-923b-fe692a4fa1bd":
            return "playercards"
        elif uuid=="dd3bf334-87f3-40bd-b043-682a57a8dc3a":
            return "buddies"
        elif uuid=="e7c63390-eda7-46e0-bb7a-a6abdacd2433":
            return "skins"
        elif uuid=="3ad1b2b2-acdb-4524-852f-954a76ddae0a":
            return "variants"
        elif uuid=="01bb38e1-da47-4e6a-9b3d-945fe4655707":
            return "agents"
        elif uuid=="de7caa6b-adf7-4588-bbd1-143831e786c6":
            return "playertitles"
        elif uuid=="f85cb6f7-33e5-4dc8-b609-ec7212301948":
            return "contracts"
        else:
            return ""
    
    def type_id_by_type(type: str) -> str:
        if type=="sprays":
            return "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475"
        elif type=="playercards":
            return "3f296c07-64c3-494c-923b-fe692a4fa1bd"
        elif type=="buddies":
            return "dd3bf334-87f3-40bd-b043-682a57a8dc3a"
        elif type=="skins":
            return "e7c63390-eda7-46e0-bb7a-a6abdacd2433"
        elif type=="variants":
            return "3ad1b2b2-acdb-4524-852f-954a76ddae0a"
        elif type=="agents":
            return "01bb38e1-da47-4e6a-9b3d-945fe4655707"
        elif type=="playertitles":
            return "de7caa6b-adf7-4588-bbd1-143831e786c6"
        elif type=="contracts":
            return "f85cb6f7-33e5-4dc8-b609-ec7212301948"
        else:
            return ""
    
    def entitlements_from_type_id(uuid: str, entitlements: dict) -> list:
        value = []
        try:
            for entitlement in entitlements.get("EntitlementsByTypes", []):
                if entitlement.get("ItemTypeID")==uuid:
                    for item in entitlement.get("Entitlements", []):
                        value.append(item.get("ItemID"))
            return value
        except KeyError:
            return []

    def get_act_list() -> list:
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
    
    def get_eventpass_list() -> list:
        contracts = JSON.read("api/contracts.json")
        events = sorted(JSON.read("api/events.json"), key=lambda x: dateutil.parser.parse(x["startTime"]))
        ret = []

        ret.append("a3dd5293-4b3d-46de-a6d7-4493f0530d9b") #プレイしてエージェントをアンロック
        ret.append("0df5adb9-4dcb-6899-1306-3e9860661dd3") #クローズドベータ報酬

        for event in events:
            for contract in contracts:
                if contract["content"]["relationType"] == "Event" and contract["content"]["relationUuid"]==event["uuid"]:
                    ret.append(contract["uuid"])

        return ret
    
    def get_bundle_name(uuid: str) -> str:
        if uuid=="f7bf90a6-4e39-6c04-c12a-b79c8842359c":
            return "チームエース (スキンセット)|チームエース"
        elif uuid=="b7d754d4-44aa-4663-afc3-84a5cccc3c9d":
            return "オニ (EP6)"
        elif uuid=="f7dcf7e1-485e-0524-ec82-0d97b2c8b40b":
            return "リーヴァー (EP5)"
        elif uuid=="790f52c4-4ed8-9869-fa8b-bf92fc24b441":
            return "イオン (EP5)"
        elif uuid=="338cabdb-473f-1f37-fa35-47a3d994517f":
            return "メイジパンク (EP3)"
        elif uuid=="61215a36-435b-9c3e-73e0-25906a3ffe06":
            return "メイジパンク (EP6)"
        elif uuid=="05e8add9-404d-5d37-8973-9f93f8880e2d":
            return "グリッチポップ (EP2)"
        elif uuid=="ed453815-44aa-4c4d-f3aa-77b4bcf048d7":
            return "RGX 11z Pro (EP4)"
        elif uuid=="bf987f36-4a33-45e4-3c49-1ab9a2502607":
            return "Champions 2021 (スキンセット)|Champions 2021"
        elif uuid=="f99e5b38-48c7-1146-acfa-9baaf773b844":
            return "Champions 2022 (スキンセット)|Champions 2022"
        elif uuid=="90ee89df-40cf-03d3-420f-3d9a1b81d85b":
            return "Champions 2023 (スキンセット)|Champions 2023"
        elif uuid=="2654d506-4d05-e7e9-c996-63ac6fdaf767":
            return "VCT LOCK//IN (スキンセット)|VCT LOCK//IN"
        elif uuid=="a6fa35c6-4205-d5bc-dd65-3b92aeaac412":
            return "ラン・イット・バック 2.0"
        elif uuid=="bcdd8956-4588-f586-fda8-fd991c593449":
            return "ラン・イット・バック (EP5)"
        elif uuid=="9d801e67-4b33-4d99-04b8-aab317819a4e":
            return "ラン・イット・バック (EP6)"
        else:
            return API.bundle_by_uuid(uuid)["displayName"]["ja-JP"]