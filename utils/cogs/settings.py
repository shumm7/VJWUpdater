import os, glob, asyncio
import flet as ft
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.tools.localize import Lang
from utils.tools.config import Config
from utils.tools.assets import Assets
from utils.tools.endpoint import Endpoint
from utils.tools.api import API
from utils.tools.wiki import Wiki
from utils.tools.auth import Auth, RiotAccount
from utils.tools.gui import Gui
from utils.tools.fetch import Webdriver

class Settings():
    page: ft.Page
    wiki: Wiki
    gui: Gui
    auth: RiotAccount
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui
        self.auth = RiotAccount(page)

    def main(self):
        # 言語設定
        language_list = {}
        for p in glob.glob(Assets.path('assets/lang')+"/*.json"):
            lang = os.path.splitext(os.path.basename(p))[0]
            language_list[lang] = Lang.value("name", lang) + f" ( {lang} )"

        language_options = []
        for k,h in language_list.items():
            language_options.append(ft.dropdown.Option(key=k, text=h))
        
        def language_selected(e):
            current: str = Config.read_key("lang")
            if current != language_dropdown.value:
                Config.save_key("lang", language_dropdown.value)
                self.gui.popup_notice(Lang.value("settings.lang.notice"))

        language_dropdown = ft.Dropdown(
            options=language_options,
            on_change=language_selected,
            value = Lang.get_current_language(),
            width=200,
            label=Lang.value("settings.lang.title")
        )

        # テーマ
        current_theme = Config.read_key("theme")
        if not current_theme in ["system", "dark", "light"]:
            current_theme = "system"
        
        theme_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(key="system", text=Lang.value("settings.theme.system")),
                ft.dropdown.Option(key="light", text=Lang.value("settings.theme.light")),
                ft.dropdown.Option(key="dark", text=Lang.value("settings.theme.dark"))
            ],
            value=current_theme,
            width=200,
            label=Lang.value("settings.theme.title")
        )

        def theme_selected(e):
            v = theme_dropdown.value
            if v == "system":
                self.page.theme_mode = ft.ThemeMode.SYSTEM
            elif v == "light":
                self.page.theme_mode = ft.ThemeMode.LIGHT
            elif v == "dark":
                self.page.theme_mode = ft.ThemeMode.DARK
            self.gui.safe_update(self.page)
            Config.save_key("theme", v)

        theme_dropdown.on_change = theme_selected

        

        # Wiki API
        api_url_field: ft.TextField = ft.TextField(label=Lang.value("common.url"), value=Config.read_key("api"))

        def api_changed(e):
            Config.save_key("api", api_url_field.value)
        
        api_url_field.on_change = api_changed


        # Riot アカウント ログイン
        riot_loading = ft.Container()
        riot_login_button: ft.FilledTonalButton = ft.FilledTonalButton(text=Lang.value("settings.riot.button"), icon=ft.icons.LOGIN)
        riot_id_field: ft.TextField = ft.TextField(label=Lang.value("settings.riot.id"))
        riot_password_field: ft.TextField = ft.TextField(label=Lang.value("settings.riot.password"), password=True, can_reveal_password=True)
        riot_username: ft.Text = ft.Text()
        riot_playercard: ft.CircleAvatar = ft.CircleAvatar()
        riot_reflesh: ft.IconButton = ft.IconButton(icon=ft.icons.REFRESH, tooltip=Lang.value("common.reload"), on_click=lambda e: set_playercard())
        
        def set_playercard():
            player_name = Auth().get_auth().get("username")

            if player_name!=None:
                try:
                    card_id = Endpoint().fetch_player_loadout()["Identity"]["PlayerCardID"]
                    card_url = API.playercard_by_uuid(card_id)["displayIcon"]
                    riot_username.value = player_name
                    riot_playercard.foreground_image_url = card_url
                except Exception as e:
                    riot_username.value = ""
                    riot_playercard.foreground_image_url = None
            else:
                riot_username.value = ""
                riot_playercard.foreground_image_url = None
                
            self.gui.safe_update(riot_username)
            self.gui.safe_update(riot_playercard)

        def riot_clicked(e):
            try:
                riot_loading.content = ft.ProgressRing(width=16, height=16, stroke_width = 2)
                self.gui.safe_update(riot_loading)
                asyncio.run(self.auth.login(riot_id_field.value, riot_password_field.value))

            except Exception as e:
                self.gui.popup_error(Lang.value("settings.riot.failed"), str(e))

            finally:
                riot_loading.content = None
                self.gui.safe_update(riot_loading)
                
                riot_id_field.value = ""
                self.gui.safe_update(riot_id_field)
                riot_password_field.value = ""
                self.gui.safe_update(riot_password_field)
                set_playercard()

        riot_login_button.on_click = riot_clicked
        set_playercard()


        # Wiki Bot ログイン
        wikibot_loading = ft.Container()
        wikibot_login_button: ft.FilledTonalButton = ft.FilledTonalButton(text=Lang.value("settings.wikibot.button"), icon=ft.icons.LOGIN)
        wikibot_id_field: ft.TextField = ft.TextField(label=Lang.value("settings.wikibot.id"), value=Config.read_key("wikibot").get("id"))
        wikibot_password_field: ft.TextField = ft.TextField(label=Lang.value("settings.wikibot.password"), password=True, can_reveal_password=True)

        def wikibot_clicked(e):
            try:
                wikibot_loading.content = ft.ProgressRing(width=16, height=16, stroke_width = 2)
                try:
                    wikibot_loading.update()
                except Exception as e:
                    pass

                wiki = Wiki(wikibot_id_field.value, wikibot_password_field.value, Config.read_key("api"))
                wiki.login()
                Config.save_key("wikibot", {"id": wikibot_id_field.value, "password": wikibot_password_field.value})
                self.gui.popup_success(Lang.value("settings.wikibot.success"))

            except Exception as e:
                self.gui.popup_error(Lang.value("settings.wikibot.failed"), str(e))

            finally:
                wikibot_loading.content = None
                self.gui.safe_update(wikibot_loading)

        wikibot_login_button.on_click = wikibot_clicked

        # ロゴ
        logo_src_field: ft.TextField = ft.TextField(label=Lang.value("settings.logo.src"), value=Config.read_key("logo"))
        logo_image = ft.Image(fit=ft.ImageFit.CONTAIN)

        if len(logo_src_field.value) == 0:
            logo_image.src = Assets.path(f"assets/logo.png")
        else:
            logo_image.src = logo_src_field.value

        def logo_changed(e):
            Config.save_key("logo", logo_src_field.value)
            if len(logo_src_field.value) == 0:
                logo_image.src = Assets.path(f"assets/logo.png")
            else:
                logo_image.src = logo_src_field.value
            self.gui.safe_update(logo_image)
        
        logo_src_field.on_change = logo_changed

        # Webdriver
        webdriver_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="chrome", label=Lang.value("settings.webdriver.chrome")),
                ft.Radio(value="firefox", label=Lang.value("settings.webdriver.firefox")),
                ft.Radio(value="edge", label=Lang.value("settings.webdriver.edge")),
            ]),
            value=Config.read_key("webdriver")
        )
        webdriver_button = ft.FilledTonalButton(text=Lang.value("settings.webdriver.button"), icon=ft.icons.LOGIN, tooltip=Lang.value("settings.webdriver.tooltip"))
        webdriver_loading = self.gui.ProgressRing(self.page)

        def webdriver_changed(e):
            Config.save_key("webdriver", webdriver_radio.value)
        
        def webdriver_clicked(e):
            webdriver_button.disabled = True
            self.gui.safe_update(webdriver_button)
            webdriver_loading.state(True)

            try:
                driver = Webdriver.get()
                driver.get("https://playvalorant.com/ja-jp/news/announcements/valorant-community-code/")
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "article")))
                WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)
                driver.find_element(by=By.CSS_SELECTOR, value='h2[class*="heading-10 NewsArticleContent-module--title--"] span')
                self.gui.popup_success(Lang.value("settings.webdriver.success"))
            except Exception as e:
                self.gui.popup_error(Lang.value("common.error_message.error"), str(e))
            finally:
                webdriver_loading.state(False)
                webdriver_button.disabled = False
                self.gui.safe_update(webdriver_button)

            
        webdriver_radio.on_change = webdriver_changed
        webdriver_button.on_click = webdriver_clicked

        # Card
        card = ft.Card(
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(Lang.value("settings.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                        ),

                        # 言語
                        ft.Container(
                            padding=10,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(name=ft.icons.LANGUAGE),
                                            ft.Text(Lang.value("settings.lang.title"), style=ft.TextThemeStyle.BODY_MEDIUM),
                                        ],
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.icons.WARNING_AMBER,
                                                icon_color="yellow400",
                                                icon_size=20,
                                                tooltip=Lang.value("settings.lang.notice"),
                                            ),
                                            language_dropdown
                                        ]
                                    )
                                ]
                            ),
                        ),
                        ft.Divider(),

                        # テーマ
                        ft.Container(
                            padding=10,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(name=ft.icons.LIGHT_MODE),
                                            ft.Text(Lang.value("settings.theme.title"), style=ft.TextThemeStyle.BODY_MEDIUM),
                                        ],
                                    ),
                                    theme_dropdown
                                ]
                            ),
                        ),

                        ft.Divider(),

                        # Webdriver
                        ft.Column(
                            controls=[
                                ft.Container(
                                    padding=10,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                                        controls=[
                                            ft.Row([
                                                ft.Icon(name=ft.icons.PUBLIC),
                                                ft.Text(Lang.value("settings.webdriver.title"), style=ft.TextThemeStyle.BODY_MEDIUM)
                                            ]),
                                            webdriver_radio
                                        ]
                                    ),
                                ),
                                ft.Row(
                                    [
                                        webdriver_loading.main(),
                                        webdriver_button
                                    ],
                                    alignment=ft.MainAxisAlignment.END
                                )
                            ]
                        ),
                        ft.Divider(),

                        # Wiki API
                        ft.Column(
                            controls=[
                                ft.Container(
                                    padding=10,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.START, 
                                        controls=[
                                            ft.Icon(name=ft.icons.API),
                                            ft.Text(Lang.value("settings.api.title"), style=ft.TextThemeStyle.BODY_MEDIUM),
                                        ]
                                    ),
                                ),
                                api_url_field
                            ]
                        ),
                        ft.Divider(),

                        # Riot アカウント
                        ft.Column(
                            controls=[
                                ft.Container(
                                    padding=10,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.START, 
                                        controls=[
                                            ft.Icon(name=ft.icons.LINK),
                                            ft.Text(Lang.value("settings.riot.title"), style=ft.TextThemeStyle.BODY_MEDIUM),
                                        ]
                                    ),
                                ),

                                ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                riot_id_field,
                                                riot_password_field
                                            ],
                                            expand=True
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Row([
                                            riot_reflesh,
                                            riot_playercard,
                                            riot_username
                                        ]),
                                        ft.Row([
                                            riot_loading,
                                            ft.Container(
                                                content=riot_login_button,
                                                padding=10
                                            )
                                        ])
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                )
                            ]
                        ),
                        ft.Divider(),

                        # Wikiへのログイン
                        ft.Column(
                            controls=[
                                ft.Container(
                                    padding=10,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.START, 
                                        controls=[
                                            ft.Icon(name=ft.icons.SMART_TOY_SHARP),
                                            ft.Text(Lang.value("settings.wikibot.title"), style=ft.TextThemeStyle.BODY_MEDIUM),
                                        ]
                                    ),
                                ),

                                ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                wikibot_id_field,
                                                wikibot_password_field
                                            ],
                                            expand=True
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    controls=[
                                        wikibot_loading,
                                        ft.Container(
                                            content=wikibot_login_button,
                                            padding=10
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                )
                            ]
                        ),
                        ft.Divider(),

                        # ロゴ
                        ft.Column(
                            controls=[
                                ft.Container(
                                    padding=10,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                                        controls=[
                                            ft.Row([
                                                ft.Icon(name=ft.icons.IMAGE),
                                                ft.Text(Lang.value("settings.logo.title"), style=ft.TextThemeStyle.BODY_MEDIUM)
                                            ]),
                                            ft.Row([
                                                ft.IconButton(
                                                    icon=ft.icons.HELP,
                                                    tooltip=Lang.value("settings.logo.notice"),
                                                ),
                                            ])
                                        ]
                                    ),
                                ),
                                logo_src_field,
                                ft.Row(
                                    [ft.Container(content=logo_image, width=100, height=100, padding=2)],
                                    alignment=ft.MainAxisAlignment.END
                                )
                            ]
                        ),
                        ft.Divider(),
                    ],
                    spacing=0,
                ),
            )
        )

        return ft.ListView(
            controls=[card],
            expand=1,
            spacing=10,
            padding=20,
            auto_scroll=False
        )
