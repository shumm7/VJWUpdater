import os, re, requests
import urllib.error
import urllib.request
import urllib.parse
from utils.tools.json import JSON
from utils.tools.api import API

class Wiki():
    url: str
    session: requests.Session
    id: str
    password: str

    login_token: str
    csrf_token: str

    def __init__(self, id: str, password: str, url: str) -> None:
        self.url = url
        self.api = urllib.parse.urljoin(base=url, url="w/api.php")
        print(self.api)
        self.id = id
        self.password = password
    
    def login(self):
        self.session = requests.Session()

        # LOGIN TOKEN
        LOGIN_TOKEN_PARAMS = {
            'action': "query",
            'meta': "tokens",
            'type': "login",
            'format': "json"
        }
        ret = self.session.get(url=self.api, params=LOGIN_TOKEN_PARAMS)
        data = ret.json()
        self.login_token = data['query']['tokens']['logintoken']
        
        # LOGIN
        LOGIN_PARAMS = {
            'action': "login",
            'lgname': self.id,
            'lgpassword': self.password,
            'lgtoken': self.login_token,
            'format': "json"
        }
        ret = self.session.post(self.api, data=LOGIN_PARAMS)
        data = ret.json()

        if data.get("login", {}).get("result")!="Success":
            raise Exception(data.get("login", {}).get("reason", "Login failed"))

        # CSRF TOKEN
        CSRF_PARAMS = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }
        ret = self.session.get(url=self.api, params=CSRF_PARAMS)
        data = ret.json()

        self.csrf_token = data['query']['tokens']['csrftoken']
    
    def logout(self):
        LOGOUT_PARAMS = {
            "action": "logout",
            "token": self.csrf_token,
            "format": "json"
        }

        ret = self.session.post(self.api, data=LOGOUT_PARAMS)
        data = ret.json()
    
    def create_page(self, page: str, text: str, summary: str ="", content_model: str = 'wikitext', minor: bool=False):
        PAGE_EDIT_PARAMS = {
            'action': 'edit',
            'title': page,
            'text': text,
            'bot': True,
            'minor': minor,
            'summary': summary,
            'createonly': True,
            'contentmodel': content_model,
            'token': self.csrf_token,
            'formatversion': 2,
            'format': 'json'
        }

        ret = self.session.post(self.api, data=PAGE_EDIT_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to create the page: {page}"))
    
    def edit_page(self, page: str, text: str, mode: str = "", summary: str = "", content_model: str = 'wikitext', minor: bool = False, editonly: bool = True):
        PAGE_EDIT_PARAMS = {
            'action': 'edit',
            'title': page.replace(" ", "_"),
            'text': text,
            'bot': True,
            'minor': minor,
            'summary': summary,
            'contentmodel': content_model,
            'token': self.csrf_token,
            'formatversion': 2,
            'format': 'json'
        }

        if editonly:
            PAGE_EDIT_PARAMS["nocreate"] = True

        if mode=="append":
            PAGE_EDIT_PARAMS["appendtext"] = text
        elif mode=="prepend":
            PAGE_EDIT_PARAMS["prependtext"] = text
 
        ret = self.session.post(self.api, data=PAGE_EDIT_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to edit the page: {page}"))
    
    def delete_page(self, page: str, reason: str, deletetalk: bool = False):
        PAGE_DELETE_PARAMS = {
            'action': 'delete',
            'title': page.replace(" ", "_"),
            'token': self.csrf_token,
            'formatversion': 2,
            'format': 'json'
        }
        
        if deletetalk and self.check_talkpage_exist(page):
            PAGE_DELETE_PARAMS["deletetalk"] = deletetalk
        
        if reason!=None:
            PAGE_DELETE_PARAMS["reason"] = reason

        ret = self.session.post(self.api, data=PAGE_DELETE_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to delete the page: {page}"))

    def get_wikitext(self, page: str):
        page = page.replace(" ", "_")
        return requests.get(urllib.parse.urljoin(self.url, f"w/index.php?title={page}&action=raw")).text
    

    def delete_from_pageid(self, pageid: str, reason: str):
        PAGE_DELETE_PARAMS = {
            'action': 'delete',
            'pageid': pageid,
            'deletetalk': True,
            'token': self.csrf_token,
            'formatversion': 2,
            'format': 'json'
        }

        if reason!=None:
            PAGE_DELETE_PARAMS["reason"] = reason

        ret = self.session.post(self.api, data=PAGE_DELETE_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to edit the page: {pageid}"))
    
    def check_exist(self, page: str):
        PAGE_CHECK_PARAMS = {
            "action": "query",
            "format": "json",
            "prop": "info",
            "titles": page.replace(" ", "_"),
            "formatversion": "2"
        }
        ret = self.session.post(self.api, data=PAGE_CHECK_PARAMS)
        data = ret.json()  

        for page in data["query"]["pages"]:
            if page.get("pageid", -1) == -1:
                return False
            else:
                return True
    
    def check_talkpage_exist(self, page: str):
        PAGE_CHECK_PARAMS = {
            "action": "query",
            "format": "json",
            "prop": "info",
            "inprop": "talkid",
            "titles": page.replace(" ", "_"),
            "formatversion": "2"
        }
        ret = self.session.post(self.api, data=PAGE_CHECK_PARAMS)
        data = ret.json()

        for page in data["query"]["pages"]:
            if page.get("talkid", -1) == -1:
                return False
            else:
                return True
    
    def read_chunks(self, file_object, chunk_size=5000):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield 

    def upload(self, filename: str, text: str, file_dir: str, summary: str = ""):
        FILE_UPLOAD_PARAMS = {
            "action": "upload",
            "filename": filename,
            "format": "json",
            "summary": summary,
            "text": text,
            "token": self.csrf_token,
            "ignorewarnings": 1,
            "formatversion": "2"
        }
        file = {'file':(filename, open(file_dir, 'rb'), 'multipart/form-data')}
        ret = self.session.post(self.api, files=file, data=FILE_UPLOAD_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to upload the file: {filename}"))
    
    def pages_in_category(self, category: str):
        LIST_PARAMS = {
            "action": "query",
            "list": "categorymembers",
            "format": "json",
            "cmtitle": category,
            "cmlimit": 5000,
            "cmprop": "ids|title",
            "ignorewarnings": 1,
            "formatversion": "2"
        }

        ret = self.session.post(self.api, data=LIST_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to fetch pages in the specific category \"{category}\""))
        return data
        
    def delete_pages_in_specified_category(self, category: str, reason: str, namespace: int = -1):
        data = self.pages_in_category(category)
        JSON.save("test.json", data)

        if data!=None:
            for value in data.get("query", {}).get("categorymembers", []):
                try:
                    if namespace>=0:
                        if value["ns"]!=namespace:
                            continue
                    
                    page = value["pageid"]
                    self.delete_from_pageid(page, reason)
                finally:
                    continue
        else:
            raise Exception(data.get("error", {}).get("info", f"Failed to delete pages in the specific category \"{category}\""))

    def change_password(self, password: str):
        PAGE_EDIT_PARAMS = {
            'action': 'changeauthenticationdata',
            'changeauthrequest': "MediaWiki\Auth\PasswordAuthenticationRequest",
            'password': password,
            'retype': password,
            'changeauthtoken': self.csrf_token,
            'formatversion': 2,
            'format': 'json'
        }

        ret = self.session.post(self.api, data=PAGE_EDIT_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to change password."))

    def authmanagerinfo(self, request_for: str, amimergerequestfields: bool = False):
        PAGE_EDIT_PARAMS = {
            'action': 'query',
            'meta': 'authmanagerinfo',
            'amirequestsfor': request_for,
            'amimergerequestfields': amimergerequestfields,
            'changeauthtoken': self.csrf_token,
            'formatversion': 2,
            'format': 'json'
        }

        ret = self.session.post(self.api, data=PAGE_EDIT_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to change password."))

    def changecontentmodel(self, page: str, model: str, summary: str = "", bot: bool = True):
        if not model in ["GadgetDefinition", "GeoJSON", "GeoJson", "JsonSchema", "scribunto", "css", "javascript", "json", "sanitized-css", "text", "wikitext"]:
            raise ValueError("Contentmodel must be GadgetDefinition, GeoJSON, GeoJson, JsonSchema, Scribunto, css, javascript, json, sanitized-css, text or wikitext")
        CHANGE_CONTENTMODEL_PARAMS = {
            "action": "changecontentmodel",
            "format": "json",
            "formatversion": "2",
            "title": page,
            "model": model,
            "summary": summary,
            "bot": bot,
            "token": self.csrf_token
        }

        ret = self.session.post(self.api, data=CHANGE_CONTENTMODEL_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to create the page: {page}"))


class WikiString:
    def wiki_format(string: str) -> str:
        return re.sub('\s+', ' ', string.replace("/", "").replace("?", "").replace(":", "").replace("#", "").replace("\r\n", " ").replace("\n", " ").strip())
    
    def wiki_template(template: str, args: dict, div: str = "") -> str:
        ret: str = "{{" + template + div
        for key,value in args.items():
            ret += f"|{key}={value}{div}"
        
        ret += "}}"
        return ret

    def wiki_mklist(ls: list, div: str = "\n") -> str:
        ret: str = ""

        for v in ls:
            if len(ret)!=0:
                ret += div
            ret += v
        return ret

    def html_escape(string: str, chars: list[str] = ['|', '{', '}']):
        for char in chars:
            if len(char)==1:
                string = string.replace(char, f"&#{ord(char)};")
        return string

    def is_url(url: str) -> bool:
        o = urllib.parse.urlparse(url)
        return len(o.scheme) > 0
    
    def remove_url_params(url: str) -> str:
        o = urllib.parse.urlparse(url)
        return f"{o.scheme}://{o.netloc}{o.path}"

class FileName():
    def playercard(data: dict, type: str) -> str:
        name = data.get("displayName", {})["en-US"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
        
        rname = WikiString.wiki_format(name)

        if type=="small":
            return f"{rname} icon.png"
        elif type=="wide":
            return f"{rname} wide.png"
        elif type=="large":
            return f"{rname}.png"
        elif type=="template":
            return "{{Playercard|" + name + "}}"
    
    def spray(data: dict, type: str=None) -> str:
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
        
        rname = WikiString.wiki_format(name)
        if type=="icon":
            return rname + " icon.png"
        elif type=="template":
            return "{{Spray|" + name + "}}"
        else:
            return rname + ".png"

    def buddy(data: dict, type: str=None) -> str:
        name = data.get("displayName", {})["en-US"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
        
        rname = WikiString.wiki_format(name)
        if type=="template":
            return "{{Buddy|" + name + "}}"
        else:
            return rname + ".png"

    def competitive_tier(data: dict, type: str) -> str:
        name = str.title(data.get("tierName", {})["en-US"])
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
        
        name = WikiString.wiki_format(name)

        if type=="large":
            return f"{name}.png"
        elif type=="rankTriangleDown":
            return f"{name} triangle down.png"
        elif type=="rankTriangleUp":
            return f"{name} triangle_up.png"
    
    def agent(data: dict, tp: str, variable: str = None) -> str:
        name = data.get("displayName", {})["en-US"]

        if name==None:
            raise Exception("Failed to get item's name.")
        
        name = WikiString.wiki_format(name)
        if type(variable)==str:
            if variable == "Astral Form / Cosmic Divide":
                variable = "Cosmic Divide"
            variable = WikiString.wiki_format(variable)

        if tp=="icon":
            return f"{name} Icon.png"
        elif tp=="full":
            return f"{name}.png"
        elif tp=="killfeed":
            return f"{name} killfeed.png"
        elif tp=="background":
            return f"{name} Background.png"
        elif tp=="abilities":
            variable = variable.title().replace("'S", "'s")
            return f"{variable} Icon.png"
        elif tp=="voiceLine":
            return f"{name} voiceline {variable} Agent Lockin.wav"
    
    def weapon(data: dict, tp: str, skin_name: str = None, weapon_name: str = None, theme_id: str = "") -> str:
        name: str = data.get("displayName", {})["en-US"]

        if name==None:
            raise Exception("Failed to get item's name.")
        if skin_name == None:
            skin_name = WikiString.wiki_format(data["displayName"]["en-US"])
        else:
            skin_name = WikiString.wiki_format(skin_name)

        suffix = None
        try:
            suffix = WikiString.wiki_format(name.splitlines()[1])
        except IndexError:
            pass
        name: str = WikiString.wiki_format(name)

        if name=="Standard":
            name = skin_name
        if name=="Random Favorite Skin":
            name = f"Random Favorite {weapon_name}"

        if tp=="icon":
            if suffix!=None:
                return f"{skin_name} {suffix}.png"
            else:
                return f"{name}.png"
        elif tp=="video":
            if suffix!=None:
                return f"{skin_name} {suffix}.mp4"
            else:
                return f"{name}.mp4"
        elif tp=="level_video":
            if name==skin_name:
                return f"{name} Level 1.mp4"
            else:
                return f"{name}.mp4"
        elif tp=="swatch":
            bundle = FileName.bundle_from_theme(theme_id, "en-US")

            level = ""
            if "Variant 1" in name:
                level = "Variant 1"
            elif "Variant 2" in name:
                level = "Variant 2"
            elif "Variant 3" in name:
                level = "Variant 3"
            elif "Variant 4" in name:
                level = "Variant 4"
            elif "Variant 5" in name:
                level = "Variant 5"
            else:
                level = "Default"
            
            return WikiString.wiki_format(f"{bundle} Swatch {level}.png")


    def levelborder(data: dict, type: str) -> str:
        name = data["startingLevel"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")

        if type=="levelNumberAppearance":
            return f"Border Lv{name}.png"
        elif type=="smallPlayerCardAppearance":
            return f"Border Card Lv{name}.png"
    
    def bundle_from_theme(uuid: str, lang: str = "en-US"):
        bundle_uuid = API.theme_from_bundle_uuid(uuid)

        if bundle_uuid==None: #no bundle (battlepasas etc..)
            if uuid=="754fbb11-4ade-2419-8fde-618bdcdffb8a": #ハーバーのギア
                return API.contract_by_uuid("5d627650-48ac-5710-5e49-78a41dc28b7b")["displayName"][lang]
            elif uuid=="37c24492-4d62-2a87-f789-bb850eb355c0": #デッドロックのギア
                return API.contract_by_uuid("78f97f6c-4f19-bfcf-e466-a4840c7c9057")["displayName"][lang]
            elif uuid=="4c7d76ad-417a-073b-04e1-0aa282877b0a": #アイソのギア
                return API.contract_by_uuid("26c6e81f-4d62-e55e-24e7-3d8fa37e3b97")["displayName"][lang]
            elif uuid=="d7a96b31-4880-dc84-a022-45bdad450753": #ゲッコーのギア
                return API.contract_by_uuid("cae6ab4a-4b4a-69a0-3c7a-48b17e313f52")["displayName"][lang]
            elif uuid=="f38e6667-4d60-3686-12e8-9d8ab950b9ff": #フェイドのギア
                return API.contract_by_uuid("7ae5ad85-400b-beba-989d-42924ccf39be")["displayName"][lang]
            elif uuid=="3b17210d-408b-e1f0-069b-fd8f6e61e90d": #ブリーチのギア
                return API.contract_by_uuid("bfb8160e-eee0-46b1-a069-16f93adc7328")["displayName"][lang]
            elif uuid=="aeed5cc9-4686-9272-e76a-3a9092b5ce0e": #レイズのギア
                return API.contract_by_uuid("60f9f1f0-2bb7-47f9-85b7-b873a5a1123b")["displayName"][lang]
            elif uuid=="e6cd5596-40b8-7028-4272-a9a1d9376f91": #チェンバーのギア
                return API.contract_by_uuid("ebfd35c7-4d47-11f6-63f3-0398f055d8ab")["displayName"][lang]
            elif uuid=="bbb8bba9-482e-a0b0-c541-799b9f1c40f1": #KAY/Oのギア
                return API.contract_by_uuid("9454d42a-471f-27b9-325c-319a355c34ee")["displayName"][lang]
            elif uuid=="ee89c075-4806-ca65-6436-db92563b1f3e": #スカイのギア
                return API.contract_by_uuid("e7e7c5e1-4e76-22f8-f423-078b33758464")["displayName"][lang]
            elif uuid=="ca77e082-4c08-bf86-2d62-6a8628398615": #サイファーのギア
                return API.contract_by_uuid("2195e89f-20ad-4e37-b46c-cf46a6715dfd")["displayName"][lang]
            elif uuid=="ca77e082-4c08-bf86-2d62-6a8628398615": #ソーヴァのギア
                return API.contract_by_uuid("3051fb18-9240-4bf3-a9f5-eb9ae954cd9d")["displayName"][lang]
            elif uuid=="dfffc0f0-4d14-b358-ab2c-1fa303b5564d": #キルジョイのギア
                return API.contract_by_uuid("9443cbd4-da4d-4395-8152-26a5b269f339")["displayName"][lang]
            elif uuid=="ad7c6d69-421d-6929-561d-3fbbe1fb596b": #ヴァイパーのギア
                return API.contract_by_uuid("f94fc320-a71f-47e3-b062-6798d14f17d6")["displayName"][lang]
            elif uuid=="f1543ca6-4d3b-4663-cd6b-4a940b79f1a1": #フェニックスのギア
                return API.contract_by_uuid("62b5521c-93f6-4178-aadd-043ed25ed21a")["displayName"][lang]
            elif uuid=="749176f4-4159-5eca-8547-f19cb7a009bc": #アストラのギア
                return API.contract_by_uuid("1d40b4b9-4d86-50b7-9f79-3d939e09c661")["displayName"][lang]
            elif uuid=="4c02ab17-4c0e-1b88-10e4-7fac410abfdf": #ブリムストーンのギア
                return API.contract_by_uuid("ace2bb52-de25-45b5-8e11-3dd2088f914d")["displayName"][lang]
            elif uuid=="fd482050-4f20-dd73-c599-2baa7bb83d18": #ネオンのギア
                return API.contract_by_uuid("6336272a-4be9-4b0c-68ef-d79c06e11ca2")["displayName"][lang]
            elif uuid=="2a5c2836-4f75-0a01-089d-eaaf43cc7d14": #レイナのギア
                return API.contract_by_uuid("4c9b0fcf-57cd-4e84-ae5a-ce89e396242f")["displayName"][lang]
            elif uuid=="def525c9-4151-ab71-5a18-c7bff46d4e46": #オーメンのギア
                return API.contract_by_uuid("eb35d061-4eed-4d22-81a3-1491ec892429")["displayName"][lang]
            elif uuid=="897f7222-4eb3-b86c-1093-7d883c36c731": #ジェットのギア
                return API.contract_by_uuid("c9d1c451-12fc-4601-a97c-8258765fb90d")["displayName"][lang]
            elif uuid=="8d1108da-4333-0b91-3a4a-4596fc5eeeb8": #ヨルのギア
                return API.contract_by_uuid("358b6e88-4cbe-0cfb-c313-c290eba0c8bc")["displayName"][lang]
            elif uuid=="c2a38af9-4d9f-010e-47a0-f5b06570c976": # レッドアラート
                return API.skin_by_uuid("41fce834-4c76-a0f4-2cf8-cca3ae879eab")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="f8ca8370-4cdb-67e6-8862-9684ac410148": # サージ
                return API.skin_by_uuid("6cc70eae-4297-91d5-adb9-efa48004da77")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="950c5b23-4a07-d8e9-9622-46b04592f43": # ソングスティール
                return API.skin_by_uuid("10354287-40e9-4087-85c5-aea7289d31f2")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="e8223acc-4d50-f83e-0029-7d9fd9bf9bc1": # クロムデック
                return API.skin_by_uuid("da41a901-493c-80f7-955b-dfa0c69629fd")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="e0652066-4c7f-2229-2921-749b044ffd48": # ハイヴマインド
                return API.skin_by_uuid("3a921c7b-4e8f-8543-bee8-01ba6da86874")["displayName"][lang].replace(API.weapon_by_uuid("42da8ccc-40d5-affc-beec-15aa47b42eda")["displayName"][lang], "").strip()
            elif uuid=="8b26e254-4d7c-7f11-e67e-9e993970d42e": # ヴェンチュリ
                return API.skin_by_uuid("5c0965bc-4860-94a3-a133-b29b08f75051")["displayName"][lang].replace(API.weapon_by_uuid("44d4e95c-4157-0037-81b2-17841bf2e8e3")["displayName"][lang], "").strip()
            elif uuid=="c9fd69be-4bfd-b808-63f1-128cac4b35e5": # ヴェロシティー
                return API.skin_by_uuid("15588213-4d09-344b-c7e1-28af37374c82")["displayName"][lang].replace(API.weapon_by_uuid("42da8ccc-40d5-affc-beec-15aa47b42eda")["displayName"][lang], "").strip()
            elif uuid=="271874eb-491b-eae3-51f8-6f93f93035f9": # .EXE
                return API.skin_by_uuid("67d3e2f7-4b73-7598-0027-63bd9e2e5fcc")["displayName"][lang].replace(API.weapon_by_uuid("1baa85b4-4c70-1284-64bb-6481dfc3bb4e")["displayName"][lang], "").strip()
            elif uuid=="2f21ff86-4db9-1c5b-ff92-4db0218f5fbd": # ハイドロディップ
                return API.skin_by_uuid("8256eb2c-4368-9da8-521f-379c3793dce1")["displayName"][lang].replace(API.weapon_by_uuid("44d4e95c-4157-0037-81b2-17841bf2e8e3")["displayName"][lang], "").strip()
            elif uuid=="0c2487bb-4cf9-78be-1bf1-c696f86b4aab": # プリズム III
                return API.skin_by_uuid("62abf8b2-4511-131d-42c9-81a5efd1b901")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="08d997b3-40c1-780a-5c48-debbafc9b2ab": # プリズム III (Only Axe)
                return API.skin_by_uuid("62abf8b2-4511-131d-42c9-81a5efd1b901")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="ee2ab81e-4f02-0832-121f-1fb1f0f5f016": # セレニティー
                return API.skin_by_uuid("d8314b6c-45fc-fbda-a797-569a24c11bb9")["displayName"][lang].replace(API.weapon_by_uuid("1baa85b4-4c70-1284-64bb-6481dfc3bb4e")["displayName"][lang], "").strip()
            elif uuid=="4b6ce579-4a00-d107-6e45-50a5e77cc526": # キングダム
                return API.skin_by_uuid("e72d72ab-4284-1469-b544-478a811a29a6")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="124b113b-420d-36e5-ad9c-56a36852acc7": # クチュール
                return API.skin_by_uuid("08bfb08f-48cc-2699-2f5c-aabec43dd43a")["displayName"][lang].replace(API.weapon_by_uuid("44d4e95c-4157-0037-81b2-17841bf2e8e3")["displayName"][lang], "").strip()
            elif uuid=="d853570b-4272-eeb1-77c1-ef890e896815": # リブレット
                return API.skin_by_uuid("e552accf-4c90-0221-02c2-889b6fe10d8f")["displayName"][lang].replace(API.weapon_by_uuid("1baa85b4-4c70-1284-64bb-6481dfc3bb4e")["displayName"][lang], "").strip()
            elif uuid=="6ce582d1-4cf9-efc4-078c-169295311f7e": # ポリフォックス
                return API.skin_by_uuid("54337477-4aec-4a68-4673-7c8731639d30")["displayName"][lang].replace(API.weapon_by_uuid("e336c6b8-418d-9340-d77f-7a9e4cfe0702")["displayName"][lang], "").strip()
            elif uuid=="deb5db21-438b-e5a1-2ee7-bc8830ea6a1f": # ポリフロッグ
                return API.skin_by_uuid("91d95358-4a3e-3abc-a251-98826225f18d")["displayName"][lang].replace(API.weapon_by_uuid("e336c6b8-418d-9340-d77f-7a9e4cfe0702")["displayName"][lang], "").strip()
            elif uuid=="f9fb29bd-4592-ee49-0e2a-93a925d7332e": # ライトウェーブ
                return API.skin_by_uuid("f67d4d78-4567-f8ca-010b-18919c49aa05")["displayName"][lang].replace(API.weapon_by_uuid("44d4e95c-4157-0037-81b2-17841bf2e8e3")["displayName"][lang], "").strip()
            elif uuid=="5b8823bc-4419-c40c-7b62-19a3b7affd21": # オリオン
                return API.skin_by_uuid("d02d21e4-4b57-945e-c504-e8af1bdd488c")["displayName"][lang].replace(API.weapon_by_uuid("44d4e95c-4157-0037-81b2-17841bf2e8e3")["displayName"][lang], "").strip()
            elif uuid=="820b86ef-494c-d8f5-604b-07ae66c53c4c": # スキーマ
                return API.skin_by_uuid("0568cd14-42ca-db85-3ac2-c485079bbbf1")["displayName"][lang].replace(API.weapon_by_uuid("e336c6b8-418d-9340-d77f-7a9e4cfe0702")["displayName"][lang], "").strip()
            elif uuid=="ac252b14-4c1d-cee9-22d1-8da59c412ba4": # シルエット
                return API.skin_by_uuid("9977a737-4bb5-8af1-ea9f-e1accc80ab1f")["displayName"][lang].replace(API.weapon_by_uuid("44d4e95c-4157-0037-81b2-17841bf2e8e3")["displayName"][lang], "").strip()
            elif uuid=="0d04f63b-4c0d-88b1-7c99-348bcfcff326": # キャバリエ
                return API.skin_by_uuid("153b2b33-4e6c-fb98-42dd-5a9819649dc7")["displayName"][lang].replace(API.weapon_by_uuid("1baa85b4-4c70-1284-64bb-6481dfc3bb4e")["displayName"][lang], "").strip()
            elif uuid=="ee1e3f3c-4837-2330-5e1f-7ba1a6bb2950": # ファイナルチャンバー
                return API.skin_by_uuid("47d5e54a-48e5-b62a-5cf5-3cb7efc12e90")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="3ee7e544-4203-ab2c-a6f1-07835b437a71": # ウェイファインダー
                return API.skin_by_uuid("e917273f-42d1-3a8d-7c9e-54afd6e5e68d")["displayName"][lang].replace(API.weapon_by_uuid("42da8ccc-40d5-affc-beec-15aa47b42eda")["displayName"][lang], "").strip()
            elif uuid=="a74e644e-415e-5187-e236-659d651ea760": # サンドスウェプト
                return API.skin_by_uuid("43e01e91-44d0-a819-852b-35b71673c648")["displayName"][lang].replace(API.weapon_by_uuid("e336c6b8-418d-9340-d77f-7a9e4cfe0702")["displayName"][lang], "").strip()
            elif uuid=="ad598603-4ea0-0064-b215-359c11e1536d": # デプス
                return API.skin_by_uuid("69addb00-4eb5-eebb-c4c5-2296549cba6f")["displayName"][lang].replace(API.weapon_by_uuid("1baa85b4-4c70-1284-64bb-6481dfc3bb4e")["displayName"][lang], "").strip()
            elif uuid=="204a73d0-480a-87e8-4da9-c49f8461520e": # イグナイト
                return API.bundle_by_uuid("3bd7465d-4257-8583-c563-188ae47cc7c6")["displayName"][lang]
            elif uuid=="98357913-41f1-916f-e250-3091ed1a5661": # RDVR
                return API.theme_by_uuid(uuid)["displayName"][lang].strip()
            elif uuid=="a081d668-4d28-1bf5-c7f8-9592ec8ad7f7": # Bullet
                return None
            elif uuid=="151e1837-47ef-27f5-74c8-d687cea2f1c5": # Closed Beta
                return None
            elif uuid=="c913e306-4823-8abe-8dcc-eca89ee1cec0": # EP1 Coin
                return None
            elif uuid=="1480c950-441e-6548-d4ad-eea4c82f881e": # Crate
                return None
            elif uuid=="1062a169-4ddf-c074-b53c-829cf0da021f": # Kingdom Crate
                return None
            elif uuid=="e2c217ac-46df-20cc-86c0-25b272ab7d3a": # Donut
                return None
            elif uuid=="9d8cefa5-4fd7-7ad0-6639-61ae5728ff0c": # FloatingIsland
                return None
            elif uuid=="ea250fe3-4d6f-7271-0905-a387abc506f4": # Gelato
                return None
            elif uuid=="af536ba4-45b3-c187-c8db-3088ce2a48a4": # LuckyCat
                return None
            elif uuid=="59aa59b4-4aca-2a44-a9d4-a29dc69fdbfa": # Onboarding
                return None
            elif uuid=="12142d3e-4bda-f937-bff4-a786da09fda2": # Pizza
                return None
            elif uuid=="cab8ec80-4a16-4f53-297f-d3b43faf6991": # RadioniteDiamond
                return None
            elif uuid=="1248174a-47ec-70a0-346c-278ab65f6958": # SwissCheese
                return None
            elif uuid=="5ef5c2fe-4db8-ebd7-5e9d-adbfab942dfa": # Toaster
                return None
            elif uuid=="495d492c-435b-2742-202b-9bb1dd30f6b5": # RGX 11z Pro (EP4)
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (EP4)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="f3427ce8-4ad1-9ece-7b37-22befb459dad": # Gaia's Vengeance (EP7)
                if lang=="ja-JP":
                    return API.bundle_by_uuid("e10e00ae-4dcc-3c4a-16f7-7e885314f0d0")["displayName"][lang] + " (EP7)"
                else:
                    return API.bundle_by_uuid("e10e00ae-4dcc-3c4a-16f7-7e885314f0d0")["displayName"][lang]
            elif uuid=="3737b313-45e6-4760-017f-60bc18c765dd": # Glitchpop (EP2)
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (EP2)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="df7fbc2f-4801-df74-7c08-0bb09ce3904c": # Magepunk (EP3)
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (EP3)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="722faa42-47ca-b0f0-65ba-9ba076fe048c": # Magepunk (EP6)
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (EP6)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="c8b4657e-4832-e294-7681-1eb634f6f96a": # Ion (EP5)
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (EP5)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="a547897d-4bd4-7c77-f5e6-55973f0e89ef": # Oni (EP6)
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (EP6)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="7c85c5c1-4a47-eb3f-c81e-4693dd8b2a62": # Sentinels of Light (EP7)
                if lang=="ja-JP":
                    return API.bundle_by_uuid("753739e7-4447-617c-8253-cf8d9d577b58")["displayName"][lang] + " (EP7)"
                else:
                    return API.bundle_by_uuid("753739e7-4447-617c-8253-cf8d9d577b58")["displayName"][lang]
            elif uuid=="42110a3e-4363-50cc-5a1f-e4bc80f97916": # Reaver (EP5)
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (EP5)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="5a629df4-4765-0214-bd40-fbb96542941f": # Standard
                if lang=="ja-JP":
                    return API.skin_by_uuid("24aee897-4cdc-b0fd-e596-1ba90fa6d1b2")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip() + " (スキンセット)"
                else:
                    return API.skin_by_uuid("24aee897-4cdc-b0fd-e596-1ba90fa6d1b2")["displayName"][lang].replace(API.weapon_by_uuid("29a0cfab-485b-f5d5-779a-b59f85e204a8")["displayName"][lang], "").strip()
            elif uuid=="ccf31eeb-429f-52dc-8447-dfb620ef6ffb": # Champions 2021
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (スキンセット)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="362829cc-4fe4-fcda-98e7-0dbdb4b3bea5": # Champions 2022
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (スキンセット)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="64934312-45d4-705f-dcf6-34b253ab1d67": # Champions 2023
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (スキンセット)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="424c4bea-4cd0-85ac-49d2-0db4da1c4835": # VCT LOCK//IN
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (スキンセット)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="a88cafc1-4ff9-5692-5764-2c9140203371": # Arcane
                if lang=="ja-JP":
                    return API.theme_by_uuid(uuid)["displayName"][lang] + " (スキンセット)"
                else:
                    return API.theme_by_uuid(uuid)["displayName"][lang]
            elif uuid=="0d7a5bfb-4850-098e-1821-d989bbfd58a8": # ランダムお気に入りスキン
                return API.skin_by_uuid("3e3ad47a-4383-73f1-4d92-1693059dae8f")["displayName"][lang]
            else:
                return API.theme_by_uuid(uuid)["displayName"][lang]
            

        else: #bundle
            bundle = API.bundle_by_uuid(bundle_uuid)
            if bundle!=None:
                return bundle["displayName"][lang]
            else:
                return None
