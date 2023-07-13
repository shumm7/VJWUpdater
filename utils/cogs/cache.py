import tkinter
import tkinter.simpledialog
from tkinter import messagebox
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData
from utils.api import API
from utils.wiki import Wiki

class Cache():
    root: tkinter.Tk
    wiki: Wiki
    force: bool = False

    def __init__(self, root: tkinter.Tk, wiki: Wiki) -> None:
        self.root = root
        self.wiki = wiki
    
    def version_check(self):
        _ftype = "CORE.CACHE.CHECK"
        try:
            result: bool = API.check_version()
            if result:
                Log.print("バージョンチェックが完了しました：最新です", "info", _ftype)
                messagebox.showinfo("バージョンチェック", "取得したデータは最新です。")
            else:
                Log.print("バージョンチェックが完了しました：最新ではありません", "warn", _ftype)
                messagebox.showwarning("バージョンチェック", "取得したデータは最新ではありません。「取得」操作を行って下さい。")

        except FileNotFoundError as e:
            messagebox.showerror("バージョンチェック", "バージョンチェックに失敗しました。「取得」操作を行って下さい。")
            Log.exception(e, "version.json が見つかりませんでした。", _ftype)
        except Exception as e:
            messagebox.showerror("バージョンチェック", "不明なエラーが発生したため、バージョンチェックに失敗しました。")
            Log.exception(e, "バージョンチェックに失敗しました。", _ftype)
        
    def fetch(self):
        _ftype = "CORE.CACHE.FETCH"
        try:
            API.fetch_all()
            messagebox.showinfo("取得", "取得操作が完了しました。")
            Log.print("データの取得が完了しました。", "info", _ftype)
        except Exception as e:
            messagebox.showerror("取得", "不明なエラーが発生したため、データの取得に失敗しました。")
            Log.exception(e, "データの取得に失敗しました。", _ftype)
