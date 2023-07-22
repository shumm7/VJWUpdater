import flet as ft
import os, bs4, requests, datetime, re
import urllib.parse
from utils.tools.localize import Lang
from utils.tools.json import JSON
from utils.tools.fetch import Fetch
from utils.tools.wiki import Wiki, WikiString
from utils.tools.gui import Gui
from utils.tools.scrape.vlr import Match as VLR_Match


class Esports():
    page: ft.Page
    wiki: Wiki
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.matchlist = MatchList(wiki, gui, page)
    
    def main(self):
        self.content = ft.Container(self.matchlist.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index
            contents = [
                self.matchlist.main()
            ]

            try:
                self.content.content = contents[i]
            except IndexError:
                pass
            self.gui.safe_update(self.content)

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
                            label=Lang.value("contents.esports.matchlist.title"),
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
                        horizontal_alignment=ft.MainAxisAlignment.START,
                        #scroll=True
                    ),
                    expand=True,
                )
            ]
        )


class MatchList():
    page: ft.Page
    loading: Gui.ProgressRing
    state: ft.Text
    output: str

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.field_id = ft.TextField(label=Lang.value("contents.esports.matchlist.match_id"))
        self.field_result = ft.TextField(label=Lang.value("common.output"), expand=True, multiline=True, max_lines=5)
        self.copy_button = self.gui.CopyButton(self.page)
        self.progress_ring = self.gui.ProgressRing(self.page)
        
              
    def main(self):
        def on_clicked(e):
            self.progress_ring.state(True)

            id = self.field_id.value
            if WikiString.is_url(id):
                p = urllib.parse.urlparse(id)
                id = p.path.split("/")[1]
            vlr = VLR_Match(id)

            self.field_result.value = self.generate_template(vlr)
            self.copy_button.set(self.field_result.value)
            self.gui.safe_update(self.field_result)
            self.progress_ring.state(False)
            self.gui.popup_success(Lang.value("contents.esports.matchlist.success"))
    
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.esports.matchlist.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.esports.matchlist.description"), style=ft.TextThemeStyle.BODY_SMALL)
                ),
                ft.Divider(),

                ft.Container(
                    ft.Row([
                        self.field_id,
                        self.progress_ring.main()
                    ])
                ),
                ft.Row([
                    ft.FilledTonalButton(
                        text=Lang.value("contents.esports.matchlist.button"),
                        icon=ft.icons.DOWNLOAD,
                        on_click=on_clicked
                    ),
                    ft.IconButton(
                        icon=ft.icons.HELP,
                        tooltip=Lang.value("contents.esports.matchlist.tooltip")
                    )
                ]),
                ft.Divider(),

                ft.Container(
                    ft.Row([
                        self.field_result,
                        self.copy_button.main()
                    ])
                ),
            ],
            spacing=0
        )

    def generate_template(self, vlr: VLR_Match) -> str:
        ret: str = "{{Match list\n"

        # team
        ret += "|team1=" + vlr.team[0] + " |team2=" + vlr.team[1] + "\n"
        # score
        ret += "|score=" + str(vlr.map_count[0]) + "-" + str(vlr.map_count[1]) + "\n"
        
        # match
        i = 1
        for match in vlr.match:
            # map score
            ret += f"|score{i}=" + str(match["score"][0]) + "-" + str(match["score"][1]) + "\n"

            # map player / agent
            for team in range(2):
                team = team + 1
                player_str = f"|player{i}-{team}="
                agent_str = f"|agent{i}-{team}="

                for player in match["player"][team-1]:
                    player_str += player["name"] + "; "
                    agent_str += player["agent"] + "; "
                
                ret += player_str + "\n"
                ret += agent_str + "\n"
            i += 1
        
        # vlr
        ret += "|vlr=" + vlr.match_id + "\n"

        # vod
        i = 1
        for vod in vlr.vod:
            ret += f"|vod{i}=" + vod + "\n"
            i += 1

        return ret + "}}"

