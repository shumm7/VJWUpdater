import flet as ft
import os, bs4, requests, datetime, re
import urllib.parse
from utils.tools.localize import Lang
from utils.tools.json import JSON
from utils.tools.fetch import Fetch
from utils.tools.wiki import Wiki, WikiString
from utils.tools.gui import Gui
from utils.tools.scrape.playvalorant import PlayValorant, ValorantEsports
from utils.tools.scrape.twitter import Tweet


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

            contents = [
                self.cite.main()
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
                        horizontal_alignment=ft.MainAxisAlignment.START,
                        scroll=True
                    ),
                    expand=True,
                )
            ]
        )


class Cite():
    page: ft.Page
    state: ft.Text
    switch_ref: ft.Switch
    field_url: ft.TextField
    output: str

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.switch_ref = ft.Switch(label=Lang.value("contents.template.cite.toggle_ref_on"), value=True)
        self.field_url = ft.TextField(label=Lang.value("common.url"), hint_text=Lang.value("contents.template.cite.url_description"))

        self.field_template_url = ft.TextField(label=Lang.value("contents.template.cite.item.url"))
        self.field_template_title = ft.TextField(label=Lang.value("contents.template.cite.item.title"))
        self.field_template_author = ft.TextField(label=Lang.value("contents.template.cite.item.author"))
        self.field_template_website = ft.TextField(label=Lang.value("contents.template.cite.item.website"))
        self.field_template_date = ft.TextField(label=Lang.value("contents.template.cite.item.date"))
        self.field_template_quote = ft.TextField(label=Lang.value("contents.template.cite.item.quote"))
        self.field_template_section = ft.TextField(label=Lang.value("contents.template.cite.item.section"))

        self.loading = self.gui.ProgressRing(self.page)
        self.field_output = ft.TextField(label=Lang.value("common.output"))
        self.copy_button = self.gui.CopyButton(self.page, self.field_output.value)

        def on_changed_ref(e):
            if self.switch_ref.value:
                self.switch_ref.label = Lang.value("contents.template.cite.toggle_ref_on")
            else:
                self.switch_ref.label = Lang.value("contents.template.cite.toggle_ref_off")
            self.gui.safe_update(self.switch_ref)

        self.switch_ref.on_change = on_changed_ref
              
    def main(self):

        def on_clicked_url(e):
            try:
                url = self.field_url.value
                if WikiString.is_url(url):
                    self.url_from_variable(url)

                    self.output = self.create_template(
                        self.field_template_url.value,
                        self.field_template_title.value,
                        self.field_template_author.value,
                        self.field_template_website.value,
                        self.field_template_date.value,
                        self.field_template_quote.value,
                        self.field_template_section.value
                    )

                    self.field_output.value = self.output
                    self.copy_button.set(self.output)
                    self.gui.safe_update(self.field_output)
            
            except Exception as e:
                self.gui.popup_error(Lang.value("contents.template.cite.failed"), str(e))

        def on_clicked_generate(e):
            try:
                self.generate()
            except Exception as e:
                self.gui.popup_error(Lang.value("contents.template.cite.failed"), str(e))
    
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
                    ),
                    self.loading.main()
                ]),
                ft.Divider(),

                ft.Container(
                    ft.Column([
                        self.switch_ref,
                        self.field_template_url,
                        self.field_template_title,
                        self.field_template_author,
                        ft.Row([self.field_template_website, self.field_template_date]),
                        ft.Row([self.field_template_quote, self.field_template_section]),
                    ])
                ),
                ft.Container(height=30),
                ft.Divider(),
                
                ft.Row([
                    ft.Container(
                        content=ft.FilledTonalButton(
                            text=Lang.value("contents.template.common.button"),
                            icon=ft.icons.DOWNLOAD,
                            on_click=on_clicked_generate
                        ),
                        padding=10
                    ),
                    self.copy_button.main()
                ]),
                self.field_output
            ],
            spacing=0
        )

    def create_template(self, url: str, title: str, author: str = None, website: str = None, date: str = None, quote: str = None, section: str = None) -> str:
        output: str = ""

        if len(url)>0 and len(title)>0:
            if WikiString.is_url(url):
                output += "{{Cite|url=" + WikiString.html_escape(url) + "|title=" + WikiString.html_escape(title, [']', '|', '{', '}'])

        if type(website)==str:
            if len(website)>0:
                output += "|website=" + website
        if type(author)==str:
            if len(author)>0:
                output += "|author=" + author
        if type(date)==str:
            if len(date)>0:
                try:
                    date = WikiString.html_escape(date)
                    spl = date.split("-", 3)
                    y, m, d = spl[0], spl[1], spl[2]
                    if y.isdecimal() and m.isdecimal() and d.isdecimal():
                        y, m, d = int(y), int(m), int(d)
                        output += "|date=" + "{:04}-{:02}-{:02}".format(y, m, d)
                except IndexError:
                    pass
        if type(quote)==str:
            if len(quote)>0:
                quote = WikiString.html_escape(quote)
                output += "|quote=" + quote
        if type(section)==str:
            if len(section)>0:
                section = WikiString.html_escape(section)
                output += "|section=" + section
        
        if len(output)>0:
            output += "}}"

        if self.switch_ref.value:
            output = "<ref>" + output +"</ref>"
        return output

    def generate(self):
        self.output = self.create_template(
            self.field_template_url.value,
            self.field_template_title.value,
            self.field_template_author.value,
            self.field_template_website.value,
            self.field_template_date.value,
            self.field_template_quote.value,
            self.field_template_section.value
        )

        self.field_output.value = self.output
        self.copy_button.set(self.output)
        self.gui.safe_update(self.field_output)
    
    def url_from_variable(self, _url: str):
        self.loading.state(True)
        purl = urllib.parse.urlparse(_url)
        address = purl.netloc

        url: str = ""
        title: str = ""
        author: str = ""
        website: str = ""
        date: str = ""
        quote: str = ""
        section: str = ""


        if "playvalorant.com" in address:
            v = PlayValorant(_url)
            url = v.url
            title = v.title
            author = v.author
            website = "VALORANT"
            date =  datetime.datetime.strftime(v.date, "%Y-%m-%d")

            self.field_template_url.value = url
            self.field_template_title.value = title
            self.field_template_author.value = author
            self.field_template_website.value = website
            self.field_template_date.value = date

            self.gui.safe_update(self.field_template_url)
            self.gui.safe_update(self.field_template_title)
            self.gui.safe_update(self.field_template_author)
            self.gui.safe_update(self.field_template_website)
            self.gui.safe_update(self.field_template_date)
        
        elif "valorantesports.com" in address:
            self.ValorantEsportsDialog(self.page, _url, self.field_template_url, self.field_template_title, self.field_template_author, self.field_template_website, self.field_template_date)
        
        elif "zetadivision.com" in address:
            html = requests.get(_url)
            html.raise_for_status()
            soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html.text, "html.parser")

            title = soup.select_one("h1").get_text(strip=True)
            website = "ZETA DIVISION"
            date =  datetime.datetime.strftime(datetime.datetime.strptime(soup.select_one(".singleNews__date").get_text(strip=True), "%d %b %Y"), "%Y-%m-%d")

            title = re.sub("\n+", " ", title)

            self.field_template_url.value = _url
            self.field_template_title.value = title
            self.field_template_author.value = ""
            self.field_template_website.value = website
            self.field_template_date.value = date

            self.gui.safe_update(self.field_template_url)
            self.gui.safe_update(self.field_template_title)
            self.gui.safe_update(self.field_template_author)
            self.gui.safe_update(self.field_template_website)
            self.gui.safe_update(self.field_template_date)

        elif "twitter.com" in address:
            v = Tweet(_url)
            url = v.url
            title = v.text
            author = v.id
            website = "Twitter"
            date =  datetime.datetime.strftime(v.date, "%Y-%m-%d")

            title = re.sub("\n+", " ", title)

            self.field_template_url.value = url
            self.field_template_title.value = title
            self.field_template_author.value = author
            self.field_template_website.value = website
            self.field_template_date.value = date

            self.gui.safe_update(self.field_template_url)
            self.gui.safe_update(self.field_template_title)
            self.gui.safe_update(self.field_template_author)
            self.gui.safe_update(self.field_template_website)
            self.gui.safe_update(self.field_template_date)
            
        
        self.generate()
        self.loading.state(False)    

    class ValorantEsportsDialog():
        wait: float = 0.5
        locale: str = "ja-JP"
        format: str = "%Y年%m月%d日"

        def __init__(self, page: ft.Page, url: str, field_template_url, field_template_title, field_template_author, field_template_website, field_template_date):
            gui  = Gui(page)
            field_wait = ft.TextField(label=Lang.value("contents.template.cite.dialog.wait"), keyboard_type=ft.KeyboardType.NUMBER, value=self.wait)
            field_locale = ft.TextField(label=Lang.value("contents.template.cite.dialog.locale"), value=self.locale)
            field_format = ft.TextField(label=Lang.value("contents.template.cite.dialog.dateformat"), value=self.format)

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(Lang.value("contents.template.cite.dialog.title")),
                content=ft.Column([
                    ft.Text(Lang.value("contents.template.cite.dialog.description"), style=ft.TextThemeStyle.BODY_MEDIUM),
                    field_wait,
                    field_locale,
                    field_format
                ]),
                actions_alignment=ft.MainAxisAlignment.END
            )
            def close_dlg(e):
                dialog.open = False
                gui.safe_update(dialog)

                self.wait = field_wait.value
                self.locale = field_locale.value
                self.format = field_format.value

                v = ValorantEsports(url, self.wait)
                field_template_url.value = v.url
                field_template_title.value = v.title
                if v.author!=None:
                    field_template_author.value = v.author
                else:
                    field_template_author.value = ""
                field_template_website.value = "VALORANT Esports"
                field_template_date.value = datetime.date.strftime(v.date(self.locale, self.format), "%Y-%m-%d")

                gui.safe_update(field_template_url)
                gui.safe_update(field_template_title)
                gui.safe_update(field_template_author)
                gui.safe_update(field_template_website)
                gui.safe_update(field_template_date)

            dialog.actions = [ft.TextButton(Lang.value("common.ok"), on_click=close_dlg)]

            page.dialog = dialog
            dialog.open = True
            gui.safe_update(page)

