# from __future__ import annotations

# Standard
import os
import json
import re
import ssl
import asyncio
import flet as ft
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from utils.tools.json import JSON
from utils.tools.gui import Gui
from utils.tools.localize import Lang

# Third
import aiohttp
import urllib3
from multidict import MultiDict

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _extract_tokens(data: str) -> str:
    """Extract tokens from data"""

    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response


def _extract_tokens_from_uri(url: str) -> Optional[Tuple[str, Any]]:
    try:
        access_token = url.split("access_token=")[1].split("&scope")[0]
        token_id = url.split("id_token=")[1].split("&")[0]
        return access_token, token_id
    except IndexError:
        raise Exception('Cookies Invalid')


# https://developers.cloudflare.com/ssl/ssl-tls/cipher-suites/

FORCED_CIPHERS = [
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-SHA256',
    'ECDHE-RSA-AES128-SHA',
    'ECDHE-RSA-AES256-SHA',
    'ECDHE-ECDSA-AES128-SHA256',
    'ECDHE-ECDSA-AES128-SHA',
    'ECDHE-ECDSA-AES256-SHA',
    'ECDHE+AES128',
    'ECDHE+AES256',
    'ECDHE+3DES',
    'RSA+AES128',
    'RSA+AES256',
    'RSA+3DES',
]


class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.set_ciphers(':'.join(FORCED_CIPHERS))
        super().__init__(*args, **kwargs, cookie_jar=aiohttp.CookieJar(), connector=aiohttp.TCPConnector(ssl=ctx))


class Auth:
    RIOT_CLIENT_USER_AGENT = "RiotClient/60.0.6.4770705.4749685 rso-auth (Windows;10;;Professional, x64)"
    
    def __init__(self) -> None:
        self._headers: Dict = {
            'Content-Type': 'application/json',
            'User-Agent': Auth.RIOT_CLIENT_USER_AGENT,
            'Accept': 'application/json, text/plain, */*',
        }
        self.user_agent = Auth.RIOT_CLIENT_USER_AGENT

        self.locale_code = 'en-US'  # default language
        self.response = {}  # prepare response for local response
    
    def get_auth(self) -> dict:
        if not os.path.exists("auth.json"):
            JSON.save("auth.json", {})
        data = JSON.read("auth.json")
        return data

    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """This function is used to authenticate the user."""
        session = ClientSession()

        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }

        # headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}

        r = await session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=self._headers)

        # prepare cookies for auth request
        cookies = {'cookie': {}}
        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        data = {"type": "auth", "username": username, "password": password, "remember": True}

        async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=self._headers) as r:
            data = await r.json()
            for cookie in r.cookies.items():
                cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        # print('Response Status:', r.status)
        await session.close()

        if data['type'] == 'response':
            expiry_token = datetime.now() + timedelta(hours=1)

            response = _extract_tokens(data)
            access_token = response[0]
            token_id = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies['expiry_token'] = int(datetime.timestamp(expiry_token))

            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}

        elif data['type'] == 'multifactor':

            if r.status == 429:
                raise Exception(Lang.value("common.error_message.busy"))

            WaitFor2FA = {"auth": "2fa", "cookie": cookies}

            if data['multifactor']['method'] == 'email':
                WaitFor2FA['message'] = Lang.value("common.error_message.sent_email").format(email=data['multifactor']['email'])
                return WaitFor2FA

            WaitFor2FA['message'] = Lang.value("common.error_message.2fa_active")
            return WaitFor2FA

        raise Exception(Lang.value("common.error_message.incorrect"))

    async def get_entitlements_token(self, access_token: str) -> Optional[str]:
        """This function is used to get the entitlements token."""
        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
            data = await r.json()

        await session.close()
        try:
            entitlements_token = data['entitlements_token']
        except KeyError:
            raise Exception(Lang.value("common.error_message.cookie_expired"))
        else:
            return entitlements_token

    async def get_userinfo(self, access_token: str) -> Tuple[str, str, str]:
        """This function is used to get the user info."""
        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
            data = await r.json()

        await session.close()
        try:
            puuid = data['sub']
            name = data['acct']['game_name']
            tag = data['acct']['tag_line']
        except KeyError:
            raise Exception(Lang.value("common.error_message.name_key"))
        else:
            return puuid, name, tag

    async def get_region(self, access_token: str, token_id: str) -> str:
        """This function is used to get the region."""
        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        body = {"id_token": token_id}

        async with session.put(
            'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body
        ) as r:
            data = await r.json()

        await session.close()
        try:
            region = data['affinities']['live']
        except KeyError:
            raise Exception(Lang.value("common.error_message.error"))
        else:
            return region

    async def give2facode(self, code: str, cookies: Dict) -> Dict[str, Any]:
        """This function is used to give the 2FA code."""
        session = ClientSession()

        # headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}

        data = {"type": "multifactor", "code": code, "rememberDevice": True}

        async with session.put(
            'https://auth.riotgames.com/api/v1/authorization', headers=self._headers, json=data, cookies=cookies['cookie']
        ) as r:
            data = await r.json()

        await session.close()
        if data['type'] == 'response':
            cookies = {'cookie': {}}
            for cookie in r.cookies.items():
                cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

            uri = data['response']['parameters']['uri']
            access_token, token_id = _extract_tokens_from_uri(uri)

            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}

        return {'auth': 'failed', 'error': Lang.value("common.error_message.2fa_invalid")}

    async def redeem_cookies(self, cookies: Dict) -> Tuple[Dict[str, Any], str, str]:
        """This function is used to redeem the cookies."""
        if isinstance(cookies, str):
            cookies = json.loads(cookies)

        session = ClientSession()

        if 'cookie' in cookies:
            cookies = cookies['cookie']

        async with session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play"
            "-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            cookies=cookies,
            allow_redirects=False,
        ) as r:
            data = await r.text()

        if r.status != 303:
            raise Exception(Lang.value("common.error_message.cookie_expired"))

        old_cookie = cookies.copy()

        new_cookies = {'cookie': old_cookie}
        for cookie in r.cookies.items():
            new_cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        await session.close()

        accessToken, tokenId = _extract_tokens_from_uri(data)
        entitlements_token = await self.get_entitlements_token(accessToken)

        return new_cookies, accessToken, entitlements_token

    async def refresh_token(self) -> Tuple[Dict[str, Any], str, str]:
        auth_data = self.get_auth()

        cookies, access_token, entitlements_token = await self.redeem_cookies(auth_data["cookie"])
        expired_cookie = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))

        auth_data['cookie'] = cookies['cookie']
        auth_data['access_token'] = access_token
        auth_data['emt'] = entitlements_token
        auth_data['expiry_token'] = expired_cookie

        JSON.save("auth.json", auth_data)


class RiotAccount():
    page: ft.Page
    auth: Auth
    login_data: dict

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.auth = Auth()
        self.gui = Gui(page)
    
    async def authenicate(self, data: dict):
        auth_data = data['data']
        cookie = auth_data['cookie']['cookie']
        access_token = auth_data['access_token']
        token_id = auth_data['token_id']

        entitlements_token = await self.auth.get_entitlements_token(access_token)
        puuid, name, tag = await self.auth.get_userinfo(access_token)
        region = await self.auth.get_region(access_token, token_id)
        player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'

        expiry_token = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))

        return dict(
            cookie=cookie,
            access_token=access_token,
            token_id=token_id,
            emt=entitlements_token,
            puuid=puuid,
            username=player_name,
            region=region,
            expiry_token=expiry_token,
        )

    async def login(self, username: str, password: str):
        authenticate = await self.auth.authenticate(username, password)
        if authenticate['auth'] == 'response':
            self.login_data = await self.authenicate(authenticate)
            JSON.save("auth.json", self.login_data)
            self.gui.popup_success(Lang.value("settings.riot.success"), self.login_data["username"])
        elif authenticate['auth'] == '2fa':
            self.gui.popup_notice(authenticate['message'])
            self.twofa = RiotAccount.TwoFa(self.page, authenticate['cookie'])
            self.twofa.show()


    class TwoFa():
        cookies: dict
        field: ft.TextField
        dialog: ft.AlertDialog
        auth: Auth
        auth_data: dict
        login_data: dict

        def __init__(self, page: ft.Page, cookies: dict):
            self.page = page
            self.cookies = cookies
            self.field = ft.TextField(label=Lang.value("settings.riot.2fa"))
            self.auth = Auth()
            self.riot = RiotAccount(page)
            self.gui = Gui(page)

            self.dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(Lang.value("settings.riot.logincode")),
                content=self.field,
                actions_alignment=ft.MainAxisAlignment.END
            )

            def dlg_ok(e):
                code = self.field.value
                if code==None:
                    return
                if not code.isdigit():
                    return

                asyncio.run(self.auth_2fa(code, self.cookies))
            
            def dlg_cancel(e):
                self.dialog.open = False
                try:
                    self.page.update()
                except Exception as e:
                    pass

            self.dialog.actions=[
                ft.TextButton(Lang.value("common.cancel"), on_click=dlg_cancel),
                ft.TextButton(Lang.value("common.ok"), on_click=dlg_ok)
            ]

        async def auth_2fa(self, code, cookie):
            self.auth_data = await self.auth.give2facode(code, cookie)

            if self.auth_data['auth'] == 'response':
                self.login_data = await self.riot.authenicate(self.auth_data)
                JSON.save("auth.json", self.login_data)
                self.gui.popup_success(Lang.value("settings.riot.success"), self.login_data["username"])

            elif self.auth_data['auth'] == 'failed':
                self.gui.popup_error(Lang.value("settings.riot.failed"), self.auth_data['error'])
            
            self.dialog.open = False
            try:
                self.page.update()
            except Exception as e:
                pass
        
        def show(self):
            self.page.dialog = self.dialog
            self.dialog.open = True
            try:
                self.page.update()
            except Exception as e:
                pass
        

