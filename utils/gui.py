import os, glob, pyperclip
import flet as ft
from utils.misc import JSON, Log, Config, Lang
from utils.wiki import Wiki

class Gui():
    page: ft.Page

    def __init__(self, page: ft.Page) -> None:
        self.page = page
    
    def popup(self, content: ft, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=content,
            bgcolor=color,
            show_close_icon=True
        )
        self.page.snack_bar.open = True
        try:
            self.page.update()
        except Exception as e:
            pass
    
    def popup_success(self, title: str, subtitle: str = None):
        if type(subtitle)==str:
            return self.popup(
                ft.Row([
                    ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(content=ft.Text(subtitle, color="black"), padding=3)
                ]),
                "green100"
            )
        else:
            return self.popup(
                ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                "green100"
            )
        
    def popup_notice(self, title: str, subtitle: str = None):
        if type(subtitle)==str:
            return self.popup(
                ft.Row([
                    ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(content=ft.Text(subtitle, color="black"), padding=3)
                ]),
                "blue100"
            )
        else:
            return self.popup(
                ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                "blue100"
            )
    
    def popup_warn(self, title: str, subtitle: str = None):
        if type(subtitle)==str:
            return self.popup(
                ft.Row([
                    ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(content=ft.Text(subtitle, color="black"), padding=3)
                ]),
                "yellow100"
            )
        else:
            return self.popup(
                ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                "yellow100"
            )
        
    def popup_error(self, title: str, subtitle: str = None):
        if type(subtitle)==str:
            return self.popup(
                ft.Row([
                    ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(content=ft.Text(subtitle, color="black"), padding=3)
                ]),
                "red100"
            )
        else:
            return self.popup(
                ft.Text(title, weight=ft.FontWeight.BOLD, color="black"),
                "red100"
            )
    
    def copy_button(self, text: str):
        def on_click(e):
            pyperclip.copy(text)
            self.popup_notice(Lang.value("common.copy_success"))
        
        return ft.IconButton(
            icon=ft.icons.COPY,
            tooltip=Lang.value("common.copy"),
            on_click=on_click
        ) 