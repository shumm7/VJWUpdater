import tkinter, os, datetime, math
import tkinter.simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData
from utils.api import API
from utils.wiki import Wiki

class Update():
    root: tkinter.Tk
    wiki: Wiki
    force: bool

    def __init__(self, root: tkinter.Tk, wiki: Wiki, force: bool = False) -> None:
        self.root = root
        self.wiki = wiki
        self.force = force
    
    def playercards(self):
        _ftype = "CORE.UPDATE.CARD"
        try:
            data = JSON.read("api/playercards.json")
            for cat in ["small", "wide", "large"]:
                os.makedirs(f"output/playercards/{cat}", exist_ok=True)
            self.wiki.login()

            max = len(data)
            count = 1
            result = {
                "start": str(datetime.datetime.now()),
                "end": str(datetime.datetime.now()),
                "small": {
                    "exists": [],
                    "skipped": [],
                    "updated": [],
                    "error": []
                },
                "wide": {
                    "exists": [],
                    "skipped": [],
                    "updated": [],
                    "error": []
                },
                "large": {
                    "exists": [],
                    "skipped": [],
                    "updated": [],
                    "error": []
                }
            }

            for value in data:
                progress = f"({count}/{max})"
                try:
                    # set filename
                    name = value.get("displayName", {})["en-US"]
                    name_en: str
                    name_jp: str

                    name_en = String.wiki_format(value.get("displayName", {})["en-US"])
                    name_jp = String.wiki_format(value.get("displayName", {})["ja-JP"])

                    try:
                        for cat in ["small", "wide", "large"]:
                            fn_ext = {"small": " icon", "wide": " wide", "large": ""}
                            filename = f"{name_en}{fn_ext[cat]}.png"

                            # update check
                            img_exist = os.path.exists(f"output/playercards/{cat}/{filename}")
                            exist: bool
                            if self.force:
                                exist = self.wiki.check_exist("File:" + filename)
                            else:
                                if img_exist:
                                    exist = True
                                else:
                                    exist = self.wiki.check_exist("File:" + filename)

                            # get icon url
                            icon: str = None
                            if value.get(f"{cat}Art")!=None:
                                icon = value.get(f"{cat}Art")
                            elif cat=="small" and value.get(f"smallArt")==None:
                                icon = value.get("displayIcon")
                            else:
                                Log.print(f"{name_jp} はスキップされました ({cat}Art が見つかりません)", "warn", _ftype)
                                result[cat]["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                                continue


                            if not exist:
                                if icon!=None:
                                    if not(img_exist) or self.force:
                                        Fetch.download(icon, f"output/playercards/{cat}/{filename}")
                                    category = {"small": "プレイヤーカードのアイコン", "wide": "プレイヤーカードのバナー", "large": "プレイヤーカード"}
                                    fd = filename.replace(" ", "_")
                                    self.wiki.upload(fd, "[[Category:" + category[cat] +"]]\n\n{{License Riot Games}}", f"output/playercards/{cat}/{filename}")
                                    Log.print(f"{name_jp} ({cat}) はアップロードされました {progress}", "info", _ftype)
                                    result[cat]["updated"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                                else:
                                    Log.print(f"{name_jp} ({cat}) はスキップされました ({cat}Art が見つかりません) {progress}", "warn", _ftype)
                                    result[cat]["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                                    continue
                                
                            else:
                                if not(img_exist) or self.force:
                                    Fetch.download(icon, f"output/playercards/{cat}/{filename}")
                                Log.print(f"{name_jp} ({cat}) はスキップされました (既にアップロードされています) {progress}", "info", _ftype)
                                result[cat]["exists"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        
                    except Exception as e:
                        Log.exception(e, value.get("uuid", "") +f" ({cat}) で例外が発生しました。", _ftype)
                        result[cat]["error"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        continue

                except Exception as e:
                    Log.exception(e, value.get("uuid", "")+" で例外が発生しました。", _ftype)
                    for cat in ["small", "wide", "large"]:
                        result[cat]["error"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                    continue
                
                finally:
                    count+=1



            messagebox.showinfo("プレイヤーカード (更新)", "プレイヤーカードの更新確認が完了しました。")
            result["end"] = str(datetime.datetime.now())
            JSON.save("output/playercards/result.json", result)
            self.wiki.logout()

        except Exception as e:
            messagebox.showerror("プレイヤーカード (更新)", "不明なエラーが発生したため、更新確認に失敗しました。")
            Log.exception(e, "プレイヤーカードの更新確認に失敗しました。", _ftype)
    
    def sprays(self):
        _ftype = "CORE.UPDATE.SPRAY"
        try:
            data = JSON.read("api/sprays.json")
            os.makedirs("output/sprays", exist_ok=True)
            self.wiki.login()

            max = len(data)
            count = 1
            result = {
                "start": str(datetime.datetime.now()),
                "end": str(datetime.datetime.now()),
                "exists": [],
                "skipped": [],
                "updated": [],
                "error": []
            }

            for value in data:
                progress = f"({count}/{max})"
                try:
                    # set filename
                    name = value.get("displayName", {})["en-US"]
                    name_en: str
                    name_jp: str
                    if name == "¯\\_(ツ)_/¯ Spray":
                        name_en = "¯＼＼ (ツ) ／¯ Spray"
                        name_jp = "¯＼＼ (ツ) ／¯ スプレー"
                    elif name == "<3 Spray":
                        name_en = "＜3 Spray"
                        name_jp = "＜3 スプレー"
                    elif name == "Love > Hate Spray":
                        name_en = "Love ＞ Hate Spray"
                        name_jp = "愛は憎しみに勝る スプレー"
                    else:
                        name_en = String.wiki_format(value.get("displayName", {})["en-US"])
                        name_jp = String.wiki_format(value.get("displayName", {})["ja-JP"])
                    filename = f"{name_en}.png"

                    # update check
                    img_exist: bool = os.path.exists(f"output/sprays/{filename}")
                    exist: bool
                    if self.force:
                        exist = self.wiki.check_exist("File:" + filename)
                    else:
                        if img_exist:
                            exist = True
                        else:
                            exist = self.wiki.check_exist("File:" + filename)
                    
                    # get icon url
                    icon: str = None
                    if value.get("animationPng")!=None:
                        icon = value.get("animationPng")
                    elif value.get("fullTransparentIcon")!=None:
                        icon = value.get("fullTransparentIcon")
                    elif value.get("fullIcon")!=None:
                        icon = value.get("fullIcon")
                    else:
                        Log.print(f"{name_jp} はスキップされました (fullIcon が見つかりません)", "warn", _ftype)
                        result["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        continue

                    if not exist:
                        if icon!=None:
                            if not(img_exist) or self.force:
                                Fetch.download(icon, f"output/sprays/{filename}")
                                
                            fd = filename.replace(" ", "_")
                            self.wiki.upload(fd, "[[Category:スプレー]]\n\n{{License Riot Games}}", f"output/sprays/{filename}")
                            Log.print(f"{name_jp} はアップロードされました {progress}", "info", _ftype)
                            result["updated"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        else:
                            Log.print(f"{name_jp} はスキップされました (fullIcon が見つかりません) {progress}", "warn", _ftype)
                            result["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                            continue
                        
                    else:
                        if not(img_exist) or self.force:
                            Fetch.download(icon, f"output/sprays/{filename}")
                        Log.print(f"{name_jp} はスキップされました (既にアップロードされています) {progress}", "info", _ftype)
                        result["exists"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                    
                except Exception as e:
                    Log.exception(e, value.get("uuid", "") + "で例外が発生しました。", _ftype)
                    result["error"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                    continue
                
                finally:
                    count+=1



            messagebox.showinfo("スプレー (更新)", "スプレーの更新確認が完了しました。")
            result["end"] = str(datetime.datetime.now())
            JSON.save("output/sprays/result.json", result)
            self.wiki.logout()

        except Exception as e:
            messagebox.showerror("スプレー (更新)", "不明なエラーが発生したため、更新確認に失敗しました。")
            Log.exception(e, "スプレーの更新確認に失敗しました。", _ftype)
    
    def buddies(self):
        _ftype = "CORE.UPDATE.BUDDY"
        try:
            data = JSON.read("api/buddies.json")
            os.makedirs("output/buddies", exist_ok=True)
            self.wiki.login()

            max = len(data)
            count = 1
            result = {
                "start": str(datetime.datetime.now()),
                "end": str(datetime.datetime.now()),
                "exists": [],
                "skipped": [],
                "updated": [],
                "error": []
            }

            for value in data:
                progress = f"({count}/{max})"
                try:
                    # set filename
                    name = value.get("displayName", {})["en-US"]
                    name_en: str
                    name_jp: str

                    name_en = String.wiki_format(value.get("displayName", {})["en-US"])
                    name_jp = String.wiki_format(value.get("displayName", {})["ja-JP"])
                    filename = f"{name_en}.png"

                    # update check
                    img_exist: bool = os.path.exists(f"output/buddies/{filename}")
                    exist: bool
                    if self.force:
                        exist = self.wiki.check_exist("File:" + filename)
                    else:
                        if img_exist:
                            exist = True
                        else:
                            exist = self.wiki.check_exist("File:" + filename)
                    
                    # get icon url
                    icon: str = None
                    if value.get("displayIcon")!=None:
                        icon = value.get("displayIcon")
                    else:
                        Log.print(f"{name_jp} はスキップされました (displayIcon が見つかりません)", "warn", _ftype)
                        result["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        continue

                    if not exist:
                        if icon!=None:
                            if not(img_exist) or self.force:
                                Fetch.download(icon, f"output/buddies/{filename}")
                                
                            fd = filename.replace(" ", "_")
                            self.wiki.upload(fd, "[[Category:ガンバディー]]\n\n{{License Riot Games}}", f"output/buddies/{filename}")
                            Log.print(f"{name_jp} はアップロードされました {progress}", "info", _ftype)
                            result["updated"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        else:
                            Log.print(f"{name_jp} はスキップされました (displayIcon が見つかりません) {progress}", "warn", _ftype)
                            result["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                            continue
                        
                    else:
                        if not(img_exist) or self.force:
                            Fetch.download(icon, f"output/buddies/{filename}")
                        Log.print(f"{name_jp} はスキップされました (既にアップロードされています) {progress}", "info", _ftype)
                        result["exists"].append({"file": filename, "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                    
                except Exception as e:
                    Log.exception(e, value.get("uuid", "") + " で例外が発生しました。", _ftype)
                    result["error"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                    continue
                
                finally:
                    count+=1



            messagebox.showinfo("ガンバディー (更新)", "ガンバディーの更新確認が完了しました。")
            result["end"] = str(datetime.datetime.now())
            JSON.save("output/buddies/result.json", result)
            self.wiki.logout()

        except Exception as e:
            messagebox.showerror("ガンバディー (更新)", "不明なエラーが発生したため、更新確認に失敗しました。")
            Log.exception(e, "ガンバディーの更新確認に失敗しました。", _ftype)

    def competitivetiers(self):
        _ftype = "CORE.UPDATE.RANK"
        try:
            data = JSON.read("api/competitivetiers.json")[-1]["tiers"]
            os.makedirs("output/competitivetiers", exist_ok=True)
            self.wiki.login()

            max = len(data)
            count = 1
            result = {
                "start": str(datetime.datetime.now()),
                "end": str(datetime.datetime.now()),
                "exists": [],
                "skipped": [],
                "updated": [],
                "error": []
            }

            for value in data:
                for tp in ["largeIcon", "rankTriangleDownIcon", "rankTriangleUpIcon"]:
                    progress = f"({count}/{max})"
                    try:
                        # set filename
                        name_en = String.wiki_format(value.get("tierName", {})["en-US"])
                        name_jp = String.wiki_format(value.get("tierName", {})["ja-JP"])
                        filename = str.title(name_en)
                        
                        if tp=="largeIcon":
                            filename += ".png"
                        elif tp=="rankTriangleDownIcon":
                            filename += "_triangle_down.png"
                        elif tp=="rankTriangleUpIcon":
                            filename += "_triangle_up.png"

                        # update check
                        img_exist: bool = os.path.exists(f"output/competitivetiers/{filename}")
                        exist: bool
                        if self.force:
                            exist = self.wiki.check_exist("File:" + filename)
                        else:
                            if img_exist:
                                exist = True
                            else:
                                exist = self.wiki.check_exist("File:" + filename)
                        
                        # get icon url
                        icon: str = None
                        if value.get(tp)!=None:
                            icon = value.get(tp)
                        else:
                            Log.print(f"{name_jp}({tp}) はスキップされました ({tp} が見つかりません)", "warn", _ftype)
                            result["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("tierName", {})["en-US"], "localized_name": value.get("tierName", {})["ja-JP"]})
                            continue

                        if not exist:
                            if icon!=None:
                                if not(img_exist) or self.force:
                                    Fetch.download(icon, f"output/competitivetiers/{filename}")
                                    
                                fd = filename.replace(" ", "_")
                                category = "[[Category:ランク]]"
                                if tp!="largeIcon":
                                    category = "[[Category:ACTランク]]"

                                self.wiki.upload(fd, category+"\n\n{{License Riot Games}}", f"output/competitivetiers/{filename}")
                                Log.print(f"{name_jp}({tp}) はアップロードされました {progress}", "info", _ftype)
                                result["updated"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("tierName", {})["en-US"], "localized_name": value.get("tierName", {})["ja-JP"]})
                            else:
                                Log.print(f"{name_jp}({tp}) はスキップされました ({tp} が見つかりません) {progress}", "warn", _ftype)
                                result["skipped"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("tierName", {})["en-US"], "localized_name": value.get("tierName", {})["ja-JP"]})
                                continue
                            
                        else:
                            if not(img_exist) or self.force:
                                Fetch.download(icon, f"output/competitivetiers/{filename}")
                            Log.print(f"{name_jp}({tp}) はスキップされました (既にアップロードされています) {progress}", "info", _ftype)
                            result["exists"].append({"file": filename, "name": value.get("tierName", {})["en-US"], "localized_name": value.get("tierName", {})["ja-JP"]})
                        
                    except Exception as e:
                        Log.exception(e, value.get("uuid", "") + " で例外が発生しました。", _ftype)
                        result["error"].append({"file": filename, "uuid": value.get("uuid", ""), "name": value.get("tierName", {})["en-US"], "localized_name": value.get("tierName", {})["ja-JP"]})
                        continue
                count+=1

            messagebox.showinfo("ランク (更新)", "ランクの更新確認が完了しました。")
            result["end"] = str(datetime.datetime.now())
            JSON.save("output/buddies/result.json", result)
            self.wiki.logout()

        except Exception as e:
            messagebox.showerror("ランク (更新)", "不明なエラーが発生したため、更新確認に失敗しました。")
            Log.exception(e, "ランクの更新確認に失敗しました。", _ftype)

    def agents(self):
        _ftype = "CORE.UPDATE.AGENT"
        try:
            data = JSON.read("api/agents.json")
            os.makedirs("output/agents", exist_ok=True)
            self.wiki.login()

            max = len(data)
            count = 1

            for value in data:
                for tp in ["displayIcon", "fullPortrait", "killfeedPortrait", "background", "voiceLine en-US", "voiceLine ja-JP"]:
                    progress = f"({count}/{max})"
                    # set filename
                    name_en = String.wiki_format(value.get("displayName", {})["en-US"])
                    name_jp = String.wiki_format(value.get("displayName", {})["ja-JP"])
                    if name_en == "Kayo":
                        name_en = "KAYO"
                        name_jp = "KAY/O"
                    filename = str.title(name_en)
                    
                    if tp=="displayIcon":
                        filename += "_Icon.png"
                    elif tp=="fullPortrait":
                        filename += ".png"
                    elif tp=="killfeedPortrait":
                        filename += "_killfeed.png"
                    elif tp=="background":
                        filename += "_Background.png"
                    elif tp=="voiceLine en-US":
                        filename += "_voiceline_en-us_Agent_Lockin.wav"
                    elif tp=="voiceLine ja-JP":
                        filename += "_voiceline_ja-jp_Agent_Lockin.wav"

                    try:
                        # update check
                        img_exist: bool = os.path.exists(f"output/agents/{filename}")
                        exist: bool
                        if self.force:
                            exist = self.wiki.check_exist("File:" + filename)
                        else:
                            if img_exist:
                                exist = True
                            else:
                                exist = self.wiki.check_exist("File:" + filename)
                        
                        # get icon url
                        icon: str = None
                        if tp=="voiceLine ja-JP":
                            if value.get("voiceLine", {}).get("ja-JP", {}).get("mediaList", [{}])[0].get("wave")!=None:
                                icon = value.get("voiceLine", {}).get("ja-JP", {}).get("mediaList", [{}])[0].get("wave")
                            else:
                                Log.print(f"{name_jp}({tp}) はスキップされました ({tp} が見つかりません)", "warn", _ftype)
                                continue
                        elif tp=="voiceLine en-US":
                            if value.get("voiceLine", {}).get("en-US", {}).get("mediaList", [{}])[0].get("wave")!=None:
                                icon = value.get("voiceLine", {}).get("en-US", {}).get("mediaList", [{}])[0].get("wave")
                            else:
                                Log.print(f"{name_jp}({tp}) はスキップされました ({tp} が見つかりません)", "warn", _ftype)
                                continue
                        else:
                            if value.get(tp)!=None:
                                icon = value.get(tp)
                            else:
                                Log.print(f"{name_jp}({tp}) はスキップされました ({tp} が見つかりません)", "warn", _ftype)
                                continue

                        if not exist:
                            if icon!=None:
                                if not(img_exist) or self.force:
                                    Fetch.download(icon, f"output/agents/{filename}")
                                    
                                fd = filename.replace(" ", "_")

                                category: str
                                if tp=="displayIcon":
                                    category = f"[[Category:エージェントの画像]][[Category:{name_jp}]]"
                                elif tp=="fullPortrait":
                                    category = f"[[Category:エージェントのアイコン]][[Category:{name_jp}]]"
                                elif tp=="killfeedPortrait":
                                    category = f"[[Category:エージェントのアイコン]][[Category:{name_jp}]]"
                                elif tp=="background":
                                    category = f"[[Category:エージェントの背景]][[Category:{name_jp}]]"
                                elif tp=="voiceLine en-US":
                                    category = f"[[Category:英語のボイス]][[Category:{name_jp}のボイス]]"
                                elif tp=="voiceLine ja-JP":
                                    category = f"[[Category:日本語のボイス]][[Category:{name_jp}のボイス]]"

                                self.wiki.upload(fd, category+"\n\n{{License Riot Games}}", f"output/agents/{filename}")
                                Log.print(f"{name_jp}({tp}) はアップロードされました {progress}", "info", _ftype)
                            else:
                                Log.print(f"{name_jp}({tp}) はスキップされました ({tp} が見つかりません) {progress}", "warn", _ftype)
                                continue
                            
                        else:
                            if not(img_exist) or self.force:
                                Fetch.download(icon, f"output/agents/{filename}")
                            Log.print(f"{name_jp}({tp}) はスキップされました (既にアップロードされています) {progress}", "info", _ftype)
                            
                    except Exception as e:
                        Log.exception(e, value.get("uuid", "") + " で例外が発生しました。", _ftype)
                        continue
                count+=1

            messagebox.showinfo("エージェント (更新)", "エージェントの更新確認が完了しました。")
            self.wiki.logout()

        except Exception as e:
            messagebox.showerror("エージェント (更新)", "不明なエラーが発生したため、更新確認に失敗しました。")
            Log.exception(e, "エージェントの更新確認に失敗しました。", _ftype)

    def weapons(self):
        _ftype = "CORE.UPDATE.WEAPON"

        try:
            data = JSON.read("api/weapons.json")
            self.wiki.login()

            res = {}

            for weapon in data:
                max = len(weapon.get("skins", []))
                count = 1
                result = {
                    "start": str(datetime.datetime.now()),
                    "end": str(datetime.datetime.now()),
                    "exists": [],
                    "skipped": [],
                    "updated": [],
                    "error": []
                }
                w_name = String.wiki_format(weapon.get("displayName", {})["en-US"]).lower()
                w_name_jp = weapon.get("displayName", {})["ja-JP"]

                os.makedirs(f"output/weapons/{w_name}", exist_ok=True)

                for value in weapon.get("skins", []):
                    progress = f"({count}/{max})"
                    try:
                        # set filename
                        name_en = String.wiki_format(value.get("displayName", {})["en-US"])
                        name_jp = String.wiki_format(value.get("displayName", {})["ja-JP"])

                        for chroma in value.get("chromas"):
                            filename = String.wiki_format(chroma.get("displayName", {})["en-US"])
                            if name_en == "Random Favorite Skin":
                                filename = f"Random Favorite {name_en} Skin.png"
                            elif filename == "Standard":
                                filename = f"{name_en}.png"
                            else:
                                if "\n" in filename:
                                    spl = filename.splitlines()
                                    filename = f"{name_en} {spl[1]}.png"
                                else:
                                    filename = filename + ".png"

                            # update check
                            img_exist: bool = os.path.exists(f"output/weapons/{w_name}/{filename}")
                            exist: bool
                            if self.force:
                                exist = self.wiki.check_exist("File:" + filename)
                            else:
                                if img_exist:
                                    exist = True
                                else:
                                    exist = self.wiki.check_exist("File:" + filename)
                            
                            # get icon url
                            icon: str = None
                            if chroma.get("displayIcon")!=None:
                                icon = chroma.get("displayIcon")
                            elif chroma.get("fullRender")!=None:
                                icon = chroma.get("fullRender")
                            else:
                                Log.print(f"{name_jp} はスキップされました (displayIcon が見つかりません)", "warn", _ftype)
                                result["skipped"].append({"file": filename, "uuid": chroma.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                                continue

                            if not exist:
                                if icon!=None:
                                    if not(img_exist) or self.force:
                                        Fetch.download(icon, f"output/weapons/{w_name}/{filename}")
                                        
                                    fd = filename.replace(" ", "_")
                                    self.wiki.upload(fd, "[[Category:"+ w_name_jp +"のスキン]]\n\n{{License Riot Games}}", f"output/weapons/{w_name}/{filename}")
                                    Log.print(f"{name_jp} はアップロードされました {progress}", "info", _ftype)
                                    result["updated"].append({"file": filename, "uuid": chroma.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                                else:
                                    Log.print(f"{name_jp} はスキップされました (displayIcon が見つかりません) {progress}", "warn", _ftype)
                                    result["skipped"].append({"file": filename, "uuid": chroma.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                                    continue
                                
                            else:
                                if not(img_exist) or self.force:
                                    Fetch.download(icon, f"output/weapons/{w_name}/{filename}")
                                Log.print(f"{name_jp} はスキップされました (既にアップロードされています) {progress}", "info", _ftype)
                                result["exists"].append({"file": filename, "uuid": chroma.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        
                    except Exception as e:
                        Log.exception(e, value.get("uuid", "") + "で例外が発生しました。", _ftype)
                        result["error"].append({"file": filename, "uuid": chroma.get("uuid", ""), "name": value.get("displayName", {})["en-US"], "localized_name": value.get("displayName", {})["ja-JP"]})
                        continue
                    
                    finally:
                        count+=1

            res[w_name] = result

        except Exception as e:
            messagebox.showerror("武器 (更新)", "不明なエラーが発生したため、更新確認に失敗しました。")
            Log.exception(e, "武器の更新確認に失敗しました。", _ftype)
    
    def skin_video(self):
        _ftype = "CORE.UPDATE.SKINVIDEO"
        
        try:
            data = JSON.read("api/weapons.json")

            for weapon in data:
                dir_name = String.wiki_format(weapon.get("displayName", {})["en-US"]).lower()
                os.makedirs(f"output/weapons/video/{dir_name}", exist_ok=True)
                count = len(weapon.get("skins", []))
                i: int = 1

                for skin in weapon.get("skins", []):
                    try:
                        skin_name = skin.get("displayName", {})["en-US"]
                        Log.print(f"{skin_name} の映像をダウンロードしています ({i}/{count})", "info", _ftype)

                        for chroma in skin.get("chromas", []):
                            if chroma["streamedVideo"]!=None:
                                chroma_name: str = chroma.get("displayName", {})["en-US"]
                                if "\n" in chroma_name:
                                    c = chroma_name.splitlines()
                                    chroma_name = f"{skin_name} {c[1]}"
                                chroma_name = String.wiki_format(chroma_name)

                                if exist==False or self.force:
                                    Log.print(f"{chroma_name}.mp4 をダウンロードしています", "info", _ftype)
                                    Fetch.download(chroma["streamedVideo"], f"output/weapons/video/{dir_name}/{chroma_name}.mp4")
                        
                        for level in skin.get("levels", []):
                            if level["streamedVideo"]!=None:
                                level_name: str = level.get("displayName", {})["en-US"]
                                if "\n" in level_name:
                                    c = level_name.splitlines()
                                    level_name = f"{skin_name} {c[1]}"
                                level_name = String.wiki_format(level_name)

                                exist: bool = os.path.exists(f"output/weapons/video/{dir_name}/{level_name}.mp4")

                                if exist==False or self.force:
                                    Log.print(f"{level_name}.mp4 をダウンロードしています", "info", _ftype)
                                    Fetch.download(level["streamedVideo"], f"output/weapons/video/{dir_name}/{level_name}.mp4")
                        
                        i = i+1

                    except Exception as e:
                        Log.exception(e, f"{skin_name}のダウンロードに失敗しました。", _ftype)
                        continue

        except Exception as e:
            messagebox.showerror("武器 - ビデオ (更新)", "不明なエラーが発生したため、ダウンロードに失敗しました。")
            Log.exception(e, "武器 (ビデオ)のダウンロードに失敗しました。", _ftype)
                    
    def levelborders(self):
        _ftype = "CORE.UPDATE.BORDER"
        try:
            data = JSON.read("api/levelborders.json")
            os.makedirs("output/levelborders", exist_ok=True)
            self.wiki.login()

            max = len(data)
            count = 1
            result = {
                "levelNumberAppearance": {
                    "start": str(datetime.datetime.now()),
                    "end": str(datetime.datetime.now()),
                    "exists": [],
                    "skipped": [],
                    "updated": [],
                    "error": []
                },
                "smallPlayerCardAppearance": {
                    "start": str(datetime.datetime.now()),
                    "end": str(datetime.datetime.now()),
                    "exists": [],
                    "skipped": [],
                    "updated": [],
                    "error": []
                }
            }

            for value in data:
                progress = f"({count}/{max})"
                try:
                    # set filename
                    level = value.get("startingLevel")

                    for c in ["levelNumberAppearance", "smallPlayerCardAppearance"]:
                        filename = {
                            "levelNumberAppearance": f"Border Lv{level}.png",
                            "smallPlayerCardAppearance": f"Border Card Lv{level}.png"
                        }

                        # update check
                        img_exist: bool = os.path.exists(f"output/levelborders/{filename[c]}")
                        exist: bool
                        if self.force:
                            exist = self.wiki.check_exist("File:" + filename[c])
                        else:
                            if img_exist:
                                exist = True
                            else:
                                exist = self.wiki.check_exist("File:" + filename[c])
                        
                        # get icon url
                        icon: str = None
                        if value.get(c)!=None:
                            icon = value.get(c)
                        else:
                            Log.print(f"Lv.{level} はスキップされました ({c} が見つかりません)", "warn", _ftype)
                            result[c]["skipped"].append({"file": filename[c], "uuid": value.get("uuid", ""), "level": level})
                            continue

                        if not exist:
                            if icon!=None:
                                if not(img_exist) or self.force:
                                    Fetch.download(icon, f"output/levelborders/{filename[c]}")
                                    
                                fd = filename[c].replace(" ", "_")
                                self.wiki.upload(fd, "[[Category:レベルボーダー]]\n\n{{License Riot Games}}", f"output/levelborders/{filename[c]}")
                                Log.print(f"Lv.{level} はアップロードされました ({c}) {progress}", "info", _ftype)
                                result[c]["updated"].append({"file": filename[c], "uuid": value.get("uuid", ""), "level": level})
                            else:
                                Log.print(f"Lv.{level} はスキップされました ({c} が見つかりません) {progress}", "warn", _ftype)
                                result[c]["skipped"].append({"file": filename[c], "uuid": value.get("uuid", ""), "level": level})
                                continue
                        
                        else:
                            if not(img_exist) or self.force:
                                Fetch.download(icon, f"output/levelborders/{filename[c]}")
                            Log.print(f"Lv.{level} はスキップされました ({c}は既にアップロードされています) {progress}", "info", _ftype)
                            
                            result[c]["exists"].append({"file": filename[c], "uuid": value.get("uuid", ""), "level": level})
                    
                except Exception as e:
                    Log.exception(e, value.get("uuid", "") + "で例外が発生しました。", _ftype)
                    result["levelNumberAppearance"]["error"].append({"file": filename[c], "uuid": value.get("uuid", ""), "level": level})
                    result["smallPlayerCardAppearance"]["error"].append({"file": filename[c], "uuid": value.get("uuid", ""), "level": level})
                    continue
                
                finally:
                    count+=1



            messagebox.showinfo("レベルボーダー (更新)", "レベルボーダーの更新確認が完了しました。")
            result["end"] = str(datetime.datetime.now())
            JSON.save("output/levelborders/result.json", result)
            self.wiki.logout()

        except Exception as e:
            messagebox.showerror("レベルボーダー (更新)", "不明なエラーが発生したため、更新確認に失敗しました。")
            Log.exception(e, "レベルボーダーの更新確認に失敗しました。", _ftype)
    