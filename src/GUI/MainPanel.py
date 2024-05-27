import FileManager
import DatabaseManager
import ContentDump
import SearchWordPanel

from typing import Dict

import flet
from flet import (
    Column,
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    FilePickerUploadFile,
    Page,
    ProgressRing,
    Ref,
    Row,
    Text,
    icons,
    TextField,
    Radio,
    RadioGroup,
    Tabs,
    Tab,
    Container,
)

search_number = 0
def main(page: Page):

    db = DatabaseManager.DatabaseManager()
    db.open_database()

    prog_bars: Dict[str, ProgressRing] = {}
    files = Ref[Column]()
    upload_button = Ref[ElevatedButton]()

    # show
    show_button = Ref[ElevatedButton]()
    search_options = RadioGroup(content=Row([
        Radio(value="original_name", label="Original Name"),
        Radio(value="updated_name", label="Updated Name"),
        Radio(value="id", label="ID"),]))

    file_search_target = Ref[TextField]()

    search_token_button = Ref[ElevatedButton]()
    target_token = Ref[TextField]()

    t = Tabs(
        selected_index=0,
        animation_duration=200,
        tabs=[
            Tab(

            ),
            Tab(
                text="search",
                icon=icons.SEARCH,
                content=Container(
                    SearchWordPanel.WordSearch(),
                )
            )
        ]
    )

    def file_picker_result(e: FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(Row([prog, Text(f.name)]))

        page.update()

    def on_upload_progress(e: FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)

    def upload_files(e):
        file_manager = FileManager.FileManager()

        uf = []
        if file_picker.result is not None and file_picker.result.files is not None:

            for f in file_picker.result.files:
                name, content = file_manager.get_file_content_and_name(f.path)
                db.insert_to_database(name, content)

    def show_file_content(e):
        option = search_options.value
        key = file_search_target.current.value

        show_file_from_database(key, option)

    def show_file_from_database(key, option):
        if option == 'original_name':
            id = db.translate_to_id(key, 'original_name')
            print(id)
            s = db.get_content(id)

            ContentDump.text_dump(s)

    def search_token(e):
        global search_number
        file_manager = FileManager.FileManager()
        option = search_options.value
        f_key = file_search_target.current.value
        t_key = target_token.current.value
        if option == 'original_name':
            id = db.translate_to_id(f_key, 'original_name')
            s = db.get_content(id)

            ContentDump.search_token(s, t_key)

    # hide dialog in a overlay
    page.overlay.append(file_picker)

    page.add(

        ElevatedButton(
            "Select files...",
            icon=icons.FOLDER_OPEN,
            on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        ),
        Column(ref=files),
        ElevatedButton(
            "Upload",
            ref=upload_button,
            icon=icons.UPLOAD,
            on_click=upload_files,
        ),

        TextField(ref=file_search_target, label="file name or id"),
        search_options,
        TextField(ref=target_token, label='search token'),


        Row(
            controls=[
                ElevatedButton(
                    "Show content",
                    ref=upload_button,
                    icon=icons.DOWNLOAD,
                    on_click=show_file_content,
                ),

                ElevatedButton(
                    "Search token",
                    ref=search_token_button,
                    icon=icons.SEARCH,
                    on_click=search_token,
                )
            ]
        )

    )


flet.app(target=main)


