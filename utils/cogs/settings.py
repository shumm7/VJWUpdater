import os, glob
import flet as ft

from utils.wiki import Wiki
from utils.gui import Gui
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData, Config, Lang

class Settings():
    page: ft.Page
    wiki: Wiki
    gui: Gui
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui
    
    def main(self):
        # 言語設定
        language_list = {}
        for p in glob.glob('lang/*.json'):
            lang = os.path.splitext(os.path.basename(p))[0]
            language_list[lang] = Lang.value("name", lang) + f" ( {lang} )"

        language_options = []
        for k,h in language_list.items():
            language_options.append(ft.dropdown.Option(key=k, text=h))
        
        def language_selected(e):
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
            try:
                self.page.update()
            except Exception as e:
                pass
            Config.save_key("theme", v)

        theme_dropdown.on_change = theme_selected

        

        # Wiki API
        api_url_field: ft.TextField = ft.TextField(label=Lang.value("settings.api.url"), value=Config.read_key("api"))

        def api_changed(e):
            Config.save_key("api", api_url_field.value)
        
        api_url_field.on_change = api_changed

        # Wiki Bot ログイン
        wikibot_loading = ft.Container()
        wikibot_login_button: ft.FilledTonalButton = ft.FilledTonalButton(
            text=Lang.value("settings.wikibot.login"),
            icon=ft.icons.LOGIN
        )
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
                try:
                    wikibot_loading.update()
                except Exception as e:
                    pass

        wikibot_login_button.on_click = wikibot_clicked

        # ロゴ
        logo_src_field: ft.TextField = ft.TextField(label=Lang.value("settings.logo.src"), value=Config.read_key("logo"))
        logo_image = ft.Image(src=logo_src_field.value, fit=ft.ImageFit.CONTAIN)

        def logo_changed(e):
            Config.save_key("logo", logo_src_field.value)
            logo_image.src = logo_src_field.value
            try:
                logo_image.update()
            except Exception as e:
                pass
        
        logo_src_field.on_change = logo_changed

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
                                                tooltip=Lang.value("settings.lang.warning"),
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
                                        alignment=ft.MainAxisAlignment.START, 
                                        controls=[
                                            ft.Icon(name=ft.icons.IMAGE),
                                            ft.Text(Lang.value("settings.logo.title"), style=ft.TextThemeStyle.BODY_MEDIUM),
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
