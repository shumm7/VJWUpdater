import flet as ft
import os, requests, shutil
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData, Config, Lang
from utils.api import API
from utils.wiki import Wiki
from utils.gui import Gui

class Cache():
    page: ft.Page
    wiki: Wiki
    gui: Gui
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.version_check = VersionCheck(wiki, gui, page)
        self.fetch = FetchAll(wiki, gui, page)
    
    def main(self):
        self.content = ft.Container(self.version_check.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index

            if i==0:
                self.content.content = self.version_check.main()
            elif i==1:
                self.content.content = self.fetch.main()
            try:
                self.content.update()
            except Exception as e:
                pass
            

        card = ft.Row(
            [
                ft.NavigationRail(
                    selected_index=0,
                    label_type=ft.NavigationRailLabelType.ALL,
                    min_width=100,
                    min_extended_width=400,
                    destinations=[
                        ft.NavigationRailDestination(
                            icon_content=ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINED),
                            selected_icon_content=ft.Icon(ft.icons.CHECK_CIRCLE),
                            label=Lang.value("contents.cache.check.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.CLOUD_DOWNLOAD_OUTLINED,
                            selected_icon_content=ft.Icon(ft.icons.CLOUD_DOWNLOAD),
                            label=Lang.value("contents.cache.fetch.title"),
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

        return card
    
class VersionCheck():
    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.legacy = JSON.read("api/version.json")
        self.message = ft.Container(padding=10)
        self.loading = ft.Container()
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.datacells = [ft.Text(self.legacy.get("manifestId", "")), ft.Text(self.legacy.get("branch", "")), ft.Text(self.legacy.get("version", ""))]

    def main(self):
        def on_clicked(e):
            self.loading.content = ft.ProgressRing(width=16, height=16, stroke_width = 2)
            try:
                self.loading.update()
            except Exception as e:
                pass

            try:
                self.update_state(Lang.value("contents.cache.check.fetch"))
                resp = requests.get('https://valorant-api.com/v1/version')
                result: bool
                if resp.status_code == 200:
                    if not os.path.exists("api/version.json"):
                        raise FileNotFoundError()

                    legacy = JSON.read("api/version.json")
                    current = resp.json()['data']
                    if current['manifestId']==legacy['manifestId']:
                        result = True
                    else:
                        result = False
                else:
                    raise Exception("Failed to checking version")
                
                self.update_state(Lang.value("contents.cache.check.check"))
                if result:
                    self.message.content = ft.ListTile(
                        leading=ft.Icon(name=ft.icons.CHECK, color="green"),
                        title=ft.Text(Lang.value("contents.cache.check.result_latest"), style=ft.TextThemeStyle.BODY_MEDIUM),
                        subtitle=ft.Text(Lang.value("contents.cache.check.result_latest_message"), style=ft.TextThemeStyle.BODY_SMALL),
                    )
                else:
                    self.message.content = ft.ListTile(
                        leading=ft.Icon(name=ft.icons.ERROR_OUTLINE, color="red"),
                        title=ft.Text(Lang.value("contents.cache.check.result_outdated"), style=ft.TextThemeStyle.BODY_MEDIUM),
                        subtitle=ft.Text(Lang.value("contents.cache.check.result_outdated_message"), style=ft.TextThemeStyle.BODY_SMALL),
                    )
                try:
                    self.message.update()
                except Exception as e:
                    pass
                self.gui.popup_success(Lang.value("contents.cache.check.success"))

            except FileNotFoundError as e:
                self.gui.popup_error(Lang.value("contents.cache.check.notfound"))

            except Exception as e:
                self.gui.popup_error(Lang.value("contents.cache.check.failed"), str(e))

            finally:
                self.loading.content = None
                try:
                    self.loading.update()
                except Exception as e:
                    pass
                self.update_state("")
                self.update_datacells()

        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.cache.check.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.cache.check.description"), style=ft.TextThemeStyle.BODY_SMALL),
                ),
                ft.Divider(),
                
                ft.Container(
                    ft.Column([
                        ft.ListTile(
                            title=ft.Text(Lang.value("contents.cache.fetch.manifestId"), style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                            subtitle=self.datacells[0]
                        ),
                        ft.ListTile(
                            title=ft.Text(Lang.value("contents.cache.fetch.branch"), style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                            subtitle=self.datacells[1]
                        ),
                        ft.ListTile(
                            title=ft.Text(Lang.value("contents.cache.fetch.version"), style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                            subtitle=self.datacells[2]
                        ),
                    ])
                ),
                ft.Container(height=30),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.cache.check.button"),
                                icon=ft.icons.CHECK,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading,
                        self.state
                    ],
                ),
                
                self.message
            ],
            spacing=0
        )

    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
        
    def update_datacells(self):
        legacy = JSON.read("api/version.json")
        self.datacells[0].value = legacy.get("manifestId", "")
        self.datacells[1].value = legacy.get("branch", "")
        self.datacells[2].value = legacy.get("version", "")
        try:
            self.datacells[0].update()
            self.datacells[1].update()
            self.datacells[2].update()
        except Exception:
            pass

class FetchAll():
    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.message = ft.Container(padding=10)
        self.loading = ft.Container()
        self.legacy = JSON.read("api/version.json")
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.datacells = [ft.Text(self.legacy.get("manifestId", "")), ft.Text(self.legacy.get("branch", "")), ft.Text(self.legacy.get("version", ""))]
    
    def main(self):
        def on_clicked(e):
            self.loading.content = ft.ProgressRing(width=16, height=16, stroke_width = 2)
            try:
                self.loading.update()
            except Exception as e:
                pass

            try:
                self.fetch()
            except Exception as e:
                self.gui.popup_error(Lang.value("contents.cache.fetch.failed"), str(e))
            
            self.loading.content = None
            try:
                self.loading.update()
            except Exception as e:
                pass

            self.update_state("")
            self.update_datacells()
            self.gui.popup_success(Lang.value("contents.cache.fetch.success"))

        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.cache.fetch.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.cache.fetch.description"), style=ft.TextThemeStyle.BODY_SMALL),
                ),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        ft.ListTile(
                            title=ft.Text(Lang.value("contents.cache.fetch.manifestId"), style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                            subtitle=self.datacells[0]
                        ),
                        ft.ListTile(
                            title=ft.Text(Lang.value("contents.cache.fetch.branch"), style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                            subtitle=self.datacells[1]
                        ),
                        ft.ListTile(
                            title=ft.Text(Lang.value("contents.cache.fetch.version"), style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD),
                            subtitle=self.datacells[2]
                        ),
                    ])
                ),
                ft.Container(height=30),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.cache.fetch.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked
                            ),
                            padding=10
                        ),
                        self.loading,
                        self.state
                    ],
                ),
                
                self.message
            ],
            spacing=0
        )


    def update_state(self, str: str):
        self.state.value = str
        try:
            self.state.update()
        except Exception:
            pass
        
    def update_datacells(self):
        legacy = JSON.read("api/version.json")
        self.datacells[0].value = legacy.get("manifestId", "")
        self.datacells[1].value = legacy.get("branch", "")
        self.datacells[2].value = legacy.get("version", "")
        try:
            self.datacells[0].update()
            self.datacells[1].update()
            self.datacells[2].update()
        except Exception:
            pass
        
    def fetch(self):
        os.makedirs(f"api/dict", exist_ok=True)
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.version")))
        API.version()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.agent")))
        API.agents()

        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.buddy")))
        API.buddies()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.bundle")))
        API.bundles()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.competitivetier")))
        API.competitivetiers()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.contract")))
        API.contracts()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.gear")))
        API.gear()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.levelborder")))
        API.levelborders()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.map")))
        API.maps()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.playercard")))
        API.playercards()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.playertitle")))
        API.playertitles()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.season")))
        API.seasons()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.spray")))
        API.sprays()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.weapon")))
        API.weapons()
        
        self.update_state(Lang.value("contents.cache.fetch.finish"))
        b = JSON.read("api/version.json").get('version', "None")
        os.makedirs(f"api/{b}", exist_ok=True)

        filelist = []
        for file in os.listdir("api"):
            if os.path.splitext(file)[1]==".json":
                filelist.append(file)
        
        for file in filelist:
            shutil.copy(f'api/{file}', f'api/{b}/{file}')
