import flet as ft
import os
from utils.tools.localize import Lang
from utils.tools.json import JSON
from utils.tools.fetch import Fetch
from utils.tools.wiki import Wiki, WikiString
from utils.tools.gui import Gui


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
    
    def main(self):
        self.content = ft.Container(self.playercard.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index

            if i==0:
                self.content.content = self.playercard.main()
            elif i==1:
                self.content.content = self.spray.main()
            elif i==2:
                self.content.content = self.buddy.main()
            elif i==3:
                self.content.content = self.competitivetier.main()
            try:
                self.content.update()
            except Exception as e:
                pass
            

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
        self.lists = self.gui.UpdateResult(self.page, "output/playercards")
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
            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.playercard.begin"))
                self.loading.state(True)

                os.makedirs("output/playercards", exist_ok=True)
                os.makedirs("output/playercards/wide", exist_ok=True)
                os.makedirs("output/playercards/small", exist_ok=True)
                os.makedirs("output/playercards/large", exist_ok=True)
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
                            filename = self.get_filename(value, type)

                            # update check
                            exist: bool
                            download: bool = False
                            if self.switch_force.value:
                                exist = self.wiki.check_exist(f"File:{filename}")
                            else:
                                exist = os.path.exists(f"output/playercards/{type}/{filename}")
                                if not exist:
                                    download = True
                                    exist = self.wiki.check_exist(f"File:{filename}")
                            
                            # icon link
                            icon: str = None
                            if value.get(f"{type}Art")!=None:
                                icon = value.get(f"{type}Art")
                            elif type=="small" and value.get(f"smallArt")==None:
                                icon = value.get("displayIcon")
                            if icon==None:
                                self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, f"output/playercards/{type}/{filename}", "warn", Lang.value("common.warn"), Lang.value("contents.update.playercard.warn_notfound"))
                                result["warn"] += 1
                                continue
                            
                            # download
                            if download:
                                Fetch.download(icon, f"output/playercards/{type}/{filename}")
                                    
                            # upload
                            if (not exist) and login:
                                fd = filename.replace(" ", "_")
                                self.wiki.upload(fd, Lang.value(f"contents.update.playercard.wiki_description.{type}"), f"output/playercards/{type}/{filename}")
                                self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, f"output/playercards/{type}/{filename}", "success", Lang.value("common.success"))
                                
                                result["success"] += 1
                            else:
                                self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")) or "", filename, f"output/playercards/{type}/{filename}", "skipped", Lang.value("common.skipped"))
                                result["skipped"] += 1

                        except Exception as e:
                            self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, f"output/playercards/{type}/{filename}", "error", Lang.value("common.error"), str(e))
                            result["error"] += 1
                
                self.result.success(Lang.value("contents.update.playercard.success"), Lang.value("contents.update.playercard.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.playercard.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.playercard.failed"))
                self.gui.popup_error(Lang.value("contents.update.playercard.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
    
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

    def get_filename(self, data: dict, type: str) -> str:
        name = data.get("displayName", {})["en-US"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
        
        name = WikiString.wiki_format(name)

        if type=="small":
            return f"{name} icon.png"
        elif type=="wide":
            return f"{name} wide.png"
        elif type=="large":
            return f"{name}.png"

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
        self.lists = self.gui.UpdateResult(self.page, "output/sprays")
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
            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.spray.begin"))
                self.loading.state(True)

                os.makedirs("output/sprays", exist_ok=True)
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
                    try:
                        progress = Lang.value("contents.update.common.progress").format(count=count, max=max)
                        self.update_state(progress)
                        count += 1
                        filename = self.get_filename(value)

                        # update check
                        exist: bool
                        download: bool = False
                        if self.switch_force.value:
                            exist = self.wiki.check_exist(f"File:{filename}")
                        else:
                            exist = os.path.exists(f"output/sprays/{filename}")
                            if not exist:
                                download = True
                                exist = self.wiki.check_exist(f"File:{filename}")
                        
                        # icon link
                        icon: str = None
                        if value.get("animationPng")!=None:
                            icon = value.get("animationPng")
                        elif value.get("fullTransparentIcon")!=None:
                            icon = value.get("fullTransparentIcon")
                        elif value.get("fullIcon")!=None:
                            icon = value.get("fullIcon")
                        if icon==None:
                            self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")) or "", filename, f"output/sprays/{filename}", "warn", Lang.value("common.warn"), Lang.value("contents.update.spray.warn_notfound"))
                            result["warn"] += 1
                            continue
                        
                        # download
                        if download:
                            Fetch.download(icon, f"output/sprays/{filename}")
                                
                        # upload
                        if (not exist) and login:
                            fd = filename.replace(" ", "_")
                            self.wiki.upload(fd, Lang.value("contents.update.spray.wiki_description"), f"output/sprays/{filename}")
                            self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")) or "", filename, f"output/sprays/{filename}", "success", Lang.value("common.success"))
                            result["success"] += 1
                        else:
                            self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")) or "", filename, f"output/sprays/{filename}", "skipped", Lang.value("common.skipped"))
                            result["skipped"] += 1

                    except Exception as e:
                        self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")) or "", filename, f"output/sprays/{filename}", "error", Lang.value("common.error"), str(e))
                        result["error"] += 1
                
                self.result.success(Lang.value("contents.update.spray.success"), Lang.value("contents.update.spray.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.spray.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.spray.failed"))
                self.gui.popup_error(Lang.value("contents.update.spray.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
    
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

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
      
    def get_filename(self, data: dict) -> str:
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
        
        name = WikiString.wiki_format(name)
        return f"{name}.png"

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
        self.lists = self.gui.UpdateResult(self.page, "output/buddies")
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
            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.buddy.begin"))
                self.loading.state(True)

                os.makedirs("output/buddies", exist_ok=True)
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
                        filename = self.get_filename(value)

                        # update check
                        exist: bool
                        download: bool = False
                        if self.switch_force.value:
                            exist = self.wiki.check_exist(f"File:{filename}")
                        else:
                            exist = os.path.exists(f"output/buddies/{filename}")
                            if not exist:
                                download = True
                                exist = self.wiki.check_exist(f"File:{filename}")
                        
                        # icon link
                        icon: str = None
                        if value.get("displayIcon")!=None:
                            icon = value.get("displayIcon")
                        if icon==None:
                            self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/buddies/{filename}", "warn", Lang.value("common.warn"), Lang.value("contents.update.buddy.warn_notfound"))
                            result["warn"] += 1
                            continue
                        
                        # download
                        if download:
                            Fetch.download(icon, f"output/buddies/{filename}")
                                
                        # upload
                        if (not exist) and login:
                            fd = filename.replace(" ", "_")
                            self.wiki.upload(fd, Lang.value("contents.update.buddy.wiki_description"), f"output/buddies/{filename}")
                            self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/buddies/{filename}", "success", Lang.value("common.success"))
                            
                            result["success"] += 1
                        else:
                            self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")) or "", filename, f"output/buddies/{filename}", "skipped", Lang.value("common.skipped"))
                            result["skipped"] += 1

                    except Exception as e:
                        self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/buddies/{filename}", "error", Lang.value("common.error"), str(e))
                        result["error"] += 1
                
                self.result.success(Lang.value("contents.update.buddy.success"), Lang.value("contents.update.buddy.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.buddy.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.buddy.failed"))
                self.gui.popup_error(Lang.value("contents.update.buddy.failed"), str(e))

            finally:
                self.loading.state(False)
    
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
        
    def get_filename(self, data: dict) -> str:
        name = data.get("displayName", {})["en-US"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
        
        name = WikiString.wiki_format(name)
        return f"{name}.png"

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
        self.lists = self.gui.UpdateResult(self.page, "output/competitivetiers")
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
            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.competitivetier.begin"))
                self.loading.state(True)

                os.makedirs("output/competitivetiers", exist_ok=True)
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
                            filename = self.get_filename(value, type)

                            # update check
                            exist: bool
                            download: bool = False
                            if self.switch_force.value:
                                exist = self.wiki.check_exist(f"File:{filename}")
                            else:
                                exist = os.path.exists(f"output/competitivetiers/{filename}")
                                if not exist:
                                    download = True
                                    exist = self.wiki.check_exist(f"File:{filename}")
                            
                            # icon link
                            icon: str = None
                            if value.get(f"{type}Icon")!=None:
                                icon = value.get(f"{type}Icon")
                            if icon==None:
                                self.lists.append(value, value.get("tierName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, f"output/competitivetiers/{filename}", "warn", Lang.value("common.warn"), Lang.value("contents.update.competitivetier.warn_notfound"))
                                result["warn"] += 1
                                continue
                            
                            # download
                            if download:
                                Fetch.download(icon, f"output/competitivetiers/{filename}")
                                    
                            # upload
                            if (not exist) and login:
                                fd = filename.replace(" ", "_")
                                self.wiki.upload(fd, Lang.value(f"contents.update.competitivetier.wiki_description.{type}"), f"output/competitivetiers/{filename}")
                                self.lists.append(value, value.get("tierName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, f"output/competitivetiers/{filename}", "success", Lang.value("common.success"))
                                
                                result["success"] += 1
                            else:
                                self.lists.append(value, value.get("tierName", {}).get(Lang.value("common.localize")) or "", filename, f"output/competitivetiers/{filename}", "skipped", Lang.value("common.skipped"))
                                result["skipped"] += 1

                        except Exception as e:
                            self.lists.append(value, value.get("tierName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", filename, f"output/competitivetiers/{filename}", "error", Lang.value("common.error"), str(e))
                            result["error"] += 1
                
                self.result.success(Lang.value("contents.update.competitivetier.success"), Lang.value("contents.update.competitivetier.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.competitivetier.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.competitivetier.failed"))
                self.gui.popup_error(Lang.value("contents.update.competitivetier.failed"), str(e))

            finally:
                self.loading.state(False)
                self.update_state("")
    
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

    def get_filename(self, data: dict, type: str) -> str:
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

