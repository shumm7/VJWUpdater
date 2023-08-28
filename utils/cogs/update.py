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
        self.agent = Agent(wiki, gui, page)
        self.weapon = Weapon(wiki, gui, page)
    
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
                self.weapon.main()
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
                                self.wiki.upload(fd, Lang.value(f"contents.update.playercard.wiki_description.{type}") + Lang.value(f"contents.update.common.wiki_description"), f"output/playercards/{type}/{filename}")
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
                            self.wiki.upload(fd, Lang.value("contents.update.spray.wiki_description") + Lang.value(f"contents.update.common.wiki_description"), f"output/sprays/{filename}")
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
                            self.wiki.upload(fd, Lang.value("contents.update.buddy.wiki_description") + Lang.value(f"contents.update.common.wiki_description"), f"output/buddies/{filename}")
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
                                self.wiki.upload(fd, Lang.value(f"contents.update.competitivetier.wiki_description.{type}") + Lang.value(f"contents.update.common.wiki_description"), f"output/competitivetiers/{filename}")
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
                self.update_state(Lang.value("contents.update.agent.begin"))
                self.loading.state(True)

                os.makedirs("output/agents", exist_ok=True)
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

                    def update(_filename: str, _filedir: str, _title: str, _description: str):
                        # update check
                        exist: bool
                        download: bool = False
                        if self.switch_force.value:
                            exist = self.wiki.check_exist(f"File:{_filename}")
                        else:
                            exist = os.path.exists(f"output/agents/{_filename}")
                            if not exist:
                                download = True
                                exist = self.wiki.check_exist(f"File:{_filename}")
                        
                        # icon link
                        icon: str = _filedir
                        if icon==None:
                            self.lists.append(value, _title, _filename, f"output/agents/{_filename}", "warn", Lang.value("common.warn"), Lang.value("contents.update.agent.warn_notfound"))
                            result["warn"] += 1
                            return
                        
                        # download
                        if download:
                            Fetch.download(icon, f"output/agents/{_filename}")
                                
                        # upload
                        if (not exist) and login:
                            fd = _filename.replace(" ", "_")
                            self.wiki.upload(fd, _description, f"output/agents/{_filename}")
                            self.lists.append(value, _title, _filename, f"output/agents/{_filename}", "success", Lang.value("common.success"))
                            
                            result["success"] += 1
                        else:
                            self.lists.append(value, _title, _filename, f"output/agents/{_filename}", "skipped", Lang.value("common.skipped"))
                            result["skipped"] += 1
                    
                    for type in ["icon", "full", "killfeed", "background", "abilities", "voiceLine"]:
                        variable: str = None
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
                            icons.append([value.get("voiceLine")["en-US"].get("mediaList", [])[0]["wave"], "en-us"])
                            icons.append([value.get("voiceLine")["ja-JP"].get("mediaList", [])[0]["wave"], "ja-jp"])

                        for icon in icons:
                            try:
                                filename = self.get_filename(value, type, icon[1])

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

                                update(filename, icon[0], title, description)
                            except Exception as e:
                                self.lists.append(value, value.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/agents/{filename}", "error", Lang.value("common.error"), str(e))
                                result["error"] += 1
                            
                
                self.result.success(Lang.value("contents.update.agent.success"), Lang.value("contents.update.agent.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"]))
                self.gui.popup_success(Lang.value("contents.update.agent.success"))

            except Exception as e:
                self.result.error(Lang.value("contents.update.agent.failed"))
                self.gui.popup_error(Lang.value("contents.update.agent.failed"), str(e))

            finally:
                self.loading.state(False)
    
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
        
    def get_filename(self, data: dict, tp: str, variable: str = None) -> str:
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
        self.lists = self.gui.UpdateResult(self.page, "output/buddies")
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
            try:
                self.lists.clear()
                self.result.clear()
                self.update_state(Lang.value("contents.update.weapon.begin"))
                self.loading.state(True)

                os.makedirs("output/weapons", exist_ok=True)
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

                            def update(_filename: str, _filedir: str, _title: str, _description: str, is_video: bool = False):
                                # update check
                                exist: bool
                                download: bool = False

                                if not is_video:
                                    if self.switch_force.value:
                                        exist = self.wiki.check_exist(f"File:{_filename}")
                                    else:
                                        exist = os.path.exists(f"output/weapons/{weapon_name}/{_filename}")
                                        if not exist:
                                            download = True
                                            exist = self.wiki.check_exist(f"File:{_filename}")
                                else:
                                    exist = os.path.exists(f"output/weapons/{weapon_name}/{_filename}")
                                    if not exist:
                                        download = True
                                
                                # icon link
                                icon: str = _filedir
                                if icon==None:
                                    self.lists.append(value, _title, _filename, f"output/weapons/{weapon_name}/{_filename}", "warn", Lang.value("common.warn"), Lang.value("contents.update.weapon.warn_notfound"))
                                    result["warn"] += 1
                                    return
                                
                                # download
                                if download:
                                    Fetch.download(icon, f"output/weapons/{weapon_name}/{_filename}")
                   
                                # upload
                                if (not exist) and login and (not is_video):
                                    fd = _filename.replace(" ", "_")
                                    self.wiki.upload(fd, _description, f"output/weapons/{weapon_name}/{_filename}")
                                    self.lists.append(value, _title, _filename, f"output/weapons/{weapon_name}/{_filename}", "success", Lang.value("common.success"))
                                    
                                    result["success"] += 1
                                else:
                                    self.lists.append(value, _title, _filename, f"output/weapons/{weapon_name}/{_filename}", "skipped", Lang.value("common.skipped"))
                                    result["skipped"] += 1
                            
                            for chroma in skin.get("chromas"):
                                filename = self.get_filename(chroma, "icon", skin_name, weapon)
                                try:
                                    title = chroma.get("displayName", {}).get(Lang.value("common.localize"))
                                    description = Lang.value("contents.update.weapon.wiki_description").format(weapon=weapon_name_locale, bundle=self.get_bundle_name(weapon_name_locale, skin)) + Lang.value(f"contents.update.common.wiki_description")
                                    icon: str = None

                                    if chroma.get("fullRender")!=None:
                                        icon = chroma.get("fullRender")
                                    elif  chroma.get("displayIcon")!=None:
                                        icon = chroma.get("displayIcon")
                                    if icon==None:
                                        self.lists.append(chroma, chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/weapons/{weapon_name}/{filename}", "warn", Lang.value("common.warn"), Lang.value("contents.update.weapon.warn_notfound"))
                                        result["warn"] += 1
                                        continue
                                    update(filename, icon, title, description, False)
                                except Exception as e:
                                    self.lists.append(chroma, chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/weapons/{weapon_name}/{filename}", "error", Lang.value("common.error"), str(e))
                                    result["error"] += 1

                                filename = self.get_filename(chroma, "video", skin_name, weapon)
                                try:
                                    if self.switch_video.value==True and chroma.get("streamedVideo")!=None:
                                        title = chroma.get("displayName", {}).get(Lang.value("common.localize")) + Lang.value("contents.update.weapon.video")
                                        description = Lang.value("contents.update.weapon.wiki_description_video").format(bundle=self.get_bundle_name(weapon_name_locale, skin)) + Lang.value(f"contents.update.common.wiki_description")
                                        icon = chroma.get("streamedVideo")
                                        update(filename, icon, title, description, True)
                                except Exception as e:
                                    self.lists.append(chroma, chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/weapons/{weapon_name}/{filename}", "error", Lang.value("common.error"), str(e))
                                    result["error"] += 1
                            
                            for level in skin.get("levels"):
                                filename = self.get_filename(level, "level_video", skin_name, weapon)
                                try:
                                    if self.switch_video.value==True and chroma.get("streamedVideo")!=None:
                                        title = level.get("displayName", {}).get(Lang.value("common.localize")) + Lang.value("contents.update.weapon.video")
                                        description = Lang.value("contents.update.weapon.wiki_description_video").format(bundle=self.get_bundle_name(weapon_name_locale, skin)) + Lang.value(f"contents.update.common.wiki_description")
                                        icon = level.get("streamedVideo")
                                        update(filename, icon, title, description, True)
                                except Exception as e:
                                    self.lists.append(chroma, chroma.get("displayName", {}).get(Lang.value("common.localize")), filename, f"output/weapons/{weapon_name}/{filename}", "error", Lang.value("common.error"), str(e))
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

    def update_state(self, str: str):
        self.state.value = str
        self.gui.safe_update(self.state)
        
    def get_filename(self, data: dict, tp: str, skin_name: str, weapon_name: str) -> str:
        name: str = data.get("displayName", {})["en-US"]

        if name==None:
            raise Exception("Failed to get item's name.")
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
    
    def get_bundle_name(self, weapon_name: str, data: dict):
        name = data.get("displayName", {}).get("ja-JP").replace(weapon_name, "").strip()

        if name=="VCT LOCK//IN":
            name="VCT LOCK//IN (スキンセット)"
        return name
