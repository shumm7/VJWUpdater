import pyperclip, subprocess, os, datetime
import flet as ft
from utils.tools.localize import Lang
from utils.tools.json import JSON

class Gui():
    page: ft.Page
    file_picker: ft.FilePicker

    def __init__(self, page: ft.Page) -> None:
        self.page = page

    def safe_update(self, o: ft.Control):
        try:
            o.update()
        except:
            pass
    
    def popup(self, content: ft, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=content,
            bgcolor=color,
            show_close_icon=True
        )
        self.page.snack_bar.open = True
        self.safe_update(self.page)
    
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
        time: str = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")
        os.makedirs("output/logs", exist_ok=True)
        JSON.save(f"output/logs/log_{time}_error.json", {"title": title, "subtitle": subtitle})

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

    def directory_button(self, path: str):
        return ft.IconButton(
            icon=ft.icons.FOLDER_OPEN,
            tooltip=Lang.value("common.open_directory"),
            on_click=lambda e: subprocess.Popen(["explorer", path.replace('/', '\\')], shell=True)
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
        self.safe_update(self.page)

    class CopyButton():
        def __init__(self, page: ft.Page, text: str = None):
            self.page = page
            self.gui = Gui(page)
            self.text = text
        
        def main(self):
            def on_click(e):
                pyperclip.copy(self.text)
                self.gui.popup_notice(Lang.value("common.copy_success"))
            
            self.button = ft.IconButton(
                icon=ft.icons.COPY,
                tooltip=Lang.value("common.copy"),
                on_click=on_click
            )
            return self.button

        def set(self, text: str = None):
            self.text = text

            def on_click(e):
                pyperclip.copy(text)
                self.gui.popup_notice(Lang.value("common.copy_success"))
            
            self.button.on_click = on_click
            self.gui.safe_update(self.button)  

    class ExportButton():
        filename: str

        def __init__(self, page: ft.Page, action):
            self.page = page
            self.gui = Gui(page)
            self.action = action
        
        def main(self):
            def on_click(e):
                try:
                    self.action()
                    self.gui.popup_notice(Lang.value("common.export_success"), self.filename)
                except Exception as e:
                    pass
            
            self.button = ft.IconButton(
                icon=ft.icons.DOWNLOAD,
                tooltip=Lang.value("common.export"),
                on_click=on_click
            )
            return self.button

        def set(self, filename: str = None):
            self.filename = filename
            self.gui.safe_update(self.button)

    class UpdateResult():
        page: ft.Page
        lists: ft.ListView
        data: list

        def __init__(self, page: ft.Page, output_dir: str) -> None:
            self.page = page
            self.gui = Gui(page)
            self.lists = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
            self.data = []
            self.output = output_dir

            def update_button(e):
                self.clear()
                for d in self.data:
                    if self.check_success.value and d["mode"]=="success":
                        self._add_list(d["value"], d["title"], d["filename"], d["image_src"], d["mode"], d["reason"], d["description"])
                    if self.check_skipped.value and d["mode"]=="skipped":
                        self._add_list(d["value"], d["title"], d["filename"], d["image_src"], d["mode"], d["reason"], d["description"])
                    if self.check_warn.value and d["mode"]=="warn":
                        self._add_list(d["value"], d["title"], d["filename"], d["image_src"], d["mode"], d["reason"], d["description"])
                    elif self.check_error.value and d["mode"]=="error":
                        self._add_list(d["value"], d["title"], d["filename"], d["image_src"], d["mode"], d["reason"], d["description"])
                
                self.gui.safe_update(self.lists)
            
            self.check_success = ft.Checkbox(value=True, label=Lang.value("common.success"), on_change=update_button)
            self.check_skipped = ft.Checkbox(value=False, label=Lang.value("common.skipped"), on_change=update_button)
            self.check_warn = ft.Checkbox(value=True, label=Lang.value("common.warn"), on_change=update_button)
            self.check_error = ft.Checkbox(value=True, label=Lang.value("common.error"), on_change=update_button)
            self.export_button = self.gui.ExportButton(self.page, self._export_log)
            
            """
            self.check = ft.Row([
                self.check_success, self.check_skipped, self.check_warn, self.check_error, ft.Container(self.export_button.main(), margin=2)
            ])
            """
            self.directory_button = self.gui.directory_button(self.output)
            self.export_button = self.gui.ExportButton(self.page, self._export_log)
            self.check = ft.Row([self.directory_button, self.export_button.main()])
        
        def main(self) -> ft.ListView:
            return ft.Column([
                self.check,
                self.lists
            ])

        def clear(self):
            self.lists.controls.clear()
            self.gui.safe_update(self.lists)
        
        def append(self, value: dict, title: str, filename: str, image_src: str, mode: str, reason: str, description: str = None):
            self.data.append({
                "value": value,
                "title": title,
                "filename": filename,
                "image_src": image_src,
                "mode": mode,
                "reason": reason,
                "description": description
            })

            if self.check_success.value and mode=="success":
                self._add_list(value, title, filename, image_src, mode, reason, description)
            if self.check_skipped.value and mode=="skipped":
                self._add_list(value, title, filename, image_src, mode, reason, description)
            if self.check_warn.value and mode=="warn":
                self._add_list(value, title, filename, image_src, mode, reason, description)
            if self.check_error.value and mode=="error":
                self._add_list(value, title, filename, image_src, mode, reason, description)
        
        def _append_list(self, ctrl: ft.Control):
            self.lists.controls.append(ctrl)
            self.gui.safe_update(self.lists)
        
        def _add_list(self, value: dict, title: str, filename: str, image_src: str, mode: str, reason: str, description: str = None):
            def close_dialog(e):
                dialog.open = False
                try:
                    self.page.update()
                except Exception as e:
                    pass

            def open_dialog(e):
                self.page.dialog = dialog
                dialog.open = True
                try:
                    self.page.update()
                except Exception as e:
                    pass
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(filename),
                content=ft.Column([
                    ft.Text(title, weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM),
                    ft.Row([
                        ft.Text(value.get("uuid", ""), style=ft.TextThemeStyle.BODY_SMALL),
                        self.gui.CopyButton(self.page, value.get("uuid", "")).main()
                    ]),
                    ft.Image(src=image_src, width=200, height=200, fit=ft.ImageFit.CONTAIN)
                ]),
                actions=[
                    ft.TextButton(Lang.value("common.ok"), on_click=close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            iconbutton: ft.IconButton
            imagebutton = ft.IconButton(
                icon=ft.icons.PREVIEW,
                tooltip=Lang.value("common.preview"),
                on_click = open_dialog
            ) 
            buttons = ft.Row([imagebutton])
            if type(description)==str:
                buttons.controls.insert(
                    0,
                    ft.IconButton(
                        icon=ft.icons.HELP,
                        tooltip=Lang.value("common.detail"),
                        on_click=lambda e: self.gui.dialog_ok(ft.Text(reason), ft.Text(description, style=ft.TextThemeStyle.BODY_MEDIUM))
                    )
                )

            if mode=="success":
                iconbutton = ft.IconButton(icon=ft.icons.CHECK, icon_color="green", tooltip=reason)
            elif mode=="skipped":
                iconbutton = ft.IconButton(icon=ft.icons.NEARBY_ERROR, icon_color="green", tooltip=reason)
            elif mode=="warn":
                iconbutton = ft.IconButton(icon=ft.icons.WARNING, icon_color="yellow", tooltip=reason)
            elif mode=="error":
                iconbutton = ft.IconButton(icon=ft.icons.ERROR, icon_color="red", tooltip=reason)

            self._append_list(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Row(
                                controls=[
                                    ft.Row([
                                        iconbutton,
                                        ft.Text(title, weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM)
                                    ]),
                                    buttons
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Row([
                                ft.Text(filename, style=ft.TextThemeStyle.BODY_SMALL)
                            ])
                        ]),
                        padding=3
                    )
                )
            )    
        
        def _export_log(self):
            time: str = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")
            output: dict = {
                "success": [],
                "skipped": [],
                "warn": [],
                "error": []
            }

            for d in self.data:
                output[d["mode"]].append({
                    "uuid": d["value"].get("uuid", ""),
                    "name": d["title"],
                    "filename": d["filename"],
                    "image": d["image_src"],
                    "reason": d["reason"],
                    "description": d["description"],
                })
            
            self.export_button.set(f"output/logs/log_{time}.json")
            os.makedirs("output/logs", exist_ok=True)
            JSON.save(f"output/logs/log_{time}.json", output)

    class Result():
        page: ft.Page
        result = ft.ListTile

        def __init__(self, page: ft.Page):
            self.page = page
            self.gui = Gui(page)
        
        def main(self) -> ft.Container:
            self.result = ft.ListTile()
            return ft.Container(self.result, padding=10)

        def success(self, title: str = None, subtitle: str = None, icon: str = ft.icons.CHECK, icon_color: str = "green"):
            self.result.leading=ft.Icon(name=icon, color=icon_color)
            self.result.title=ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM)
            self.result.subtitle=ft.Text(subtitle, style=ft.TextThemeStyle.BODY_SMALL)

            self.gui.safe_update(self.result)
        
        def warn(self, title: str = None, subtitle: str = None, icon: str = ft.icons.WARNING, icon_color: str = "yellow"):
            self.result.leading=ft.Icon(name=icon, color=icon_color)
            self.result.title=ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM)
            self.result.subtitle=ft.Text(subtitle, style=ft.TextThemeStyle.BODY_SMALL)

            self.gui.safe_update(self.result)
        
        def info(self, title: str = None, subtitle: str = None, icon: str = ft.icons.INFO, icon_color: str = "blue"):
            self.result.leading=ft.Icon(name=icon, color=icon_color)
            self.result.title=ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM)
            self.result.subtitle=ft.Text(subtitle, style=ft.TextThemeStyle.BODY_SMALL)

            self.gui.safe_update(self.result)
    
        def error(self, title: str = None, subtitle: str = None, icon: str = ft.icons.ERROR_OUTLINE, icon_color: str = "red"):
            self.result.leading=ft.Icon(name=icon, color=icon_color)
            self.result.title=ft.Text(title, style=ft.TextThemeStyle.BODY_MEDIUM)
            self.result.subtitle=ft.Text(subtitle, style=ft.TextThemeStyle.BODY_SMALL)

            self.gui.safe_update(self.result)
        
        def clear(self):
            self.result.leading=None
            self.result.title=None
            self.result.subtitle=None

            self.gui.safe_update(self.result)

    class ProgressRing():
        page: ft.Page
        container: ft.Container

        def __init__(self, page: ft.Page, width=16, height=16, stroke_width=2):
            self.page = page
            self.width = width
            self.height = height
            self.stroke_width = stroke_width
            self.gui = Gui(page)
        
        def main(self):
            self.container = ft.Container()
            return self.container
        
        def state(self, state: bool = False):
            try:
                if state:
                    self.container.content = ft.ProgressRing(width=self.width, height=self.height, stroke_width=self.stroke_width)
                else:
                    self.container.content = None

                self.gui.safe_update(self.container)
            except Exception as e:
                print(e)
