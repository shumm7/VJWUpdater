import tkinter, os, datetime, math
import tkinter.simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData
from utils.api import API
from utils.wiki import Wiki

class Wikitext():
    root: tkinter.Tk
    wiki: Wiki
    force: bool

    def __init__(self, root: tkinter.Tk, wiki: Wiki, force: bool = False) -> None:
        self.root = root
        self.wiki = wiki
        self.force = force
    
    def infobox_agents(self):
        _ftype = "CORE.WIKITEXT.AGENT"
        try:
            messagebox.showwarning("Infobox agent (Wiki構文)", "出力されるテンプレートは未完成です。必要に応じて情報を追加してください。")
            data = JSON.read("api/agents.json")
            os.makedirs(f"output/agents/infobox", exist_ok=True)

            for value in data:
                try:
                    name = value.get("displayName", {})["en-US"]
                    name_en = String.wiki_format(value.get("displayName", {})["en-US"])
                    name_jp = value.get("displayName", {})["ja-JP"]

                    abilities = {
                        "passive": [],
                        "signature": [],
                        "ultimate": []
                    }
                    for abl in value.get("abilities", []):
                        if abl["slot"]=="Ultimate":
                            abilities["ultimate"].append("{{ability" + abl.get("displayName", {}).get("ja-JP", "") + "}}")
                        elif abl["slot"]=="Passive":
                            abilities["passive"].append("{{ability" + abl.get("displayName", {}).get("ja-JP", "") + "}}")
                        else:
                            abilities["signature"].append("{{ability" + abl.get("displayName", {}).get("ja-JP", "") + "}}")

                    tags = ""
                    if value.get("characterTags", []) != None:
                        if len(value.get("characterTags", []))>0:
                            tags = "{{hlist"
                            for tag in value.get("characterTags", []):
                                tags += "|" + tag.get("ja-JP", "")
                            tags += "}}"
                    
                    colors = []
                    if value.get("backgroundGradientColors", []) != None:
                        for c in value.get("backgroundGradientColors", []):
                            colors.append("{{color box|" + c[:-2] + "}}")

                    args = {
                        "title": f"Infobox agent/{name}",
                        "image": f"{name_en}.png",
                        "icon": f"{name_en} Icon.png",
                        "killfeed": f"{name_en} killfeed.png",
                        "name": name_jp,
                        "name-latin": name.upper(),

                        "role": value.get("role", {}).get("displayName", {}).get("ja-JP", ""),
                        "passive": String.wiki_mklist(abilities["passive"]),
                        "ability": String.wiki_mklist(abilities["signature"]),
                        "ultimate": String.wiki_mklist(abilities["ultimate"]),
                        "tag": tags,
                        "colors": String.wiki_mklist(colors, " "),
                        "codename": value.get("developerName"),

                        "realname": "",
                        "alias": "",
                        "origin": "",
                        "birth": "",
                        "race": "",
                        "gender": "",
                        "relation": "",
                        "number": "",
                        "affiliation": "",
                        "occupation": "",
                        "other": "",
                        "added": "",
                        "voice": "",
                        "voice-actor": ""
                    }
                    with open(f"output/agents/infobox/{name_en}.txt", "w") as fp:
                        fp.write(String.wiki_template("Infobox agent", args, "\n"))
                        Log.print(f"{name_en}.txt を生成しました。", "info", _ftype)

                except Exception as e:
                    Log.exception(e, name + "のInfoboxテンプレートの作成に失敗しました。", _ftype)

            messagebox.showinfo("Infobox agent (Wiki構文)", "Infobox agent の作成が完了しました。")
            Log.print("Infobox agentの作成が完了しました。", "info", _ftype)

        except Exception as e:
            messagebox.showerror("Infobox agent (Wiki構文)", "Infobox agent の作成に失敗しました。")
            Log.exception(e, "Infobox agentの作成に失敗しました。", _ftype)

    def contracts(self):
        _ftype = "CORE.WIKITEXT.CONTRACT"
        try:
            upload: bool = False
            if "yes" == messagebox.askquestion("Contracts (Wiki構文)", "作成したテンプレートをWikiにアップロードしますか？"):
                upload = True

            d: dict = JSON.read("api/contracts.json")
            os.makedirs("output/contracts/", exist_ok=True)

            if upload:
                self.wiki.login()


            for data in d:
                try:
                    if data["displayIcon"]:
                        Fetch.download(data["displayIcon"], "output/contracts/" + String.wiki_format(data["displayName"]["en-US"]) + "_icon.png")
                    
                    f = open("output/contracts/" + String.wiki_format(data["displayName"]["en-US"]) + ".txt", 'w', newline="\n", encoding='utf-8')
                    line = []
                    line.append("{{Contracts-begin"
                        + "|" + data["displayName"]["ja-JP"]
                        + "|name=Template:Contracts/" + data["displayName"]["en-US"].replace("/", "").replace("?", "").replace(":", "").replace("#", "")
                        + "}}\n"
                    )

                    def append_line(value: dict, tier: str, free: bool = False, premium: bool = False, isfree: bool = False):
                        vp: str = ""
                        xp: str = ""
                        tp: str = ""
                        kc: str = ""
                        uuid: str = ""
                        if free:
                            tp = value["type"]
                            uuid=  value["uuid"]
                        else:
                            tp = value["reward"]["type"]
                            uuid = value["reward"]["uuid"]
                            if value["isPurchasableWithVP"]==True:
                                vp = str(value["vpCost"])
                            xp = str(value["xp"])
                            
                            if value["isPurchasableWithDough"]==True:
                                kc = str(value["doughCost"])
                        
                        if premium:
                            premium = "|premium=yes"
                        else:
                            premium = ""
                            
                        if isfree:
                            isfree = "|free=yes"
                        else:
                            isfree = ""

                        if tp=="Spray":
                            for content in JSON.read("api/sprays.json"):
                                if content["uuid"]==uuid:
                                    line.append("{{Contracts|"
                                        + content["displayName"]["ja-JP"]
                                        +"||[[File:"
                                        + content["displayName"]["en-US"].replace("/", "").replace("?", "").replace(":", "").replace("#", "")
                                        + ".png]]|"
                                        + tier + "|"
                                        + xp + "|"
                                        + vp + "|"
                                        + kc
                                        + isfree + premium + "}}\n"
                                    )
                                    break

                        elif tp=="PlayerCard":
                            for content in JSON.read("api/playercards.json"):
                                if content["uuid"]==uuid:
                                    line.append("{{Contracts|"
                                        + content["displayName"]["ja-JP"]
                                        +"||[[File:"
                                        + content["displayName"]["en-US"].replace("/", "").replace("?", "").replace(":", "").replace("#", "")
                                        + "_icon.png]]|"
                                        + tier + "|"
                                        + xp + "|"
                                        + vp + "|"
                                        + kc
                                        + isfree + premium + "}}\n"
                                    )
                                    break

                        elif tp=="Title":
                            for content in JSON.read("api/playertitles.json"):
                                if content["uuid"]==uuid:
                                    line.append("{{Contracts|"
                                        + content["displayName"]["ja-JP"]
                                        +"|"
                                        + content["titleText"]["ja-JP"]
                                        + "|[[File:Player Titles.png]]|"
                                        + tier + "|"
                                        + xp + "|"
                                        + vp + "|"
                                        + kc
                                        + isfree + premium + "}}\n"
                                    )
                                    break

                        elif tp=="Character":
                            for content in JSON.read("api/agents.json"):
                                if content["uuid"]==uuid:
                                    line.append("{{Contracts|[["
                                        + content["displayName"]["ja-JP"]
                                        +"]]||[[File:"
                                        + content["displayName"]["en-US"].replace("/", "").replace("?", "").replace(":", "").replace("#", "")
                                        + "_Icon.png]]|"
                                        + tier + "|"
                                        + xp + "|"
                                        + vp + "|"
                                        + kc
                                        + isfree + premium + "}}\n"
                                    )
                                    break
                        
                        elif tp=="EquippableCharmLevel":
                            for buddy in JSON.read("api/buddies.json"):
                                for content in buddy["levels"]:
                                    if content["uuid"]==uuid:
                                        line.append("{{Contracts|"
                                            + buddy["displayName"]["ja-JP"]
                                            +"||[[File:"
                                            + buddy["displayName"]["en-US"].replace("/", "").replace("?", "").replace(":", "").replace("#", "")
                                            + ".png]]|"
                                            + tier + "|"
                                            + xp + "|"
                                            + vp + "|"
                                            + kc
                                            + isfree + premium + "}}\n"
                                        )
                                        break
                        
                        elif tp=="EquippableSkinLevel":
                            for guns in JSON.read("api/weapons.json"):
                                for skin in guns["skins"]:
                                    for content in skin["levels"]:
                                        if content["uuid"]==uuid:
                                            line.append("{{Contracts|"
                                                + skin["displayName"]["ja-JP"]
                                                +"||[[File:"
                                                + skin["displayName"]["en-US"].replace("/", "").replace("?", "").replace(":", "").replace("#", "")
                                                + ".png]]|"
                                                + tier + "|"
                                                + xp + "|"
                                                + vp + "|"
                                                + kc
                                                + isfree + premium + "}}\n"
                                            )
                                            break

                        elif tp=="Currency":
                            if uuid=="e59aa87c-4cbf-517a-5983-6e81511be9b7":
                                line.append("{{Contracts|[["
                                                + "レディアナイトポイント"
                                                +"]]|"
                                                + "{{rp|10|invert=no}}"
                                                +"|[[File:Radianite Point.png]]|"
                                                + tier + "|"
                                                + xp + "|"
                                                + vp + "|"
                                                + kc
                                                + isfree + premium + "}}\n"
                                            )
                            elif uuid=="f08d4ae3-939c-4576-ab26-09ce1f23bb37":
                                line.append("{{Contracts|[["
                                                + "フリーエージェント"
                                                +"]]|"
                                                +"|[[File:Free Agent.png]]|"
                                                + tier + "|"
                                                + xp + "|"
                                                + vp + "|"
                                                + kc
                                                + isfree + premium + "}}\n"
                                            )
                            elif uuid=="85ca954a-41f2-ce94-9b45-8ca3dd39a00d":
                                line.append("{{Contracts|[["
                                                + "キングダムクレジット"
                                                +"]]|"
                                                +"|[[File:Kingdom Credit.png]]|"
                                                + tier + "|"
                                                + xp + "|"
                                                + vp + "|"
                                                + kc
                                                + isfree + premium + "}}\n"
                                            )

                    count: int = 0
                    count_ep: int = 0
                    for chapter in data["content"]["chapters"]:
                        epilogue = chapter["isEpilogue"]
                        tier: str = ""

                        if epilogue:
                            tier = "EPILOGUE "
                            for item in chapter["levels"]:
                                count_ep = count_ep + 1
                                append_line(item, tier+str(count_ep), False, epilogue, False)
                            
                            if chapter.get("freeRewards")==None:
                                chapter["freeRewards"] = []
                            for item in chapter["freeRewards"]:
                                append_line(item, tier+str(count_ep), True, epilogue, True)
                        else:
                            tier = "TIER "
                            for item in chapter["levels"]:
                                count = count + 1
                                append_line(item, tier+str(count), False, epilogue, False)
                            
                            if chapter.get("freeRewards")==None:
                                chapter["freeRewards"] = []
                            for item in chapter["freeRewards"]:
                                append_line(item, tier+str(count), True, epilogue, True)

                    line.append("{{Contracts-end}}<noinclude>\n[[カテゴリ:バトルパステンプレート]]\n</noinclude>")
                    f.writelines(line)
                    f.close()

                    if upload:
                        f = open("output/contracts/" + String.wiki_format(data["displayName"]["en-US"]) + ".txt", 'r', encoding='utf-8')
                        template = f.read() + "<noinclude>\n[[Category:バトルパステンプレート]]\n</noinclude>"
                        template_name = "Template:Contracts/" + String.wiki_format(data["displayName"]["en-US"])

                        self.wiki.edit_page(page=template_name, text=template, editonly=False)
                        Log.print(template_name + " を編集しました。", "info", _ftype)

                    
                    Log.print(data["displayName"]["ja-JP"] + " を作成しました。", "info", _ftype)

                except Exception as e:
                    messagebox.showerror("Contracts (Wiki構文)", "Contracts ("+ data["displayName"]["en-US"] +") の作成に失敗しました。")
                    Log.exception(e, "Contracts "+ data["displayName"]["en-US"] +"の作成に失敗しました。", _ftype)

            if upload:
                self.wiki.logout()
            messagebox.showinfo("Contracts (Wiki構文)", "Contracts の作成が完了しました。")
            Log.print("Contracts の作成が完了しました。", "info", _ftype)

        except Exception as e:
            messagebox.showerror("Contracts (Wiki構文)", "Contracts の作成に失敗しました。")
            Log.exception(e, "Contracts の作成に失敗しました。", _ftype)
    