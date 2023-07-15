import requests, os
from utils.misc import JSON, Log

class API:
    def version():
        url = 'https://valorant-api.com/v1/version'
        Log.print(f"Fetching Valorant version: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/version.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/version.json", "error", "API")
    
    def agents():
        url = 'https://valorant-api.com/v1/agents?language=all&isPlayableCharacter=true'
        Log.print(f"Fetching agents: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/agents.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/agents.json", "error", "API")

    def buddies():
        url = 'https://valorant-api.com/v1/buddies?language=all'
        Log.print(f"Fetching buddies: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/buddies.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/buddies.json", "error", "API")
    
    def bundles():
        # valorant-api.com
        url = 'https://valorant-api.com/v1/bundles?language=all'
        Log.print(f"Fetching bundles: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/bundles.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/bundles.json", "error", "API")

        # api.valtracker.gg
        url = 'https://api.valtracker.gg/v1/bundles'
        Log.print(f"Fetching bundles2: {url}", "info", "API")

        resp2 = requests.get(url)
        if resp2.status_code == 200:
            JSON.save("api/bundles2.json", resp2.json()['data'])
        else:
            Log.print("Failed to fetching: api/bundles2.json", "error", "API")
        
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
        Log.print(f"Fetching competitivetiers: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/competitivetiers.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/competitivetiers.json", "error", "API")
    
    def contracts():
        url = 'https://valorant-api.com/v1/contracts?language=all'
        Log.print(f"Fetching contracts: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/contracts.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/contracts.json", "error", "API")
    
    def gear():
        url = 'https://valorant-api.com/v1/gear?language=all'
        Log.print(f"Fetching gear: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/gear.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/gear.json", "error", "API")
    
    def levelborders():
        url = 'https://valorant-api.com/v1/levelborders?language=all'
        Log.print(f"Fetching levelborders: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/levelborders.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/levelborders.json", "error", "API")
    
    def maps():
        url = 'https://valorant-api.com/v1/maps?language=all'
        Log.print(f"Fetching maps: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/maps.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/maps.json", "error", "API")
    
    def playercards():
        url = 'https://valorant-api.com/v1/playercards?language=all'
        Log.print(f"Fetching playercards: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/playercards.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/playercards.json", "error", "API")
    
    def playertitles():
        url = 'https://valorant-api.com/v1/playertitles?language=all'
        Log.print(f"Fetching playertitles: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/playertitles.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/playertitles.json", "error", "API")
    
    def seasons():
        url = 'https://valorant-api.com/v1/seasons?language=all'
        Log.print(f"Fetching seasons: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/seasons.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/seasons.json", "error", "API")
    
    def sprays():
        url = 'https://valorant-api.com/v1/sprays?language=all'
        Log.print(f"Fetching sprays: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/sprays.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/sprays.json", "error", "API")
    
    def weapons():
        url = 'https://valorant-api.com/v1/weapons?language=all'
        Log.print(f"Fetching weapons: {url}", "info", "API")

        resp = requests.get(url)
        if resp.status_code == 200:
            JSON.save("api/weapons.json", resp.json()['data'])
        else:
            Log.print("Failed to fetching: api/weapons.json", "error", "API")