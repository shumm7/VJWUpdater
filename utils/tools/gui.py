import pyperclip
import flet as ft
from utils.tools.localize import Lang

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
    
    def dialog_ok(self, title: ft.Control, content: ft.Control):
        dialog = ft.AlertDialog(
            modal=True,
            title=title,
            content=content,
            actions_alignment=ft.MainAxisAlignment.END
        )

        def close_dlg(e):
            dialog.open = False
            try:
                self.page.update()
            except Exception as e:
                pass

        
        dialog.actions=[ft.TextButton(Lang.value("common.ok"), on_click=close_dlg)]

        self.page.dialog = dialog
        dialog.open = True
        try:
            self.page.update()
        except Exception as e:
            pass