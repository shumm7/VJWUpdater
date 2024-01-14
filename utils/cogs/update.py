import flet as ft
import os
import re
from utils.tools.localize import Lang
from utils.tools.json import JSON
from utils.tools.fetch import Fetch
from utils.tools.wiki import Wiki, WikiString, FileName
from utils.tools.gui import Gui
import utils.tools.db as db


class Update():
    page: ft.Page
    wiki: Wiki
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.playercard = PlayerCard(wiki, gui, page)
        self.spray = Spray(wiki, gui, page)
        self.buddy = Buddy(wiki, gui, page)
        self.competitivetier = Competitivetier(wiki, gui, page)
        self.agent = Agent(wiki, gui, page)
        self.weapon = Weapon(wiki, gui, page)
        self.levelborder = Levelborder(wiki, gui, page)
        self.playertitle = Playertitle(wiki, gui, page)
        self.contract = Contract(wiki, gui, page)
    
    def main(self):
        self.content = ft.Container(self.playercard.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index
            contents = [
                self.playercard.main(),
                self.spray.main(),
                self.buddy.main(),
                self.competitivetier.main(),
                self.agent.main(),
                self.weapon.main(),
                self.levelborder.main(),
                self.playertitle.main(),
                self.contract.main()
            ]

            try:
                self.content.content = contents[i]
            except IndexError:
                pass
            self.gui.safe_update(self.content)
            

        return ft.Row(
            [
                ft.NavigationRail(
                    selected_index=0,
                    label_type=ft.NavigationRailLabelType.ALL,
                    min_width=100,
                    min_extended_width=400,
                    destinations=[
                        ft.NavigationRailDestination(
                            icon=ft.icons.PERSON_OUTLINED,
                            selected_icon=ft.icons.PERSON,
                            label=Lang.value("contents.update.playercard.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.EMOJI_NATURE_OUTLINED,
                            selected_icon=ft.icons.EMOJI_NATURE,
                            label=Lang.value("contents.update.spray.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.CRUELTY_FREE_OUTLINED,
                            selected_icon=ft.icons.CRUELTY_FREE,
                            label=Lang.value("contents.update.buddy.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.DIAMOND_OUTLINED,
                            selected_icon=ft.icons.DIAMOND,
                            label=Lang.value("contents.update.competitivetier.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.GROUPS_OUTLINED,
                            selected_icon=ft.icons.GROUPS,
                            label=Lang.value("contents.update.agent.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.INVENTORY_2_OUTLINED,
                            selected_icon=ft.icons.INVENTORY_2,
                            label=Lang.value("contents.update.weapon.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.BOOKMARK_BORDER,
                            selected_icon=ft.icons.BOOKMARK,
                            label=Lang.value("contents.update.levelborder.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.BOOKMARK_BORDER,
                            selected_icon=ft.icons.BOOKMARK,
                            label=Lang.value("contents.update.playertitle.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.BOOKMARK_BORDER,
                            selected_icon=ft.icons.BOOKMARK,
                            label=Lang.value("contents.update.contract.title"),
                        ),
                    ],
                    on_change=on_clicked
                ),
                ft.Card(
                    content=ft.Column([
                        ft.Container(
                            width=500,
                            padding=20,
                            content = self.content,
                        )],
                        horizontal_alignment=ft.MainAxisAlignment.START
                    ),
                    expand=True
                )
            ]
        )


class PlayerCard():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    lists: Gui.UpdateResult
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.lists = self.gui.UpdateResult(self.page)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_force.on_change = on_changed_force
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            result = {"skipped": 0, "success": 0, "warn": 0, "error": 0}
            checked = JSON.read("output/playercards.json")
            
            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.playercard.begin"))
                self.loading.state(True)

                self.update_state(Lang.value("contents.update.playercard.db"))
                self.cargo_data()

                os.makedirs("output/temp", exist_ok=True)
                data = JSON.read("api/playercards.json")

                login: bool = True
                try:
                    self.wiki.login()
                except Exception as e:
                    login = False
                    self.gui.popup_error(Lang.value("common.wikilogin_failed"), str(e))

                max = len(data)
                count = 1

                for value in data:
                    progress = Lang.value("contents.update.common.progress").format(count=count, max=max)
                    self.update_state(progress)
                    count += 1

                    for type in ["small", "wide", "large"]:
                        try:
                            filename = FileName.playercard(value, type)
                            if checked.get(value["uuid"])==None:
                                checked[value["uuid"]] = {}

                            # update check
                            exist: bool
                            if self.switch_force.value:
                                exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["uuid"]][type] = exist
                            else:
                                exist = checked[value["uuid"]].get(type, False)
                                if not exist:
                                    exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["uuid"]][type] = exist
                            
                            if not exist:
                                # icon link
                                icon: str = None
                                if value.get(f"{type}Art")!=None:
                                    icon = value.get(f"{type}Art")
                                elif type=="small" and value.get(f"smallArt")==None:
                                    icon = value.get("displayIcon")
                                if icon==None:
                                    self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.playercard.warn_notfound"))
                                    result["warn"] += 1
                                    continue
                            
                                # upload
                                if login:
                                    Fetch.download(icon, f"output/temp/{filename}")
                                    fd = filename.replace(" ", "_")
                                    self.wiki.upload(fd, Lang.value(f"contents.update.playercard.wiki_description.{type}") + Lang.value(f"contents.update.common.wiki_description"), f"output/temp/{filename}")
                                    self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "success", Lang.value("common.success"))
                                    result["success"] += 1
                                    os.remove(f"output/temp/{filename}")
                                    checked[value["uuid"]][type] = True
                            else:
                                result["skipped"] += 1

                        except Exception as e:
                            self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "error", Lang.value("common.error"), str(e))
                            result["error"] += 1
                        finally:
                            JSON.save("output/playercards.json", checked)
                            if os.path.exists(f"output/temp/{filename}"):
                                os.remove(f"output/temp/{filename}")
                
                self.result.success(Lang.value("contents.update.playercard.success"), Lang.value("contents.update.playercard.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.playercard.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.playercard.failed"))
                self.gui.popup_error(Lang.value("contents.update.playercard.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
                JSON.save("output/playercards.json", checked)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.playercard.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.playercard.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                        self.switch_force,
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists.main(),
                    padding=10,
                    height=200
                ),

                self.result.main()
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
    
    def cargo_data(self):
        playercards, row = db.Playercard.make_list()

        for key,values in row.items():
            addition = ""
            for uuid in values:
                playercard = playercards[uuid]
                addition += "{{Playercard/CargoStore|uuid="+ playercard["uuid"] + "|name=" + playercard["name"] + "|localized_name=" + playercard["localized_name"] + "|image=" + playercard["image"] + "|icon=" + playercard["icon"] + "|wide=" + playercard["wide"]
                if len(playercard["relation"])>0:
                    addition += "|relation=" + ",".join(playercard["relation"])
                addition += "|bundle=" + playercard["bundle"] + "|description=" + playercard["description"] + "}}\n"
            addition += "[[Category:メタデータ]]"

            with open(f"output/data/Playercard.{key}.txt", "w", encoding="UTF-8") as f:
                f.write(addition)
        
            if self.switch_upload.value:  
                self.wiki.login()
                self.wiki.edit_page(f"Data:Playercard/{key}", addition, editonly=False)
                self.wiki.logout()
    
class Spray():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    lists: Gui.UpdateResult
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.lists = self.gui.UpdateResult(self.page)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_force.on_change = on_changed_force
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            result = {"skipped": 0, "success": 0, "warn": 0, "error": 0}
            checked = JSON.read("output/sprays.json")

            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.spray.begin"))
                self.loading.state(True)

                self.update_state(Lang.value("contents.update.spray.db"))
                self.cargo_data()

                os.makedirs("output/temp", exist_ok=True)
                data = JSON.read("api/sprays.json")

                login: bool = True
                try:
                    self.wiki.login()
                except Exception as e:
                    login = False
                    self.gui.popup_error(Lang.value("common.wikilogin_failed"), str(e))

                max = len(data)
                count = 1

                for value in data:
                    progress = Lang.value("contents.update.common.progress").format(count=count, max=max)
                    self.update_state(progress)
                    count += 1

                    try:
                        for type in ["image", "icon"]:
                            filename = FileName.spray(value, type)

                            # update check
                            exist: bool
                            if checked.get(value["uuid"]) == None:
                                checked[value["uuid"]] = {}
                            if self.switch_force.value:
                                exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["uuid"]][type] = exist
                            else:
                                exist = checked.get(value["uuid"], {}).get(type, False)
                                if not exist:
                                    exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["uuid"]][type] = exist
                            
                            if not exist:
                                # icon link
                                icon: str = None
                                if type=="image":
                                    if value.get("animationPng")!=None:
                                        icon = value.get("animationPng")
                                    elif value.get("fullTransparentIcon")!=None:
                                        icon = value.get("fullTransparentIcon")
                                    elif value.get("fullIcon")!=None:
                                        icon = value.get("fullIcon")
                                    if icon==None and exist==False:
                                        self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")) or "" + f"({type})", filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.spray.warn_notfound"))
                                        result["warn"] += 1
                                        continue
                                elif type=="icon":
                                    if value.get("displayIcon")!=None:
                                        icon = value.get("displayIcon")
                                    if icon==None and exist==False:
                                        self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")) or "" + f"({type})", filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.spray.warn_notfound"))
                                        result["warn"] += 1
                                        continue
                                    
                                # upload
                                if login:
                                    Fetch.download(icon, f"output/temp/{filename}")
                                    fd = filename.replace(" ", "_")
                                    self.wiki.upload(fd, Lang.value(f"contents.update.spray.wiki_description.{type}") + Lang.value(f"contents.update.common.wiki_description"), f"output/temp/{filename}")
                                    self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")) or "" + f"({type})", filename, "success", Lang.value("common.success"))
                                    result["success"] += 1
                                    os.remove(f"output/temp/{filename}")
                                    checked[value["uuid"]][type] = True
                            else:
                                result["skipped"] += 1

                    except Exception as e:
                        self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")) or "", filename, "error", Lang.value("common.error"), str(e))
                        result["error"] += 1
                    finally:
                        JSON.save("output/sprays.json", checked)
                        if os.path.exists(f"output/temp/{filename}"):
                            os.remove(f"output/temp/{filename}")

                self.result.success(Lang.value("contents.update.spray.success"), Lang.value("contents.update.spray.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.spray.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.spray.failed"))
                self.gui.popup_error(Lang.value("contents.update.spray.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
                JSON.save("output/sprays.json", checked)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.spray.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.spray.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                        self.switch_force
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists.main(),
                    padding=10,
                    height=200
                ),

                self.result.main()
            ],
            spacing=0
        )

    def cargo_data(self):
        page = self.wiki.get_wikitext("Data:Spray") 
        sprays, row = db.Spray.make_list()

        for key,values in row.items():
            addition = ""
            for uuid in values:
                spray = sprays[uuid]
                addition += "{{Spray/CargoStore|uuid="+ spray["uuid"] + "|name=" + spray["name"] + "|localized_name=" + spray["localized_name"] + "|image=" + spray["image"] + "|icon=" + spray["icon"]
                if len(spray["relation"])>0:
                    addition += "|relation=" + ",".join(spray["relation"])
                addition += "|bundle=" + spray["bundle"] + "|description=" + spray["description"] + "}}\n"
            addition += "[[Category:メタデータ]]"
        
            with open(f"output/data/Spray.{key}.txt", "w", encoding="UTF-8") as f:
                f.write(addition)

            if self.switch_upload.value:  
                self.wiki.login()
                self.wiki.edit_page(f"Data:Spray/{key}", addition, editonly=False)
                self.wiki.logout()

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass

class Buddy():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    lists: Gui.UpdateResult
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.lists = self.gui.UpdateResult(self.page)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_force.on_change = on_changed_force
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            result = {"skipped": 0, "success": 0, "warn": 0, "error": 0}
            checked = JSON.read("output/buddies.json")

            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.buddy.begin"))
                self.loading.state(True)

                self.update_state(Lang.value("contents.update.buddy.db"))
                self.cargo_data()

                os.makedirs("output/temp", exist_ok=True)
                data = JSON.read("api/buddies.json")

                login: bool = True
                try:
                    self.wiki.login()
                except Exception as e:
                    login = False
                    self.gui.popup_error(Lang.value("common.wikilogin_failed"), str(e))

                max = len(data)
                count = 1

                for value in data:
                    try:
                        progress = Lang.value("contents.update.common.progress").format(count=count, max=max)
                        self.update_state(progress)
                        count += 1
                        filename = FileName.buddy(value)

                        # update check
                        exist: bool
                        if self.switch_force.value:
                            exist = self.wiki.check_exist(f"File:{filename}")
                            checked[value["uuid"]] = exist
                        else:
                            exist = checked.get(value["uuid"], False)
                            if not exist:
                                exist = self.wiki.check_exist(f"File:{filename}")
                            checked[value["uuid"]] = exist
                        
                        if not exist:
                            # icon link
                            icon: str = None
                            if value.get("displayIcon")!=None:
                                icon = value.get("displayIcon")
                            if icon==None and exist==False:
                                self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")), filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.buddy.warn_notfound"))
                                result["warn"] += 1
                                continue

                            # upload
                            if login:
                                Fetch.download(icon, f"output/temp/{filename}")
                                fd = filename.replace(" ", "_")
                                self.wiki.upload(fd, Lang.value("contents.update.buddy.wiki_description") + Lang.value(f"contents.update.common.wiki_description"), f"output/temp/{filename}")
                                self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")), filename, "success", Lang.value("common.success"))
                                result["success"] += 1
                                os.remove(f"output/temp/{filename}")
                                checked[value["uuid"]] = True
                        else:
                            result["skipped"] += 1

                    except Exception as e:
                        self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")), filename, "error", Lang.value("common.error"), str(e))
                        result["error"] += 1
                    finally:
                        JSON.save("output/buddies.json", checked)
                        if os.path.exists(f"output/temp/{filename}"):
                            os.remove(f"output/temp/{filename}")

                self.result.success(Lang.value("contents.update.buddy.success"), Lang.value("contents.update.buddy.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.buddy.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.buddy.failed"))
                self.gui.popup_error(Lang.value("contents.update.buddy.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
                JSON.save("output/buddies.json", checked)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.buddy.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.buddy.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                        self.switch_force
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists.main(),
                    padding=10,
                    height=200
                ),

                self.result.main()
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
    
    def cargo_data(self):
        buddies, row = db.Buddy.make_list()

        for key,values in row.items():
            addition = ""
            for uuid in values:
                buddy = buddies[uuid]
                addition += "{{Buddy/CargoStore|uuid="+ buddy["uuid"] + "|name=" + buddy["name"] + "|localized_name=" + buddy["localized_name"] + "|image=" + buddy["image"]
                if len(buddy["relation"])>0:
                    addition += "|relation=" + ",".join(buddy["relation"])
                addition += "|bundle=" + buddy["bundle"] + "|description=" + buddy["description"] + "}}\n"
            addition += "[[Category:メタデータ]]"

            with open(f"output/data/Buddy.{key}.txt", "w", encoding="UTF-8") as f:
                f.write(addition)
            
            if self.switch_upload.value:  
                self.wiki.login()
                self.wiki.edit_page(f"Data:Buddy/{key}", addition, editonly=False)
                self.wiki.logout()

class Competitivetier():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    lists: Gui.UpdateResult
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.lists = self.gui.UpdateResult(self.page)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_force.on_change = on_changed_force
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            result = {"skipped": 0, "success": 0, "warn": 0, "error": 0}
            checked = JSON.read("output/competitivetiers.json")

            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.competitivetier.begin"))
                self.loading.state(True)

                self.cargo_data()

                os.makedirs("output/temp", exist_ok=True)
                data = JSON.read("api/competitivetiers.json")

                login: bool = True
                try:
                    self.wiki.login()
                except Exception as e:
                    login = False
                    self.gui.popup_error(Lang.value("common.wikilogin_failed"), str(e))

                max = len(data[-1]["tiers"])
                count = 1

                for value in data[-1]["tiers"]:
                    progress = Lang.value("contents.update.common.progress").format(count=count, max=max)
                    self.update_state(progress)
                    count += 1

                    for type in ["large", "rankTriangleDown", "rankTriangleUp"]:
                        try:
                            filename = FileName.competitive_tier(value, type)

                            if checked.get(value["tier"])==None:
                                checked[value["tier"]] = {}

                            # update check
                            exist: bool
                            if self.switch_force.value:
                                exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["tier"]][type] = exist
                            else:
                                exist = checked[value["tier"]].get(type, False)
                                if not exist:
                                    exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["tier"]][type] = exist
                            
                            if not exist:
                                # icon link
                                icon: str = None
                                if value.get(f"{type}Icon")!=None:
                                    icon = value.get(f"{type}Icon")
                                if icon==None:
                                    self.lists.append(value.get("tierName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.competitivetier.warn_notfound"))
                                    result["warn"] += 1
                                    continue
                                    
                                # upload
                                if login:
                                    Fetch.download(icon, f"output/temp/{filename}")
                                    fd = filename.replace(" ", "_")
                                    self.wiki.upload(fd, Lang.value(f"contents.update.competitivetier.wiki_description.{type}") + Lang.value(f"contents.update.common.wiki_description"), f"output/competitivetiers/{filename}")
                                    self.lists.append(value.get("tierName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "success", Lang.value("common.success"))
                                    result["success"] += 1
                                    os.remove(f"output/temp/{filename}")
                                    checked[value["tier"]][type] = True
                            else:
                                result["skipped"] += 1

                        except Exception as e:
                            self.lists.append(value.get("tierName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "error", Lang.value("common.error"), str(e))
                            result["error"] += 1
                        finally:
                            JSON.save("output/competitivetiers.json", checked)
                            if os.path.exists(f"output/temp/{filename}"):
                                os.remove(f"output/temp/{filename}")
                
                self.result.success(Lang.value("contents.update.competitivetier.success"), Lang.value("contents.update.competitivetier.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.competitivetier.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.competitivetier.failed"))
                self.gui.popup_error(Lang.value("contents.update.competitivetier.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
                JSON.save("output/competitivetiers.json", checked)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.competitivetier.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.competitivetier.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                        self.switch_force,
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists.main(),
                    padding=10,
                    height=200
                ),

                self.result.main()
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
    
    def cargo_data(self):
        seasons = db.Season.make_list()
        
        addition = ""
        for season in seasons:
            addition += "{{Season/CargoStore|uuid="+ season["uuid"] + "|name=" + season["name"] + "|episode=" + season["episode"] + "|act=" + season["act"] + "|parent=" + season["parent"] + "|page=" + season["page"] + "|start=" + season["start"] + "|end=" + season["end"] + "}}\n"
        addition += "[[Category:メタデータ]]"

        with open("output/data/Season.txt", "w", encoding="UTF-8") as f:
            f.write(addition)

        if self.switch_upload.value:  
            self.wiki.login()
            self.wiki.edit_page("Data:Season", addition, editonly=False)
            self.wiki.logout()
        

        tiers = db.CompetitiveTier.make_list()
        
        addition = ""
        for tier in tiers:
            addition += "{{CompetitiveTier/CargoStore|tier=" + str(tier["tier"]) + "|name=" + tier["name"] + "|localized_name=" + tier["localized_name"] + "|division_name=" + tier["division_name"] + "|localized_division_name=" + tier["localized_division_name"] + "|image=" + tier["image"] + "|triangle_down=" + tier["triangle_down"] + "|triangle_up=" + tier["triangle_up"] + "}}\n"
        addition += "[[Category:メタデータ]]"

        with open("output/data/CompetitiveTier.txt", "w", encoding="UTF-8") as f:
            f.write(addition)

        if self.switch_upload.value:  
            self.wiki.login()
            self.wiki.edit_page("Data:CompetitiveTier", addition, editonly=False)
            self.wiki.logout()
        
        

class Agent():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    lists: Gui.UpdateResult
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.lists = self.gui.UpdateResult(self.page)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_force.on_change = on_changed_force
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            result = {"skipped": 0, "success": 0, "warn": 0, "error": 0}
            checked = JSON.read("output/agents.json")

            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.agent.begin"))
                self.loading.state(True)

                os.makedirs("output/temp", exist_ok=True)
                data = JSON.read("api/agents.json")

                login: bool = True
                try:
                    self.wiki.login()
                except Exception as e:
                    login = False
                    self.gui.popup_error(Lang.value("common.wikilogin_failed"), str(e))

                max = len(data)
                count = 1

                for value in data:
                    progress = Lang.value("contents.update.common.progress").format(count=count, max=max)
                    self.update_state(progress)
                    count += 1
                    agent_name = value.get("displayName", {})["ja-JP"]

                    def update(_filename: str, _filedir: str, _type: str, _title: str, _description: str):
                        if checked.get(value["uuid"])==None:
                            checked[value["uuid"]] = {}
                        
                        # update check
                        exist: bool
                        if self.switch_force.value:
                            exist = self.wiki.check_exist(f"File:{_filename}")
                            checked[value["uuid"]][_type] = exist
                        else:
                            exist = checked[value["uuid"]].get(_type, False)
                            if not exist:
                                exist = self.wiki.check_exist(f"File:{_filename}")
                            checked[value["uuid"]][_type] = exist
                        
                        if not exist:
                            # icon link
                            icon: str = _filedir
                            if icon==None:
                                self.lists.append(_title, _filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.agent.warn_notfound"))
                                result["warn"] += 1
                                return
                                
                            # upload
                            if login:
                                Fetch.download(icon, f"output/temp/{_filename}")
                                fd = _filename.replace(" ", "_")
                                self.wiki.upload(fd, _description, f"output/temp/{_filename}")
                                self.lists.append(_title, _filename, "success", Lang.value("common.success"))
                                result["success"] += 1
                                os.remove(f"output/temp/{_filename}")
                                checked[value["uuid"]][_type] = True
                        else:
                            result["skipped"] += 1
                    
                    for type in ["icon", "full", "killfeed", "background", "abilities", "voiceLine"]:
                        icons = []
                        if type=="icon":
                            icons.append([value.get("displayIcon"), None])
                        elif type=="full":
                            icons.append([value.get("fullPortrait"), None])
                        elif type=="killfeed":
                            icons.append([value.get("killfeedPortrait"), None])
                        elif type=="background":
                            icons.append([value.get("background"), None])
                        elif type=="abilities":
                            for ability in value.get("abilities", []):
                                icons.append([ability.get("displayIcon"), ability.get("displayName")["en-US"]])
                        elif type=="voiceLine":
                            if value.get("voiceLine")!=None:
                                icons.append([value.get("voiceLine")["en-US"].get("mediaList", [])[0]["wave"], "en-us"])
                                icons.append([value.get("voiceLine")["ja-JP"].get("mediaList", [])[0]["wave"], "ja-jp"])

                        for icon in icons:
                            try:
                                filename = FileName.agent(value, type, icon[1])

                                title: str = agent_name
                                if type=="voiceLine":
                                    if icon[1]=="ja-jp":
                                        title += f" ({type} ja-jp)"
                                        description = Lang.value(f"contents.update.agent.wiki_description.{type}").format(agent=agent_name, language=Lang.value("contents.update.agent.language.ja-JP")) + Lang.value(f"contents.update.common.wiki_description")
                                    elif icon[1]=="en-us":
                                        title += f" ({type} en-us)"
                                        description = Lang.value(f"contents.update.agent.wiki_description.{type}").format(agent=agent_name, language=Lang.value("contents.update.agent.language.en-US")) + Lang.value(f"contents.update.common.wiki_description")
                                elif type=="abilities":
                                    description: str = Lang.value(f"contents.update.agent.wiki_description.{type}").format(agent=agent_name) + Lang.value(f"contents.update.common.wiki_description")
                                    title += f" ({type} {icon[1]})"
                                else:
                                    description: str = Lang.value(f"contents.update.agent.wiki_description.{type}").format(agent=agent_name) + Lang.value(f"contents.update.common.wiki_description")
                                    title += f" ({type})" 

                                if icon[1]!=None:
                                    update(filename, icon[0], type+"_"+icon[1], title, description)
                                else:
                                    update(filename, icon[0], type, title, description)

                            except Exception as e:
                                self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize")), filename, "error", Lang.value("common.error"), str(e))
                                result["error"] += 1
                            finally:
                                JSON.save("output/agents.json", checked)
                                if os.path.exists(f"output/temp/{filename}"):
                                    os.remove(f"output/temp/{filename}")
                
                self.result.success(Lang.value("contents.update.agent.success"), Lang.value("contents.update.agent.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.agent.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.agent.failed"))
                self.gui.popup_error(Lang.value("contents.update.agent.failed"), str(e))

            finally:
                self.loading.state(False)
                JSON.save("output/agents.json", checked)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.agent.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.agent.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                        self.switch_force
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists.main(),
                    padding=10,
                    height=200
                ),

                self.result.main()
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass

class Weapon():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    lists: Gui.UpdateResult
    switch_force: ft.Switch
    switch_upload: ft.Switch
    switch_video: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.lists = self.gui.UpdateResult(self.page)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)
        self.switch_video = ft.Switch(label=Lang.value("contents.update.weapon.toggle_video_off"), value=False)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")
            self.gui.safe_update(self.switch_force)

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")
            self.gui.safe_update(self.switch_upload)

        def on_changed_video(e):
            if self.switch_video.value:
                self.switch_video.label = Lang.value("contents.update.weapon.toggle_video_on")
            else:
                self.switch_video.label = Lang.value("contents.update.weapon.toggle_video_off")
            self.gui.safe_update(self.switch_video)

        self.switch_force.on_change = on_changed_force
        self.switch_upload.on_change = on_changed_upload
        self.switch_video.on_change = on_changed_video
              
    def main(self):

        def on_clicked(e):
            result = {"skipped": 0, "success": 0, "warn": 0, "error": 0}
            checked = JSON.read("output/weapons.json")

            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.weapon.begin"))
                self.loading.state(True)

                self.cargo_data()

                os.makedirs("output/temp", exist_ok=True)
                data = JSON.read("api/weapons.json")

                login: bool = True
                try:
                    self.wiki.login()
                except Exception as e:
                    login = False
                    self.gui.popup_error(Lang.value("common.wikilogin_failed"), str(e))
                
                w_max = len(data)
                w_count = 1

                for value in data:
                    weapon_name = value.get("displayName", {})["en-US"].lower()
                    weapon_name_locale = value.get("displayName", {})["ja-JP"]
                    weapon = value.get("displayName", {})["en-US"]
                    max = len(value.get("skins", []))
                    count = 1
                    os.makedirs(f"output/weapons/{weapon_name}", exist_ok=True)

                    for skin in value.get("skins", []):
                        skin_name = WikiString.wiki_format(skin.get("displayName", {})["en-US"])
                        try:
                            progress = Lang.value("contents.update.weapon.progress").format(count=count, max=max, weapon_count=w_count, weapon_max=w_max, weapon=value.get("displayName", {}).get(Lang.value("common.localize"), ""))
                            self.update_state(progress)
                            count += 1

                            def update(uuid: str, _filename: str, _filedir: str, _title: str, _description: str, is_video: bool = False, _key: str = "skin"):
                                # update check
                                exist: bool
                                if checked.get(_key)==None:
                                    checked[_key] = {}

                                if not is_video:
                                    if self.switch_force.value:
                                        exist = self.wiki.check_exist(f"File:{_filename}")
                                        checked[_key][uuid] = exist
                                    else:
                                        exist = checked.get(uuid, False)
                                        if not exist:
                                            exist = self.wiki.check_exist(f"File:{_filename}")
                                        checked[_key][uuid] = exist
                                else:
                                    exist = os.path.exists(f"output/weapons/{weapon_name}/{_filename}")
                                
                                if not exist:
                                    # icon link
                                    icon: str = _filedir
                                    if icon==None:
                                        self.lists.append(_title, _filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.weapon.warn_notfound"))
                                        result["warn"] += 1
                                        return
                   
                                    # upload
                                    if login and (not is_video):
                                        Fetch.download(icon, f"output/temp/{_filename}")
                                        fd = _filename.replace(" ", "_")
                                        self.wiki.upload(fd, _description, f"output/temp/{_filename}")
                                        self.lists.append(_title, _filename, "success", Lang.value("common.success"))          
                                        result["success"] += 1
                                        os.remove(f"output/temp/{_filename}")
                                        checked[_key][uuid] = True
                                    elif is_video:
                                        Fetch.download(icon, f"output/weapons/{weapon_name}/{_filename}")
                                else:
                                    result["skipped"] += 1
                            
                            for chroma in skin.get("chromas"):
                                # chromas
                                filename = FileName.weapon(chroma, "icon", skin_name, weapon)
                                try:
                                    title = chroma.get("displayName", {}).get(Lang.value("common.localize"))
                                    description = Lang.value("contents.update.weapon.wiki_description").format(weapon=weapon_name_locale, bundle=self.get_bundle_name(weapon_name_locale, skin)) + Lang.value(f"contents.update.common.wiki_description")
                                    icon: str = None

                                    if chroma.get("fullRender")!=None:
                                        icon = chroma.get("fullRender")
                                    elif  chroma.get("displayIcon")!=None:
                                        icon = chroma.get("displayIcon")
                                    if icon==None:
                                        self.lists.append(chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.weapon.warn_notfound"))
                                        result["warn"] += 1
                                        continue
                                    update(chroma["uuid"], filename, icon, title, description, False)

                                except Exception as e:
                                    self.lists.append(chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, "error", Lang.value("common.error"), str(e))
                                    result["error"] += 1
                                finally:
                                    JSON.save("output/weapons.json", checked)
                                    if os.path.exists(f"output/temp/{filename}"):
                                        os.remove(f"output/temp/{filename}")
                                
                                # swatch
                                filename = FileName.weapon(chroma, "swatch", skin_name, weapon, skin["themeUuid"])
                                try:
                                    title = chroma.get("displayName", {}).get(Lang.value("common.localize"))
                                    description = Lang.value("contents.update.weapon.wiki_description_swatch").format(bundle=self.get_bundle_name(weapon_name_locale, skin)) + Lang.value(f"contents.update.common.wiki_description")
                                    icon: str = None

                                    swatch_exception = [
                                        "34919680-4f00-554b-0c2b-95acca7d0d36", # VALORANT GO! Ghost
                                        "9103fdf7-4361-5ac5-37ae-7cb51f13f45d", # Raze Gear
                                        "4725c2c4-45b7-d9ab-ff4f-a79c3b2dd9ec", # Astra Gear
                                    ]
                                    if chroma.get("swatch")!=None and (not skin["uuid"] in swatch_exception):
                                        icon = chroma["swatch"]
                                        update(chroma["uuid"], filename, icon, title, description, False, "swatch")

                                except Exception as e:
                                    self.lists.append(chroma.get("displayName", {}).get(Lang.value("common.localize")) + " (Swatch)", filename, "error", Lang.value("common.error"), str(e))
                                    result["error"] += 1
                                finally:
                                    JSON.save("output/weapons.json", checked)
                                    if os.path.exists(f"output/temp/{filename}"):
                                        os.remove(f"output/temp/{filename}")
                                
                                filename = FileName.weapon(chroma, "video", skin_name, weapon)
                                try:
                                    if self.switch_video.value==True and chroma.get("streamedVideo")!=None:
                                        title = chroma.get("displayName", {}).get(Lang.value("common.localize")) + Lang.value("contents.update.weapon.video")
                                        description = Lang.value("contents.update.weapon.wiki_description_video").format(bundle=self.get_bundle_name(weapon_name_locale, skin)) + Lang.value(f"contents.update.common.wiki_description")
                                        icon = chroma.get("streamedVideo")
                                        update(chroma["uuid"], filename, icon, title, description, True)
                                except Exception as e:
                                    self.lists.append(chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, "error", Lang.value("common.error"), str(e))
                                    result["error"] += 1
                            
                            # level (video)
                            for level in skin.get("levels"):
                                filename = FileName.weapon(level, "level_video", skin_name, weapon)
                                try:
                                    if self.switch_video.value==True and chroma.get("streamedVideo")!=None:
                                        title = level.get("displayName", {}).get(Lang.value("common.localize")) + Lang.value("contents.update.weapon.video")
                                        description = Lang.value("contents.update.weapon.wiki_description_video").format(bundle=self.get_bundle_name(weapon_name_locale, skin)) + Lang.value(f"contents.update.common.wiki_description")
                                        icon = level.get("streamedVideo")
                                        update(level["uuid"], filename, icon, title, description, True)
                                except Exception as e:
                                    self.lists.append(chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, "error", Lang.value("common.error"), str(e))
                                    result["error"] += 1

                        except Exception as e:
                            self.gui.popup_error(Lang.value("contents.update.weapon.failed"), str(e))
                    w_count += 1

                self.result.success(Lang.value("contents.update.weapon.success"), Lang.value("contents.update.weapon.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.weapon.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.weapon.failed"))
                self.gui.popup_error(Lang.value("contents.update.weapon.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
                JSON.save("output/weapons.json", checked)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.weapon.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.weapon.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                        self.switch_force,
                        self.switch_video
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists.main(),
                    padding=10,
                    height=200
                ),

                self.result.main()
            ],
            spacing=0
        )

    def cargo_data(self):
        count = 0
        weapons = JSON.read("api/weapons.json")
        for weapon in weapons:
            count += 1
            self.update_state(Lang.value("contents.update.weapon.db").format(num=count, max=len(weapons)))

            skins, row = db.Weapon_Skin.make_list(weapon)
            addition = ""

            for uuid in row:
                skin = skins[uuid]
                vp: str = ""
                if skin["vp"]>0:
                    vp = str(skin["vp"])

                addition += "{{Skin/CargoStore|uuid="+ skin["uuid"] + "|name=" + skin["name"] + "|localized_name=" + skin["localized_name"] + "|weapon=" + skin["weapon"] + "|image=" + skin["image"] + "|bundle=" + skin["bundle"] + "|tier=" + skin["tier"] + "|vp=" + vp + "|swatch=" + skin["swatch"] + "|video=" + skin["video"]
                if len(skin["level_upgrade"])>0:
                    addition += "|level_upgrade=" + ",".join(skin["level_upgrade"])
                if len(skin["level_image"])>0:
                    addition += "|level_image=" + ",".join(skin["level_image"])
                if len(skin["level_swatch"])>0:
                    addition += "|level_swatch=" + ",".join(skin["level_swatch"])
                if len(skin["level_video"])>0:
                    addition += "|level_video=" + ",".join(skin["level_video"])
                if len(skin["level_description"])>0:
                    addition += "|level_description=" + ",".join(skin["level_description"])
                addition += "}}\n"
            addition += "[[Category:メタデータ]]"

            with open(f"output/data/Skin."+weapon["displayName"]["en-US"]+".txt", "w", encoding="UTF-8") as f:
                f.write(addition)

            if self.switch_upload.value:
                self.wiki.login()
                self.wiki.edit_page("Data:Skin/" + weapon["displayName"]["en-US"], addition, editonly=False)
                self.wiki.logout()

    def update_state(self, str: str):
        self.state.value = str
        self.gui.safe_update(self.state)
    
    def get_bundle_name(self, weapon_name: str, data: dict):
        name = data.get("displayName", {}).get("ja-JP").replace(weapon_name, "").strip()

        if name=="VCT LOCK//IN":
            name="VCT LOCK//IN (スキンセット)"
        return name

class Levelborder():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    lists: Gui.UpdateResult
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.lists = self.gui.UpdateResult(self.page)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_force.on_change = on_changed_force
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            result = {"skipped": 0, "success": 0, "warn": 0, "error": 0}
            checked = JSON.read("output/levelborders.json")
            
            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.levelborder.begin"))
                self.loading.state(True)

                self.update_state(Lang.value("contents.update.levelborder.db"))
                self.cargo_data()

                os.makedirs("output/temp", exist_ok=True)
                data = JSON.read("api/levelborders.json")

                login: bool = True
                try:
                    self.wiki.login()
                except Exception as e:
                    login = False
                    self.gui.popup_error(Lang.value("common.wikilogin_failed"), str(e))

                max = len(data)
                count = 1

                for value in data:
                    progress = Lang.value("contents.update.common.progress").format(count=count, max=max)
                    self.update_state(progress)
                    count += 1

                    for type in ["levelNumberAppearance", "smallPlayerCardAppearance"]:
                        try:
                            filename = FileName.levelborder(value, type)
                            if checked.get(value["uuid"])==None:
                                checked[value["uuid"]] = {}

                            # update check
                            exist: bool
                            if self.switch_force.value:
                                exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["uuid"]][type] = exist
                            else:
                                exist = checked[value["uuid"]].get(type, False)
                                if not exist:
                                    exist = self.wiki.check_exist(f"File:{filename}")
                                checked[value["uuid"]][type] = exist
                            
                            if not exist:
                                # icon link
                                icon: str = None
                                if value.get(f"{type}")!=None:
                                    icon = value.get(f"{type}Art")
                                if icon==None:
                                    self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "warn", Lang.value("common.warn"), Lang.value("contents.update.playercard.warn_notfound"))
                                    result["warn"] += 1
                                    continue
                            
                                # upload
                                if login:
                                    Fetch.download(icon, f"output/temp/{filename}")
                                    fd = filename.replace(" ", "_")
                                    self.wiki.upload(fd, Lang.value(f"contents.update.levelborder.wiki_description.{type}") + Lang.value(f"contents.update.common.wiki_description"), f"output/playercards/{type}/{filename}")
                                    self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "success", Lang.value("common.success"))
                                    result["success"] += 1
                                    os.remove(f"output/temp/{filename}")
                                    checked[value["uuid"]][type] = True
                            else:
                                result["skipped"] += 1

                        except Exception as e:
                            self.lists.append(value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, "error", Lang.value("common.error"), str(e))
                            result["error"] += 1
                        finally:
                            JSON.save("output/levelborders.json", checked)
                            if os.path.exists(f"output/temp/{filename}"):
                                os.remove(f"output/temp/{filename}")
                
                self.result.success(Lang.value("contents.update.levelborder.success"), Lang.value("contents.update.playercard.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.levelborder.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.levelborder.failed"))
                self.gui.popup_error(Lang.value("contents.update.levelborder.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
                JSON.save("output/levelborders.json", checked)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.levelborder.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.levelborder.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                        self.switch_force,
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists.main(),
                    padding=10,
                    height=200
                ),

                self.result.main()
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
    
    def cargo_data(self):
        borders, row = db.Levelborder.make_list()
        
        addition = ""
        for uuid in row:
            border = borders[uuid]
            addition += "{{Levelborder/CargoStore|uuid="+ border["uuid"] + "|localized_name=" + border["localized_name"] + "|level=" + str(border["level"]) + "|border=" + border["border"] + "|frame=" + border["frame"] + "}}\n"
        addition += "[[Category:メタデータ]]"

        with open("output/data/Levelborder.txt", "w", encoding="UTF-8") as f:
            f.write(addition)

        if self.switch_upload.value:  
            self.wiki.login()
            self.wiki.edit_page("Data:Levelborder", addition, editonly=False)
            self.wiki.logout()
    
class Playertitle():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            self.cargo_data()
            
            try:
                self.result.clear()
                self.update_state(Lang.value("contents.update.playertitle.begin"))
                self.loading.state(True)

                self.update_state(Lang.value("contents.update.playertitle.db"))

                self.result.success(Lang.value("contents.update.playertitle.success"))
                self.gui.popup_success(Lang.value("contents.update.playertitle.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.playertitle.failed"))
                self.gui.popup_error(Lang.value("contents.update.playertitle.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.playertitle.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.playertitle.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),

                self.result.main()
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
    
    def cargo_data(self):
        titles, row = db.Playertitle.make_list()
        
        for key,values in row.items():
            addition = ""
            for uuid in values:
                title = titles[uuid]
                addition += "{{Playertitle/CargoStore|uuid="+ title["uuid"] + "|name=" + title["name"] + "|localized_name=" + title["localized_name"] + "|title=" + title["title"]
                if len(title["relation"])>0:
                    addition += "|relation=" + ",".join(title["relation"])
                addition += "|bundle=" + title["bundle"] + "|description=" + title["description"] + "}}\n"
            addition += "[[Category:メタデータ]]"

            with open(f"output/data/Playertitle.{key}.txt", "w", encoding="UTF-8") as f:
                f.write(addition)
            
            if self.switch_upload.value:  
                self.wiki.login()
                self.wiki.edit_page(f"Data:Playertitle/{key}", addition, editonly=False)
                self.wiki.logout()

class Contract():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            try:
                self.switch_upload.update()
            except Exception as e:
                pass
            
        self.switch_upload.on_change = on_changed_upload
              
    def main(self):

        def on_clicked(e):
            
            try:
                self.result.clear()
                self.update_state(Lang.value("contents.update.contract.begin"))
                self.loading.state(True)
                
                self.cargo_data()

                self.result.success(Lang.value("contents.update.contract.success"))
                self.gui.popup_success(Lang.value("contents.update.contract.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.contract.failed"))
                self.gui.popup_error(Lang.value("contents.update.contract.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.update.contract.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.update.contract.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_upload,
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.update.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading.main(),
                        self.state
                    ],
                ),

                self.result.main()
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
    
    def cargo_data(self):
        count = 1
        contracts = JSON.read("api/contracts.json")

        # Contract
        dbs = db.Contract.make_list_parent(contracts)
        addition = ""
        for data in dbs:
            addition += "{{Contract/CargoStore|name="+ data["name"] + "|localized_name=" + data["localized_name"] + "|uuid=" + data["uuid"] + "|start=" + data["start"] + "|end=" + data["end"] + "|relation=" + data["relation"] + "|relation_type=" + data["relation_type"] + "}}\n"
        addition += "\n== 子ページ ==\n{{Special:PrefixIndex/Data:Contract/}}\n\n[[Category:メタデータ]]"

        with open(f"output/data/Contract.txt", "w", encoding="UTF-8") as f:
            f.write(addition)
        
        if self.switch_upload.value:  
            self.wiki.login()
            self.wiki.edit_page(f"Data:Contract", addition, editonly=False)
            self.wiki.logout()

        # Contract Item
        for v in contracts:
            self.update_state(Lang.value("contents.update.contract.db").format(num=count, max=len(contracts)))
            dbs = db.Contract.make_list(v)
            key = v["displayName"]["en-US"]
            if key=="IGNITION : ACT 1":
                key = "IGNITION: ACT 1"

            addition = ""
            for data in dbs:
                addition += "{{ContractItem/CargoStore|idx="+ data["idx"] + "|name=" + data["name"] + "|type=" + data["type"] + "|tier=" + data["tier"] + "|amount=" + data["amount"]
                if data["free"]:
                    addition += "|free=yes"
                else:
                    addition += "|free=no"
                
                if data["epilogue"]:
                    addition += "|epilogue=yes"
                else:
                    addition += "|epilogue=no"
                addition += "|xp=" + data["xp"] + "|vp=" + data["vp"] + "|kc=" + data["kc"] + "|contract=" + data["contract"] + "}}\n"
            addition += "[[Category:メタデータ]]"

            with open(f"output/data/Contract.{WikiString.wiki_format(key)}.txt", "w", encoding="UTF-8") as f:
                f.write(addition)
            
            if self.switch_upload.value:  
                self.wiki.login()
                self.wiki.edit_page(f"Data:Contract/{key}", addition, editonly=False)
                self.wiki.logout()
            
            count += 1
 