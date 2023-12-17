import os
import requests
import flet as ft
from utils.tools.config import Config
from utils.tools.localize import Lang
from utils.tools.wiki import Wiki
from utils.tools.gui import Gui
from utils.tools.json import JSON
from utils.tools.assets import Assets

from utils.cogs.settings import Settings
from utils.cogs.home import Home
from utils.cogs.cache import Cache
from utils.cogs.update import Update
from utils.cogs.template import Template
#from utils.cogs.wikitext import Wikitext
from utils.cogs.data import Data
from utils.cogs.esports import Esports
from utils.cogs.audio import Audio
from utils.cogs.misc import Misc

class Core():
    page: ft.Page
    gui: Gui
    settings: Settings

    cache: Cache
    update: Update
    template: Template
    #wikitext: Wikitext
    esports: Esports
    audio: Audio
    misc: Misc
    data: Data

    def __init__(self) -> None:
        ft.app(target=self.set_window)
        
    def main(self):
        wikibot: dict = Config.read_key("wikibot")
        self.wiki = Wiki(wikibot.get("id", ""), wikibot.get("password", ""), Config.read_key("api"))

        self.gui = Gui(self.page)

        self.settings = Settings(self.wiki, self.gui, self.page)
        self.home = Home(self.wiki, self.gui, self.page)
        self.cache = Cache(self.wiki, self.gui, self.page)
        self.update = Update(self.wiki, self.gui, self.page)
        self.template = Template(self.wiki, self.gui, self.page)
        #self.wikitext = Wikitext(self.wiki, self.page)
        self.data = Data(self.wiki, self.gui, self.page)
        self.esports = Esports(self.wiki, self.gui, self.page)     
        self.audio = Audio(self.wiki, self.gui, self.page)      
        self.misc = Misc(self.wiki, self.gui, self.page)
        
        self.version_check()

    def set_window(self, page: ft.Page):
        self.page = page
        self.main()
        page.title = Lang.value("title")

        # Tabs
        self.page.add(
            ft.Tabs(
                selected_index=2,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        icon=ft.icons.SETTINGS,
                        content=self.settings.main(),
                    ),
                    ft.Tab(
                        icon=ft.icons.HOME,
                        content=self.home.main(),
                    ),
                    ft.Tab(
                        text=Lang.value("tabs.cache"),
                        icon=ft.icons.ATTACH_FILE,
                        content=self.cache.main()
                    ),
                    ft.Tab(
                        text=Lang.value("tabs.update"),
                        icon=ft.icons.UPDATE,
                        content=self.update.main()
                    ),
                    #ft.Tab(
                    #    text=Lang.value("tabs.list"),
                    #    icon=ft.icons.LIST_ALT,
                    #    content=self.data.main()
                    #),
                    ft.Tab(
                        text=Lang.value("tabs.template"),
                        icon=ft.icons.CONTACT_PAGE,
                        content=self.template.main()
                    ),
                    ft.Tab(
                        text=Lang.value("tabs.esports"),
                        icon=ft.icons.MOUSE,
                        content=self.esports.main()
                    ),
                    ft.Tab(
                        text=Lang.value("tabs.audio"),
                        icon=ft.icons.MIC,
                        content=self.audio.main()
                    ),
                    ft.Tab(
                        text=Lang.value("tabs.misc"),
                        icon=ft.icons.CONSTRUCTION,
                        content=self.misc.main()
                    ),
                ],
                expand=True,
            )
        )
    
    def version_check(self):
        url = "https://raw.githubusercontent.com/shumm7/VJWUpdater/main/assets/package.json"

        try:
            current_version = JSON.read(Assets.path("assets/package.json")).get("version", "")
            ret = requests.get(url).json()
            latest_version = ret.get("version")

            if latest_version==None:
                self.gui.popup_warn(Lang.value("common.version_check.failed"), Lang.value("common.version_check.failed").format(version=str(current_version), latest=str(latest_version)))
            else:
                if latest_version==current_version:
                    self.gui.popup_success(Lang.value("common.version_check.success"), Lang.value("common.version_check.latest").format(version=str(current_version), latest=str(latest_version)))
                else:
                    self.gui.popup_warn(Lang.value("common.version_check.success"), Lang.value("common.version_check.outdated").format(version=str(current_version), latest=str(latest_version)))

        except Exception as e:
            self.gui.popup_error(Lang.value("common.version_check.failed"), str(e))
    