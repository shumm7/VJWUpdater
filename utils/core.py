import os
import flet as ft
from utils.tools.config import Config
from utils.tools.localize import Lang
from utils.tools.wiki import Wiki
from utils.tools.gui import Gui

from utils.cogs.settings import Settings
from utils.cogs.home import Home
from utils.cogs.cache import Cache
from utils.cogs.update import Update
#from utils.cogs.wikitext import Wikitext
#from utils.cogs.list import List
#from utils.cogs.esports import Esports

class Core():
    page: ft.Page
    gui: Gui
    settings: Settings

    cache: Cache
    update: Update
    #wikitext: Wikitext
    #list: List
    #esports: Esports

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
        #self.wikitext = Wikitext(self.wiki, self.page)
        #self.list = List(self.wiki, self.page)
        #self.esports = Esports(self.wiki, self.page)      
    

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
                    ft.Tab(
                        text=Lang.value("tabs.template"),
                        icon=ft.icons.CONTACT_PAGE,
                    ),
                    ft.Tab(
                        text=Lang.value("tabs.misc"),
                        icon=ft.icons.AUTO_FIX_NORMAL,
                    ),
                ],
                expand=True,
            )
        )
    

    
    