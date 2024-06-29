import flet as ft
from pydub import AudioSegment
import os

def main(page: ft.Page):
    page.title = "オーディオコンバーター"


    def on_input_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            input_file.value = e.files[0].path
            page.update()

    def on_output_dir_selected(e: ft.FilePickerResultEvent):
        if e.path:
            output_dir.value = e.path
            page.update()

    file_dialog = ft.FilePicker(on_result=on_input_file_selected)
    dir_dialog = ft.FilePicker(on_result=on_output_dir_selected)
    page.overlay.extend([file_dialog, dir_dialog])  # ここでFilePickerをページに追加

    def select_input_file(e):
        file_dialog.pick_files()

    def select_output_directory(e):
        dir_dialog.get_directory_path()

    def convert_audio(e):
        input_file_path = input_file.value
        output_dir_path = output_dir.value
        bitrate_value = bitrate.value
        sampling_rate_value = sampling_rate.value
        file_format_value = file_format.value
        bit_depth_value = bit_depth.value

        if not input_file_path or not output_dir_path or not sampling_rate_value or not file_format_value or (file_format_value == "wav" and not bit_depth_value):
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

        try:
            audio = AudioSegment.from_file(input_file_path)
            audio = audio.set_frame_rate(int(sampling_rate_value))
            output_file_path = os.path.join(output_dir_path, f"output_audio_low_bitrate.{file_format_value}")
            
            if file_format_value == "wav":
                audio.export(output_file_path, format=file_format_value, parameters=["-acodec", "pcm_s" + bit_depth_value])
            else:
                audio.export(output_file_path, format=file_format_value, bitrate=bitrate_value)
            
            page.snack_bar = ft.SnackBar(ft.Text(f"ファイルが正常に変換されました: {output_file_path}"), open=True)
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

    input_file = ft.TextField(label="入力ファイル", read_only=True, width=400,)
    output_dir = ft.TextField(label="出力ディレクトリ", value=os.path.expanduser("~/Documents/lofizer"), read_only=True, width=400,)
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
            ft.dropdown.Option("16"),
            ft.dropdown.Option("24"),
            ft.dropdown.Option("32")
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

    # 初期表示設定
    on_format_change(None)

    page.padding = 0  # 余白をゼロに設定
    page.margin = 0   # 余白をゼロに設定
    page.window_width = 680
    page.window_height = 380
    ui = ft.ListView (
        padding = 16,
        spacing = 22,
        controls =[
          ft.Row([input_file, ft.ElevatedButton("入力ファイルを選択", on_click=select_input_file)], expand=True),
          ft.Row([output_dir, ft.ElevatedButton("出力ディレクトリを選択", on_click=select_output_directory)], expand=True),
          ft.Row([file_format, sampling_rate, bitrate, bit_depth,  ], expand=True), 
          ft.ElevatedButton("変換", on_click=convert_audio, width=200, height=50)
            
        ]
    )
    page.add(ui)
    page.update()

ft.app(target=main)
