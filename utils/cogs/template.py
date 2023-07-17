import flet as ft
import os
from utils.tools.localize import Lang
from utils.tools.json import JSON
from utils.tools.fetch import Fetch
from utils.tools.wiki import Wiki, WikiString
from utils.tools.gui import Gui


class Template():
    page: ft.Page
    wiki: Wiki
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.cite = Cite(wiki, gui, page)
    
    def main(self):
        self.content = ft.Container(self.cite.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index

            if i==0:
                self.content.content = self.cite.main()
            try:
                self.content.update()
            except Exception as e:
                pass
            

        return ft.Row(
            [
                ft.NavigationRail(
                    selected_index=0,
                    label_type=ft.NavigationRailLabelType.ALL,
                    min_width=100,
                    min_extended_width=400,
                    destinations=[
                        ft.NavigationRailDestination(
                            icon=ft.icons.IMPORT_CONTACTS,
                            selected_icon=ft.icons.IMPORT_CONTACTS,
                            label=Lang.value("contents.template.cite.title"),
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


class Cite():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    switch_ref: ft.Switch
    field_url: ft.TextField

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        
        self.loading = self.gui.ProgressRing(self.page)
        self.state = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
        self.result = self.gui.Result(self.page)
        self.switch_ref = ft.Switch(label=Lang.value("contents.template.cite.toggle_ref_on"), value=True)
        self.field_url = ft.TextField(label=Lang.value("common.url"), hint_text=Lang.value("contents.template.cite.url"))

        def on_changed_ref(e):
            if self.switch_ref.value:
                self.switch_ref.label = Lang.value("contents.template.cite.toggle_ref_on")
            else:
                self.switch_ref.label = Lang.value("contents.template.cite.toggle_ref_off")

            try:
                self.switch_ref.update()
            except Exception as e:
                pass

        self.switch_ref.on_change = on_changed_ref
              
    def main(self):

        def on_clicked_url(e):
            pass

        def on_clicked_generate(e):
            try:
                self.loading.state(True)
                self.update_state(Lang.value("contents.template.cite.begin"))
                
            except Exception as e:
                self.gui.popup_error(Lang.value("contents.template.cite.failed"))
            
            finally:
                self.loading.state(False)
                self.update_state(None)
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.template.cite.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.template.cite.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Row([
                    self.field_url,
                    ft.Container(
                        content=ft.OutlinedButton(
                            text=Lang.value("contents.template.cite.button"),
                            on_click=on_clicked_url
                        ),
                        padding=5
                    )
                ]),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_ref
                    ])
                ),
                ft.Container(height=30),
                ft.Divider(),
                
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.FilledTonalButton(
                                text=Lang.value("contents.template.common.button"),
                                icon=ft.icons.DOWNLOAD,
                                on_click=on_clicked_generate
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