import flet as ft
from utils.tools.config import Config
from utils.tools.localize import Lang
from utils.tools.assets import Assets
from utils.tools.wiki import Wiki
from utils.tools.gui import Gui

class Home():
    page: ft.Page
    wiki: Wiki
    gui: Gui
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui
    
    def main(self):
        img_src: str = Config.read_key("logo")
        if len(img_src) == 0:
            img_src = Assets.path("assets/logo.png")

        card = ft.Card(
            content=ft.Container(
                width=500,
                padding=10,
                content = ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Image(
                                        src=img_src,
                                        fit=ft.ImageFit.CONTAIN,
                                    ),
                                    height=200,
                                    expand=True,
                                    margin=15
                                )
                            ],
                            alignment="center"
                        ),
                        ft.Row(
                            controls=[ft.Text(Lang.value("title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD)],
                            alignment="center"
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(ft.Text(Lang.value("description"), style=ft.TextThemeStyle.BODY_MEDIUM), margin=10)
                            ],
                            alignment="center"
                        ),
                    ]
                )
            )
        )

        return ft.ListView(
            controls=[card],
            expand=1,
            spacing=10,
            padding=20,
            auto_scroll=False
        )
