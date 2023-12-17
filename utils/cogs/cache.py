import flet as ft
import os, requests, shutil
from utils.tools.json import JSON
from utils.tools.localize import Lang
from utils.tools.api import API
from utils.tools.wiki import Wiki
from utils.tools.gui import Gui
from utils.tools.endpoint import Endpoint

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
            contents = [
                self.version_check.main(),
                self.fetch.main()
            ]

            try:
                self.content.content = contents[i]
            except IndexError:
                pass
            self.gui.safe_update(self.content)
            

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
        self.result = self.gui.Result(self.page)
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.datacells = [ft.Text(self.legacy.get("manifestId", "")), ft.Text(self.legacy.get("branch", "")), ft.Text(self.legacy.get("version", ""))]

    def main(self):
        def on_clicked(e):
            self.loading.state(True)

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
                    self.result.success(Lang.value("contents.cache.check.result_latest"), Lang.value("contents.cache.check.result_latest_message"))
                else:
                    self.result.warn(Lang.value("contents.cache.check.result_outdated"), Lang.value("contents.cache.check.result_outdated_message"))
                self.gui.popup_success(Lang.value("contents.cache.check.success"))

            except FileNotFoundError as e:
                self.gui.popup_error(Lang.value("contents.cache.check.notfound"))

            except Exception as e:
                self.gui.popup_error(Lang.value("contents.cache.check.failed"), str(e))

            finally:
                self.update_state("")
                self.loading.state(False)

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

        self.result = self.gui.Result(self.page)
        self.loading = self.gui.ProgressRing(self.page)
        self.legacy = JSON.read("api/version.json")
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.datacells = [ft.Text(self.legacy.get("manifestId", "")), ft.Text(self.legacy.get("branch", "")), ft.Text(self.legacy.get("version", ""))]
    
    def main(self):
        def on_clicked(e):
            self.loading.state(True)

            try:
                self.fetch()
            except Exception as e:
                self.update_state("")
                self.update_datacells()
                self.loading.state(False)
                self.gui.popup_error(Lang.value("contents.cache.fetch.failed"), str(e))
                self.result.error(Lang.value("contents.cache.fetch.failed"))
                return
            
            self.update_state("")
            self.update_datacells()
            self.loading.state(False)
            self.result.success(Lang.value("contents.cache.fetch.success"))
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
    
    def offer(self):
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.offer")))
        endpoint = Endpoint()
        offers = endpoint.fetch_offers()
        ret = {}

        for offer in offers["Offers"]:
            ret[offer["OfferID"]] = {
                "uuid": offer["OfferID"],
                "purchase": offer["IsDirectPurchase"],
                "date": offer["StartDate"],
                "vp": offer["Cost"].get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0),
                "reward": offer["Rewards"]
            }

        JSON.save("api/offer.json", ret)
        
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

        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.contenttier")))
        API.contenttiers()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.currency")))
        API.currencies()

        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.event")))
        API.events()

        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.gamemode")))
        API.gamemodes()
        
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
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.theme")))
        API.themes()

        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.map")))
        API.maps()
        
        self.update_state(Lang.value("contents.cache.fetch.fetch").format(name=Lang.value("common.weapon")))
        API.weapons()

        #endpoint
        self.offer()
        
        self.update_state(Lang.value("contents.cache.fetch.finish"))
        b = JSON.read("api/version.json").get('version', "None")
        os.makedirs(f"api/{b}", exist_ok=True)

        filelist = []
        for file in os.listdir("api"):
            if os.path.splitext(file)[1]==".json":
                filelist.append(file)
        
        for file in filelist:
            shutil.copy(f'api/{file}', f'api/{b}/{file}')
