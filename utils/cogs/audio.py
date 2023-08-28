import flet as ft
import datetime
import os
import zipfile
import subprocess
import shutil

from utils.tools.localize import Lang
from utils.tools.wiki import Wiki
from utils.tools.gui import Gui
from utils.tools.endpoint import Endpoint
from utils.tools.fetch import Fetch
from utils.tools.json import JSON
from utils.tools.api import API
from utils.tools.audio import Conversion

class Audio():
    page: ft.Page
    wiki: Wiki
    gui: Gui
    content: ft.Container

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page) -> None:
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.wemconv = WEMConv(wiki, gui, page)
        self.rename = Rename(wiki, gui, page)

    
    def main(self):
        self.content = ft.Container(self.wemconv.main(), expand=True)

        def on_clicked(e):
            i = e.control.selected_index
            contents = [
                self.wemconv.main(),
                self.rename.main()
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
                            icon_content=ft.Icon(ft.icons.AUDIO_FILE_OUTLINED),
                            selected_icon_content=ft.Icon(ft.icons.AUDIO_FILE),
                            label=Lang.value("contents.audio.wemconv.title"),
                        ),
                        ft.NavigationRailDestination(
                            icon_content=ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_OUTLINED),
                            selected_icon_content=ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE),
                            label=Lang.value("contents.audio.rename.title"),
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
                    expand=True
                )
            ]
        )

class WEMConv():
    files: list = []
    audio: Conversion

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui
        self.audio = Conversion()
        self.lists = ft.ListView(auto_scroll=True, height=300)
        self.state = ft.Text("")
        self.ring = self.gui.ProgressRing(self.page)
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)

    def main(self):
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.audio.wemconv.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.audio.wemconv.description"), style=ft.TextThemeStyle.BODY_SMALL),
                ),
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton(
                        text=Lang.value("contents.audio.wemconv.folder"),
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: self.file_picked()
                    ),
                    self.ring.main(),
                    self.state
                ]),
                self.lists,

                ft.Row(
                    [
                        ft.FilledTonalButton(
                            text=Lang.value("contents.audio.wemconv.wav"),
                            icon=ft.icons.AUDIO_FILE,
                            on_click=lambda e: self.convert_wav()
                        ),
                        self.gui.directory_button("output/audio/wav")
                    ]
                )
                
            ],
            scroll=True
        )
    
    def file_picked(self):
        def pick_files_result(e: ft.FilePickerResultEvent):
            self.lists.controls.clear()
            self.files.clear()
            
            try:
                for f in e.files:
                    self.files.append(f)
            except:
                pass

            self.gui.safe_update(self.lists)

        self.file_picker.on_result = pick_files_result
        self.file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["wem"]
        )

    def convert_wav(self):
        os.makedirs("output/audio/wav", exist_ok=True)
        self.ring.state(True)

        i: int = 1
        for f in self.files:
            self.state.value = Lang.value("contents.audio.wemconv.progress").format(current=i, max=len(self.files))
            self.gui.safe_update(self.state)
            try:
                self.audio.wem_to_wav(f.path, "output/audio/wav")
            except Exception as e:
                self.lists.controls.append(
                    ft.Card(
                        ft.Container(
                            ft.Column([
                                ft.Row(
                                    controls=[
                                        ft.Row([
                                            ft.IconButton(icon=ft.icons.WARNING, icon_color="yellow", tooltip=str(e)),
                                            ft.Text(f.name, weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.BODY_MEDIUM)
                                        ]),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Row([
                                    ft.Text(f.path, style=ft.TextThemeStyle.BODY_SMALL)
                                ])
                            ]),
                            padding=3
                        )
                    )
                )
            finally:
                i += 1
        
        self.lists.controls.clear()
        self.gui.safe_update(self.lists)
        self.state.value = ""
        self.gui.safe_update(self.state)
        self.ring.state(False)


class Rename():
    picker_resource: ft.FilePicker
    picker_json: ft.FilePicker
    files = []

    def __init__(self, wiki: Wiki, gui: Gui, page: ft.Page):
        self.wiki = wiki
        self.page = page
        self.gui = gui

        self.lists = ft.ListView(auto_scroll=True, height=300)
        self.dir1_show: ft.TextField = ft.TextField(label=Lang.value("contents.audio.rename.resources"), value="E:\Document\VJWUpdater\output\\audio\wav")
        self.dir2_show: ft.TextField = ft.TextField(label=Lang.value("contents.audio.rename.json"), value="E:\Document\FModel\Output\Exports\ShooterGame\Content\WwiseAudio\Localized\ja-JP\Events")
        self.state = ft.Text()
        self.ring = self.gui.ProgressRing(self.page)

        self.file_picker_json = ft.FilePicker()
        self.page.overlay.append(self.file_picker_json)
        self.file_picker_resources = ft.FilePicker()
        self.page.overlay.append(self.file_picker_resources)

        self.switch_child = ft.Switch(label=Lang.value("contents.audio.rename.toggle_child_on"), value=True)
        def on_changed_force(e):
            if self.switch_child.value:
                self.switch_child.label = Lang.value("contents.audio.rename.toggle_child_on")
            else:
                self.switch_child.label = Lang.value("contents.audio.rename.toggle_child_off")

            try:
                self.switch_child.update()
            except Exception as e:
                pass
        self.switch_child.on_change = on_changed_force

    def main(self):
        return ft.Column(
            [
                ft.ListTile(
                    title=ft.Text(Lang.value("contents.audio.rename.title"), style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(Lang.value("contents.audio.rename.description"), style=ft.TextThemeStyle.BODY_SMALL),
                ),
                ft.Divider(),
                self.switch_child,

                ft.Row(
                    [
                        self.dir1_show,
                        ft.IconButton(
                            icon = ft.icons.FOLDER,
                            on_click=lambda e: self.picked_resources()
                        )
                    ]
                ),
                ft.Row(
                    [
                        self.dir2_show,
                        ft.IconButton(
                            icon = ft.icons.FOLDER,
                            on_click=lambda e: self.picked_json()
                        )
                    ]
                ),

                ft.Row(
                    [
                        self.ring.main(),
                        self.state
                    ]
                ),

                ft.Divider(),
                self.lists,

                ft.Row(
                    [
                        ft.FilledTonalButton(
                            text=Lang.value("contents.audio.rename.action"),
                            icon=ft.icons.AUDIO_FILE,
                            on_click=lambda e: self.rename_audio()
                        ),
                    ]
                )
                
            ],
            scroll=True
        )

    def picked_resources(self):
        def pick_resources_result(e: ft.FilePickerResultEvent = None):
            if e.path!=None:
                self.dir1_show.value = e.path
                self.gui.safe_update(self.dir1_show)

        self.file_picker_resources.on_result = pick_resources_result
        self.gui.safe_update(self.file_picker_resources)
        self.file_picker_resources.get_directory_path()
    
    def picked_json(self):
        def pick_json_result(e: ft.FilePickerResultEvent = None):
            if e.path!=None:
                self.dir2_show.value = e.path
                self.gui.safe_update(self.dir2_show)

        self.file_picker_json.on_result = pick_json_result
        self.gui.safe_update(self.file_picker_json)
        self.file_picker_json.get_directory_path()
    
    def rename_audio(self):
        j: int = 1
        self.ring.state(True)

        try:
            self.files.clear()
            for root, dirs, files in os.walk(self.dir2_show.value):
                for file in files:
                    path = os.path.join(root, file)
                    _, ext = os.path.splitext(path)
                    if ext.lower()==".json":
                        self.files.append(path)
        except:
            pass

        for dir in self.files:
            self.state.value = Lang.value("contents.audio.rename.progress").format(current = j, max = len(self.files))
            self.gui.safe_update(self.state)

            try:
                dict = JSON.read(dir)
                AkAudioEventData: dict = dict[1]

                title = AkAudioEventData["Outer"]
                media_list = AkAudioEventData.get("Properties", {}).get("MediaList", [])
                id_list: list = []

                for media in media_list:
                    try:
                        source = media["AssetPathName"]
                        _, id = os.path.split(source)
                        id, _ = os.path.splitext(id)
                        id_list.append(id)
                    except:
                        pass
                
                i: int = 1
                for id in id_list:
                    try:
                        wem = os.path.join(self.dir1_show.value, id+".wem")
                        wav = os.path.join(self.dir1_show.value, id+".wav")
                        ogg = os.path.join(self.dir1_show.value, id+".ogg")

                        idx: str = ""
                        if i>1:
                            idx = "_" + str(i)

                        if os.path.isfile(wem):
                            os.rename(wem, os.path.join(self.dir1_show.value, title+idx+".wem"))
                        elif os.path.isfile(wav):
                            os.rename(wav, os.path.join(self.dir1_show.value, title+idx+".wav"))
                        elif os.path.isfile(ogg):
                            os.rename(ogg, os.path.join(self.dir1_show.value, title+idx+".ogg"))

                    except Exception as e:
                        pass
                    finally:
                        i += 1

            except Exception as e:
                self.gui.popup_error(Lang.value("contents.audio.rename.error"), str(e))
            finally:
                j += 1
        self.state.value = ""
        self.gui.safe_update(self.state)
        self.ring.state(False)