import flet as ft
from pydub import AudioSegment
import os

def main(page: ft.Page):
    page.title = "オーディオコンバーター"

    selected_files = []

    def on_input_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            selected_files.extend(e.files)
            update_file_list()
            page.update()

    def update_file_list():
        file_list.controls.clear()
        for file in selected_files:
            file_name = os.path.basename(file.path)  # フルパスからファイル名を抽出
            file_list.controls.append(ft.Text(file_name))
        page.update()

    def on_output_dir_selected(e: ft.FilePickerResultEvent):
        if e.path:
            output_dir.value = e.path
            page.update()

    def open_output_directory(e):
        output_dir_path = output_dir.value
        if os.path.exists(output_dir_path):
            os.system(f'open "{output_dir_path}"')
        else:
            page.snack_bar = ft.SnackBar(ft.Text("出力ディレクトリが存在しません"), open=True)
            page.update()

    file_dialog = ft.FilePicker(on_result=on_input_file_selected)
    dir_dialog = ft.FilePicker(on_result=on_output_dir_selected)
    page.overlay.extend([file_dialog, dir_dialog])  # ここでFilePickerをページに追加

    def select_input_file(e):
        file_dialog.pick_files(allow_multiple=True)  # ここで複数ファイル選択を許可

    def select_output_directory(e):
        dir_dialog.get_directory_path()

    def convert_audio(e):
        output_dir_path = output_dir.value
        bitrate_value = bitrate.value
        sampling_rate_value = sampling_rate.value
        file_format_value = file_format.value
        bit_depth_value = bit_depth.value

        if not selected_files or not output_dir_path or not sampling_rate_value or not file_format_value or (file_format_value == "wav" and not bit_depth_value):
            page.snack_bar = ft.SnackBar(ft.Text("すべてのフィールドを入力してください"), open=True)
            page.update()
            return

        # 出力ディレクトリが存在しない場合は作成
        if not os.path.exists(output_dir_path):
            try:
                os.makedirs(output_dir_path)
            except Exception as e:
                page.snack_bar = ft.SnackBar(ft.Text(f"ディレクトリの作成中にエラーが発生しました: {e}"), open=True)
                page.update()
                return

        for file in selected_files:
            try:
                audio = AudioSegment.from_file(file.path)
                audio = audio.set_frame_rate(int(sampling_rate_value))
                
                input_file_name = os.path.splitext(os.path.basename(file.path))[0]
                if file_format_value == "wav":
                    if bit_depth_value == "8":
                        audio = audio.set_sample_width(1)
                    elif bit_depth_value == "16":
                        audio = audio.set_sample_width(2)
                    output_file_name = f"{input_file_name}-{sampling_rate_value}-{bit_depth_value}.{file_format_value}"
                else:
                    output_file_name = f"{input_file_name}-{sampling_rate_value}-{bitrate_value}.{file_format_value}"
                
                output_file_path = os.path.join(output_dir_path, output_file_name)
                audio.export(output_file_path, format=file_format_value, bitrate=bitrate_value if file_format_value != "wav" else None)
                
                page.snack_bar = ft.SnackBar(ft.Text(f"ファイルが正常に変換さ���ました: {output_file_path}"), open=True)
                page.update()
            except Exception as e:
                page.snack_bar = ft.SnackBar(ft.Text(f"変換中にエラーが発生しました: {e}"), open=True)
                page.update()

    def on_format_change(e):
        if file_format.value == "wav":
            bitrate.visible = False
            bit_depth.visible = True
        else:
            bitrate.visible = True
            bit_depth.visible = False
        page.update()

    output_dir = ft.TextField(label="出力ディレクトリ", value=os.path.expanduser("~/Documents/lofizer"), read_only=True, expand=True,)
    bitrate = ft.Dropdown(
        label="ビットレート",
        options=[
            ft.dropdown.Option("8k"),
            ft.dropdown.Option("16k"),
            ft.dropdown.Option("32k"),
            ft.dropdown.Option("48k"),
            ft.dropdown.Option("64k"),
            ft.dropdown.Option("96k"),
            ft.dropdown.Option("128k"),
            ft.dropdown.Option("192k"),
            ft.dropdown.Option("256k"),
            ft.dropdown.Option("320k")
        ],
        value="32k",
        width=200,
    )
    bit_depth = ft.Dropdown(
        label="ビット深度",
        options=[
            ft.dropdown.Option("8"),
            ft.dropdown.Option("16"),
        ],
        value="16",
        width=200,
    )
    sampling_rate = ft.Dropdown(
        label="サンプリングレート",
        options=[
            ft.dropdown.Option("4000"),
            ft.dropdown.Option("8000"),
            ft.dropdown.Option("11025"),
            ft.dropdown.Option("16000"),
            ft.dropdown.Option("22050"),
            ft.dropdown.Option("32000"),
            ft.dropdown.Option("44100"),
            ft.dropdown.Option("48000"),
        ],
        value="8000",
        width=200,
    )
    file_format = ft.Dropdown(
        label="フォーマット",
        options=[
            ft.dropdown.Option("mp3"),
            ft.dropdown.Option("wav")
        ],
        value="wav",  # デフォルト値をwavに設定
        width=200,
        on_change=on_format_change
    )

    file_list = ft.ListView(padding=0, spacing=4)

    # 初期表示設定
    on_format_change(None)

    page.padding = 0  # 余白をゼロに設定
    page.margin = 0   # 余白をゼロに設定
    page.window.width = 680
    page.window.height = "auto"
    ui = ft.ListView (
        padding = 16,
        spacing = 30,
        controls =[
            ft.ListView(
                padding = 0,
                spacing = 8,
                controls = [
                    ft.ElevatedButton("入力ファイルを選択", on_click=select_input_file, width=200),
                    file_list,
                ],
            ),
            ft.ListView(
                padding = 0,
                spacing = 8,
                controls = [
                    ft.Row([
                        output_dir, 
                    ], expand=True),
                    ft.Row([
                        ft.ElevatedButton("出力ディレクトリを選択", on_click=select_output_directory),
                        ft.ElevatedButton("出力ディレクトリを開く", on_click=open_output_directory)  # 追加
                    ]),
                ]
            ),
            ft.Row([file_format, sampling_rate, bitrate, bit_depth,  ], expand=True), 
            ft.ElevatedButton("変換", on_click=convert_audio, width=200, height=50)
        ]
    )
    page.add(ui)
    page.update()

ft.app(target=main)
