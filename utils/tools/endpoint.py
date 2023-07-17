import requests
import json
from typing import Any, Mapping
from utils.tools.localize import Lang
from utils.tools.config import Config
from utils.tools.json import JSON
from utils.tools.auth import Auth

class Endpoint():
    auth: Auth
    headers: dict
    puuid: str = ""
    region: str = ""
    player: str = ""

    def __init__(self):
        self.auth = Auth()
        auth_data: dict = self.auth.get_auth()

        self.client_platform = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'
        
        if auth_data.get("puuid")!=None:
            self.headers = self.__build_headers(auth_data)

            self.puuid = auth_data["puuid"]
            self.region = auth_data["region"]
            self.player = auth_data["username"]

        self.pd = f"https://pd.{self.region}.a.pvp.net"
        self.shared = f"https://shared.{self.region}.a.pvp.net"
        self.glz = f"https://glz-{self.region}-1.{self.region}.a.pvp.net"

    def fetch(self, url: str, errors: dict = {}) -> dict:
        """fetch data from the api"""
        data = None

        r = requests.get(url, headers=self.headers)

        try:
            data = json.loads(r.text)
        except:  # as no data is set, an exception will be raised later in the method
            pass

        if "httpStatus" not in data:
            return data

        if data["httpStatus"] == 400:
            raise Exception(Lang.value("common.error_message.cookie_expired"))
            # await self.refresh_token()
            # return await self.fetch(endpoint=endpoint, url=url, errors=errors)
    
    def put(self, url: str, data: dict = {}, errors: dict = {}) -> dict:
        """put data to the api"""
        data = data if type(data) is list else json.dumps(data)

        data = None

        r = requests.put(url, headers=self.headers, data=data)
        data = json.loads(r.text)

        if data is not None:
            return data
        else:
            raise Exception(Lang.value("common.error_message.requests_failed"))
    

    def fetch_player_loadout(self) -> Mapping[str, Any]:
        """
        playerLoadoutUpdate
        Get the player's current loadout
        """
        data = self.fetch(url=f'{self.pd}/personalization/v2/players/{self.puuid}/playerloadout')
        return data
    

    def __build_headers(self, data: Mapping) -> Mapping[str, Any]:
        """build headers"""
        headers: dict = {}

        headers['Authorization'] = f'Bearer ' + data["access_token"]
        headers['X-Riot-Entitlements-JWT'] = data["emt"]
        headers['X-Riot-ClientPlatform'] = self.client_platform
        headers['X-Riot-ClientVersion'] = self._get_client_version()
        return headers

    def _get_client_version(self) -> str:
        """Get the client version"""
        r = requests.get('https://valorant-api.com/v1/version')
        data = r.json()['data']
        return f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}"  # return formatted version string

    def _get_valorant_version(self) -> str:
        """Get the valorant version"""
        r = requests.get('https://valorant-api.com/v1/version')
        if r.status != 200:
            return None
        data = r.json()['data']
        return data['version']
