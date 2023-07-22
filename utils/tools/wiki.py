import os, re, requests
import urllib.error
import urllib.request
import urllib.parse
from utils.tools.json import JSON

class Wiki():
    url: str
    session: requests.Session
    id: str
    password: str

    login_token: str
    csrf_token: str

    def __init__(self, id:str, password: str, url: str) -> None:
        self.url = url
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
        ret = self.session.get(url=self.url, params=LOGIN_TOKEN_PARAMS)
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
        ret = self.session.post(self.url, data=LOGIN_PARAMS)
        data = ret.json()

        if data.get("login", {}).get("result")!="Success":
            raise Exception(data.get("login", {}).get("reason", "Login failed"))

        # CSRF TOKEN
        CSRF_PARAMS = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }
        ret = self.session.get(url=self.url, params=CSRF_PARAMS)
        data = ret.json()

        self.csrf_token = data['query']['tokens']['csrftoken']
    
    def logout(self):
        LOGOUT_PARAMS = {
            "action": "logout",
            "token": self.csrf_token,
            "format": "json"
        }

        ret = self.session.post(self.url, data=LOGOUT_PARAMS)
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

        ret = self.session.post(self.url, data=PAGE_EDIT_PARAMS)
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
 
        ret = self.session.post(self.url, data=PAGE_EDIT_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to edit the page: {page}"))
    
    def delete_page(self, page: str, reason: str):
        PAGE_DELETE_PARAMS = {
            'action': 'delete',
            'title': page.replace(" ", "_"),
            'deletetalk': True,
            'token': self.csrf_token,
            'formatversion': 2,
            'format': 'json'
        }

        if reason!=None:
            PAGE_DELETE_PARAMS["reason"] = reason

        ret = self.session.post(self.url, data=PAGE_DELETE_PARAMS)
        data = ret.json()

        if data.get("error"):
            raise Exception(data.get("error", {}).get("info", f"Failed to delete the page: {page}"))

    
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

        ret = self.session.post(self.url, data=PAGE_DELETE_PARAMS)
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
        ret = self.session.post(self.url, data=PAGE_CHECK_PARAMS)
        data = ret.json()  

        for page in data["query"]["pages"]:
            if page.get("pageid", -1) == -1:
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
        ret = self.session.post(self.url, files=file, data=FILE_UPLOAD_PARAMS)
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

        ret = self.session.post(self.url, data=LIST_PARAMS)
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

class WikiString:
    def wiki_format(string: str) -> str:
        return re.sub('\s+', ' ', string.replace("/", "").replace("?", "").replace(":", "").replace("#", "").strip())
    
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