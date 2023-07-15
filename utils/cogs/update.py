import flet as ft
import os
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData, Lang, Config
from utils.api import API
from utils.wiki import Wiki
from utils.gui import Gui


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
    
    def main(self):
        self.content = ft.Container(self.spray.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index

            if i==0:
                self.content.content = self.playercard.main()
            elif i==1:
                self.content.content = self.spray.main()
            elif i==2:
                self.content.content = self.buddy.main()
            try:
                self.content.update()
            except Exception as e:
                pass
            

        return ft.Row(
            [
                ft.NavigationRail(
                    selected_index=1,
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
    loading: ft.Container
    state: ft.Text
    lists: ft.ListView
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = ft.Container()
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = ft.ListTile()
        self.lists = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            self.switch_force.update()
            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            self.switch_upload.update()
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
                self.clear_list()
                self.clear_result()
                self.update_state(Lang.value("contents.update.playercard.begin"))
                self.loading.content = ft.ProgressRing(width=16, height=16, stroke_width = 2)
                try:
                    self.loading.update()
                except Exception as e:
                    pass

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
                                self.add_item(value, "warn", filename, Lang.value("contents.update.playercard.warn_notfound"), type)
                                result["warn"] += 1
                                continue
                            
                            # download
                            if download:
                                Fetch.download(icon, f"output/playercards/{type}/{filename}")
                                    
                            # upload
                            if (not exist) and login:
                                fd = filename.replace(" ", "_")
                                self.wiki.upload(fd, Lang.value(f"contents.update.playercard.wiki_description.{type}"), f"output/playercards/{type}/{filename}")
                                self.add_item(value, "success", filename, Lang.value("common.success"), type)
                                result["success"] += 1
                            else:
                                result["skipped"] += 1

                        except Exception as e:
                            self.add_item(value, "error", filename, Lang.value("common.error"), type)
                            self.gui.popup_error(Lang.value("contents.update.playercard.failed"), str(e))
                            result["error"] += 1
                
                self.update_result(
                    Lang.value("contents.update.playercard.success"), 
                    Lang.value("contents.update.playercard.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"])
                )
                self.gui.popup_success(Lang.value("contents.update.playercard.success"))

            except Exception as e:
                self.gui.popup_error(Lang.value("contents.update.playercard.failed"), str(e))

            finally:
                self.loading.content = None
                try:
                    self.loading.update()
                except Exception as e:
                    pass
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
                        self.loading,
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists,
                    padding=10,
                    height=200
                ),

                self.result
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass

    def clear_list(self):
        self.lists.controls.clear()
        self.lists.update()
        try:
            self.lists.update()
        except Exception as e:
            pass
    
    def append_list(self, ctrl: ft.Control):
        self.lists.controls.append(ctrl)
        self.lists.update()
        try:
            self.lists.update()
        except Exception as e:
            pass
    
    def clear_result(self):
        self.result.title = None
        self.result.subtitle = None
        self.result.leading = None

        try:
            self.result.update()
        except Exception as e:
            pass

    def update_result(self, title: str, subtitle: str):
        self.result.title = ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
        self.result.subtitle = ft.Text(subtitle, style=ft.TextThemeStyle.BODY_SMALL)
        self.result.leading = ft.Icon(ft.icons.CHECK, color="green")

        try:
            self.result.update()
        except Exception as e:
            pass

    def add_item(self, value: dict, mode: str, filename: str, reason: str, type: str):
        def close_dialog(e):
            dialog.open = False
            try:
                self.page.update()
            except Exception as e:
                pass

        def open_dialog(e):
            self.page.dialog = dialog
            dialog.open = True
            try:
                self.page.update()
            except Exception as e:
                pass
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(filename),
            content=ft.Column([
                ft.Text(value.get("displayName", {}).get(Lang.value("common.localize")) or "", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Row([
                    ft.Text(value.get("uuid", ""), style=ft.TextThemeStyle.BODY_SMALL),
                    self.gui.copy_button(value.get("uuid", ""))
                ]),
                ft.Image(src=f"output/playercards/{type}/{filename}", width=200, height=200, fit=ft.ImageFit.CONTAIN)
            ]),
            actions=[
                ft.TextButton(Lang.value("common.ok"), on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        imagebutton = ft.IconButton(
            icon=ft.icons.PREVIEW,
            tooltip=Lang.value("common.preview"),
            on_click = open_dialog
        ) 
        iconbutton: ft.IconButton

        if mode=="success":
            iconbutton = ft.IconButton(icon=ft.icons.CHECK, icon_color="green", tooltip=reason)
        elif mode=="skipped":
            iconbutton = ft.IconButton(icon=ft.icons.NEARBY_ERROR, icon_color="yellow", tooltip=reason)
        elif mode=="warn":
            iconbutton = ft.IconButton(icon=ft.icons.WARNING, icon_color="yellow", tooltip=reason)
        elif mode=="error":
            iconbutton = ft.IconButton(icon=ft.icons.ERROR, icon_color="red", tooltip=reason)

        self.append_list(
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Row(
                            controls=[
                                ft.Row([
                                    iconbutton,
                                    ft.Text(value.get("displayName", {}).get(Lang.value("common.localize"))+f" ({type})" or "", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM)
                                ]),
                                imagebutton
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row([
                            ft.Text(filename, style=ft.TextThemeStyle.BODY_SMALL)
                        ])
                    ]),
                    padding=3
                )
            )
        )    
        
    def get_filename(self, data: dict, type: str) -> str:
        name = data.get("displayName", {})["en-US"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
        
        name = String.wiki_format(name)

        if type=="small":
            return f"{name} icon.png"
        elif type=="wide":
            return f"{name} wide.png"
        elif type=="large":
            return f"{name}.png"

class Spray():
    page: ft.Page
    loading: ft.Container
    state: ft.Text
    lists: ft.ListView
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = ft.Container()
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = ft.ListTile()
        self.lists = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            self.switch_force.update()
            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            self.switch_upload.update()
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
                self.clear_list()
                self.clear_result()
                self.update_state(Lang.value("contents.update.spray.begin"))
                self.loading.content = ft.ProgressRing(width=16, height=16, stroke_width = 2)
                try:
                    self.loading.update()
                except Exception as e:
                    pass

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
                            self.add_item(value, "warn", filename, Lang.value("contents.update.spray.warn_notfound"))
                            result["warn"] += 1
                            continue
                        
                        # download
                        if download:
                            Fetch.download(icon, f"output/sprays/{filename}")
                                
                        # upload
                        if (not exist) and login:
                            fd = filename.replace(" ", "_")
                            self.wiki.upload(fd, Lang.value("contents.update.spray.wiki_description"), f"output/sprays/{filename}")
                            self.add_item(value, "success", filename, Lang.value("common.success"))
                            result["success"] += 1
                        else:
                            result["skipped"] += 1

                    except Exception as e:
                        self.add_item(value, "error", filename, Lang.value("common.error"))
                        self.gui.popup_error(Lang.value("contents.update.spray.failed"), str(e))
                        result["error"] += 1
                
                self.update_result(
                    Lang.value("contents.update.spray.success"), 
                    Lang.value("contents.update.spray.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"])
                )
                self.gui.popup_success(Lang.value("contents.update.spray.success"))

            except Exception as e:
                self.gui.popup_error(Lang.value("contents.update.spray.failed"), str(e))

            finally:
                self.loading.content = None
                try:
                    self.loading.update()
                except Exception as e:
                    pass
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
                        self.loading,
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists,
                    padding=10,
                    height=200
                ),

                self.result
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass

    def clear_list(self):
        self.lists.controls.clear()
        self.lists.update()
        try:
            self.lists.update()
        except Exception as e:
            pass
    
    def append_list(self, ctrl: ft.Control):
        self.lists.controls.append(ctrl)
        self.lists.update()
        try:
            self.lists.update()
        except Exception as e:
            pass
    
    def clear_result(self):
        self.result.title = None
        self.result.subtitle = None
        self.result.leading = None

        try:
            self.result.update()
        except Exception as e:
            pass

    def update_result(self, title: str, subtitle: str):
        self.result.title = ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
        self.result.subtitle = ft.Text(subtitle, style=ft.TextThemeStyle.BODY_SMALL)
        self.result.leading = ft.Icon(ft.icons.CHECK, color="green")

        try:
            self.result.update()
        except Exception as e:
            pass

    def add_item(self, value: dict, mode: str, filename: str, reason: str):
        def close_dialog(e):
            dialog.open = False
            try:
                self.page.update()
            except Exception as e:
                pass

        def open_dialog(e):
            self.page.dialog = dialog
            dialog.open = True
            try:
                self.page.update()
            except Exception as e:
                pass
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(filename),
            content=ft.Column([
                ft.Text(value.get("displayName", {}).get(Lang.value("common.localize")) or "", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Row([
                    ft.Text(value.get("uuid", ""), style=ft.TextThemeStyle.BODY_SMALL),
                    self.gui.copy_button(value.get("uuid", ""))
                ]),
                ft.Image(src=f"output/sprays/{filename}", width=200, height=200, fit=ft.ImageFit.CONTAIN)
            ]),
            actions=[
                ft.TextButton(Lang.value("common.ok"), on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        imagebutton = ft.IconButton(
            icon=ft.icons.PREVIEW,
            tooltip=Lang.value("common.preview"),
            on_click = open_dialog
        ) 
        iconbutton: ft.IconButton

        if mode=="success":
            iconbutton = ft.IconButton(icon=ft.icons.CHECK, icon_color="green", tooltip=reason)
        elif mode=="skipped":
            iconbutton = ft.IconButton(icon=ft.icons.NEARBY_ERROR, icon_color="yellow", tooltip=reason)
        elif mode=="warn":
            iconbutton = ft.IconButton(icon=ft.icons.WARNING, icon_color="yellow", tooltip=reason)
        elif mode=="error":
            iconbutton = ft.IconButton(icon=ft.icons.ERROR, icon_color="red", tooltip=reason)

        self.append_list(
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Row(
                            controls=[
                                ft.Row([
                                    iconbutton,
                                    ft.Text(value.get("displayName", {}).get(Lang.value("common.localize")) or "", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM)
                                ]),
                                imagebutton
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row([
                            ft.Text(filename, style=ft.TextThemeStyle.BODY_SMALL)
                        ])
                    ]),
                    padding=3
                )
            )
        )    
        
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
        
        name = String.wiki_format(name)
        return f"{name}.png"

class Buddy():
    page: ft.Page
    loading: ft.Container
    state: ft.Text
    lists: ft.ListView
    switch_force: ft.Switch
    switch_upload: ft.Switch

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = ft.Container()
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = ft.ListTile()
        self.lists = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.switch_force = ft.Switch(label=Lang.value("contents.update.common.toggle_force_off"), value=False)
        self.switch_upload = ft.Switch(label=Lang.value("contents.update.common.toggle_upload_on"), value=True)

        def on_changed_force(e):
            if self.switch_force.value:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_on")
            else:
                self.switch_force.label = Lang.value("contents.update.common.toggle_force_off")

            self.switch_force.update()
            try:
                self.switch_force.update()
            except Exception as e:
                pass

        def on_changed_upload(e):
            if self.switch_upload.value:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_on")
            else:
                self.switch_upload.label = Lang.value("contents.update.common.toggle_upload_off")

            self.switch_upload.update()
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
                self.clear_list()
                self.clear_result()
                self.update_state(Lang.value("contents.update.buddy.begin"))
                self.loading.content = ft.ProgressRing(width=16, height=16, stroke_width = 2)
                try:
                    self.loading.update()
                except Exception as e:
                    pass

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
                            self.add_item(value, "warn", filename, Lang.value("contents.update.buddy.warn_notfound"))
                            result["warn"] += 1
                            continue
                        
                        # download
                        if download:
                            Fetch.download(icon, f"output/buddies/{filename}")
                                
                        # upload
                        if (not exist) and login:
                            fd = filename.replace(" ", "_")
                            self.wiki.upload(fd, Lang.value("contents.update.buddy.wiki_description"), f"output/buddies/{filename}")
                            self.add_item(value, "success", filename, Lang.value("common.success"))
                            result["success"] += 1
                        else:
                            result["skipped"] += 1

                    except Exception as e:
                        self.add_item(value, "error", filename, Lang.value("common.error"))
                        self.gui.popup_error(Lang.value("contents.update.buddy.failed"), str(e))
                        result["error"] += 1
                
                self.update_result(
                    Lang.value("contents.update.buddy.success"), 
                    Lang.value("contents.update.buddy.result").format(skipped=result["skipped"], success=result["success"], warn=result["warn"], error=result["error"])
                )
                self.gui.popup_success(Lang.value("contents.update.buddy.success"))

            except Exception as e:
                self.gui.popup_error(Lang.value("contents.update.buddy.failed"), str(e))

            finally:
                self.loading.content = None
                try:
                    self.loading.update()
                except Exception as e:
                    pass
                self.update_state("")
    
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
                        self.loading,
                        self.state
                    ],
                ),
                ft.Container(
                    content=self.lists,
                    padding=10,
                    height=200
                ),

                self.result
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass

    def clear_list(self):
        self.lists.controls.clear()
        self.lists.update()
        try:
            self.lists.update()
        except Exception as e:
            pass
    
    def append_list(self, ctrl: ft.Control):
        self.lists.controls.append(ctrl)
        self.lists.update()
        try:
            self.lists.update()
        except Exception as e:
            pass
    
    def clear_result(self):
        self.result.title = None
        self.result.subtitle = None
        self.result.leading = None

        try:
            self.result.update()
        except Exception as e:
            pass

    def update_result(self, title: str, subtitle: str):
        self.result.title = ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
        self.result.subtitle = ft.Text(subtitle, style=ft.TextThemeStyle.BODY_SMALL)
        self.result.leading = ft.Icon(ft.icons.CHECK, color="green")

        try:
            self.result.update()
        except Exception as e:
            pass

    def add_item(self, value: dict, mode: str, filename: str, reason: str):
        def close_dialog(e):
            dialog.open = False
            try:
                self.page.update()
            except Exception as e:
                pass

        def open_dialog(e):
            self.page.dialog = dialog
            dialog.open = True
            try:
                self.page.update()
            except Exception as e:
                pass
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(filename),
            content=ft.Column([
                ft.Text(value.get("displayName", {}).get(Lang.value("common.localize")) or "", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Row([
                    ft.Text(value.get("uuid", ""), style=ft.TextThemeStyle.BODY_SMALL),
                    self.gui.copy_button(value.get("uuid", ""))
                ]),
                ft.Image(src=f"output/buddies/{filename}", width=200, height=200, fit=ft.ImageFit.CONTAIN)
            ]),
            actions=[
                ft.TextButton(Lang.value("common.ok"), on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        imagebutton = ft.IconButton(
            icon=ft.icons.PREVIEW,
            tooltip=Lang.value("common.preview"),
            on_click = open_dialog
        ) 
        iconbutton: ft.IconButton

        if mode=="success":
            iconbutton = ft.IconButton(icon=ft.icons.CHECK, icon_color="green", tooltip=reason)
        elif mode=="skipped":
            iconbutton = ft.IconButton(icon=ft.icons.NEARBY_ERROR, icon_color="yellow", tooltip=reason)
        elif mode=="warn":
            iconbutton = ft.IconButton(icon=ft.icons.WARNING, icon_color="yellow", tooltip=reason)
        elif mode=="error":
            iconbutton = ft.IconButton(icon=ft.icons.ERROR, icon_color="red", tooltip=reason)

        self.append_list(
            ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Row(
                            controls=[
                                ft.Row([
                                    iconbutton,
                                    ft.Text(value.get("displayName", {}).get(Lang.value("common.localize")) or "", weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM)
                                ]),
                                imagebutton
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row([
                            ft.Text(filename, style=ft.TextThemeStyle.BODY_SMALL)
                        ])
                    ]),
                    padding=3
                )
            )
        )    
        
    def get_filename(self, data: dict) -> str:
        name = data.get("displayName", {})["en-US"]
        uuid = data.get("uuid")

        if name==None:
            raise Exception("Failed to get item's name.")
        
        name = String.wiki_format(name)
        return f"{name}.png"


