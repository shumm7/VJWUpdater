import requests
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