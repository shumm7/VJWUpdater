import os
import urllib.error
import urllib.request
import urllib.parse
import requests
from utils.misc import Log, JSON

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
        Log.append("ログイントークンの取得作業が完了しました: " + str(data))
        
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
        Log.append("Wikiへのログイン作業が完了しました: " + str(data))

        # CSRF TOKEN
        CSRF_PARAMS = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }
        ret = self.session.get(url=self.url, params=CSRF_PARAMS)
        data = ret.json()

        self.csrf_token = data['query']['tokens']['csrftoken']
        Log.append("CSRFトークンの取得作業が完了しました: " + str(data))

        Log.print(f"ログインが完了しました！ {self.url}", "info", "WIKI.LOGIN")
    
    def logout(self):
        LOGOUT_PARAMS = {
            "action": "logout",
            "token": self.csrf_token,
            "format": "json"
        }

        ret = self.session.post(self.url, data=LOGOUT_PARAMS)
        data = ret.json()
        Log.append("Wikiからのログアウト作業が完了しました: " + str(data))
        Log.print(f"ログアウトが完了しました！ {self.url}", "info", "WIKI.LOGOUT")
    
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
            Log.append(f"ページ「{page}」の作成に失敗しました: " + str(data))
            Log.print(f"ページ「{page}」の作成に失敗しました。 ", "info", "WIKI.PAGE", True)
        else:
            Log.append(f"ページ「{page}」の作成が完了しました: " + str(data))
            Log.print(f"ページ「{page}」を作成しました！ ", "info", "WIKI.PAGE", True)
    
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
            Log.append(f"ページ「{page}」の編集に失敗しました: " + str(data))
            Log.print(f"ページ「{page}」の編集に失敗しました。 ", "info", "WIKI.PAGE", True)
        else:
            Log.append(f"ページ「{page}」の編集が完了しました: " + str(data))
            Log.print(f"ページ「{page}」を編集しました！ ", "info", "WIKI.PAGE", True)
    
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
            Log.append(f"ページ「{page}」の削除に失敗しました: " + str(data))
            Log.print(f"ページ「{page}」の削除に失敗しました。 ", "info", "WIKI.PAGE", True)
        else:
            Log.append(f"ページ「{page}」の削除が完了しました: " + str(data))
            Log.print(f"ページ「{page}」を削除しました！ ", "info", "WIKI.PAGE", True)

    
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
            Log.append(f"ページ「{pageid}」の削除に失敗しました: " + str(data))
            Log.print(f"ページ「{pageid}」の削除に失敗しました。 ", "info", "WIKI.PAGE", True)
        else:
            Log.append(f"ページ「{pageid}」の削除が完了しました: " + str(data))
            Log.print(f"ページ「{pageid}」を削除しました！ ", "info", "WIKI.PAGE", True)
    
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
            Log.append(f"「{filename}」のアップロードに失敗しました: " + str(data))
            Log.print(f"「{filename}」のアップロードに失敗しました。 ", "info", "WIKI.UPLOAD", True)
        else:
            Log.append(f"「{filename}」をアップロードしました: " + str(data))
            Log.print(f"「{filename}」をアップロードしました！ ", "info", "WIKI.UPLOAD", True)
    
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
            Log.append(f"「{category}」に含まれるページの取得に失敗しました: " + str(data))
            Log.print(f"「{category}」に含まれるページの取得に失敗しました。 ", "info", "WIKI.LIST.CAT", True)
            return None
        else:
            Log.append(f"「{category}」に含まれるページを取得しました: " + str(data))
            Log.print(f"「{category}」に含まれるページを取得しました！ ", "info", "WIKI.LIST.CAT", True)
            return data
        
    def delete_pages_in_specified_category(self, category: str, reason: str, namespace: int = -1):

        try:
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
                
                Log.append(f"「{category}」に含まれるページを削除しました。")
                Log.print(f"「{category}」に含まれるページを削除しました！ ", "info", "WIKI.LIST.CAT", True)
            else:
                Log.append(f"「{category}」に含まれるページの削除に失敗しました。")
                Log.print(f"「{category}」に含まれるページの削除に失敗しました。 ", "info", "DELETE.CAT", True)
        except Exception as e:
            Log.exception(e, f"「{category}」に含まれるページの削除に失敗しました。 ", "DELETE.CAT")
