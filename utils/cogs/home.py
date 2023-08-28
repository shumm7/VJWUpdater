import flet as ft
from utils.tools.config import Config
from utils.tools.localize import Lang
from utils.tools.assets import Assets
from utils.tools.json import JSON
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
                        ft.Row(
                            controls=[
                                ft.Container(ft.Text(JSON.read(Assets.path("assets/package.json")).get("version", []), style=ft.TextThemeStyle.BODY_SMALL), margin=10)
                            ],
                            alignment="center"
                        ),
                        ft.Divider(),

                        ft.Row(
                            controls=[
                                ft.Text(
                                    spans=[
                                        ft.TextSpan("HeyM1ke/ValorantClientAPI", ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url="https://github.com/HeyM1ke/ValorantClientAPI"),
                                        ft.TextSpan(", "),
                                        ft.TextSpan("colinhartigan/valclient.py", ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url="https://github.com/colinhartigan/valclient.py"),
                                        ft.TextSpan(", "),
                                        ft.TextSpan("techchrism/valorant-api-docs", ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url="https://github.com/techchrism/valorant-api-docs/"),
                                        ft.TextSpan(", "),
                                        ft.TextSpan("Valorant-API", ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url="https://valorant-api.com/"),
                                        ft.TextSpan(", "),
                                        ft.TextSpan("hcs64/ww2ogg", ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url="https://github.com/hcs64/ww2ogg"),
                                        ft.TextSpan(", "),
                                        ft.TextSpan("ItsBranK/ReVorb", ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url="https://github.com/ItsBranK/ReVorb"),
                                        ft.TextSpan(", "),
                                        ft.TextSpan("vgmstream/vgmstream", ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url="https://github.com/vgmstream/vgmstream"),
                                        
                                    ]
                                )
                            ],
                            alignment="center"
                        )
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
