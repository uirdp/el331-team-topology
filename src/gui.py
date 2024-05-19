import FileManager
import DatabaseManager
import ContentDump

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
)


def main(page: Page):

    db = DatabaseManager.DatabaseManager()
    db.open_database()

    prog_bars: Dict[str, ProgressRing] = {}
    files = Ref[Column]()
    upload_button = Ref[ElevatedButton]()
    show_button = Ref[ElevatedButton]()

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
        dump = ContentDump.text_dump('sample text')


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
        ElevatedButton(
            "Show File Content",
            ref=upload_button,
            icon=icons.UPLOAD,
            on_click=show_file_content,
        ),
    )


flet.app(target=main)


def upload_file(db, path):
    file_manager = FileManager.FileManager()

    name, content = file_manager.get_file_content_and_name(path)

    db.insert_to_database(name, content)