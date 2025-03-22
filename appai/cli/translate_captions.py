from deep_translator import GoogleTranslator
import os
from pathlib import Path
from alive_progress import alive_bar

def list_files_recursive(directory):
    return [str(file) for file in Path(directory).rglob("*") if file.is_file()]

def translate_vtt_to_np(vtt_path, vtts_dir):

    # File paths
    input_vtt_path = vtt_path
    output_vtt_path = vtts_dir+'ne/'+ vtt_path.removeprefix(vtts_dir+'en/')

    # Read the VTT file
    with open(input_vtt_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    translator = GoogleTranslator(source="en", target="ne")

    translated_lines = []
    for line in lines:
        stripped_line = line.strip()

        if stripped_line and "-->" not in stripped_line and not stripped_line.startswith("WEBVTT"):
            translated_line = translator.translate(stripped_line)
            print(translated_line)
        else:
            translated_line = stripped_line

        translated_lines.append(translated_line)

    os.makedirs(os.path.dirname(output_vtt_path), exist_ok=True)
    with open(output_vtt_path, "w", encoding="utf-8") as file:
        file.write("\n".join(translated_lines))

    print(output_vtt_path)

data_dir = os.getenv("DATADIR")

all_vtts = list_files_recursive(data_dir+"/content/video_captions/en/")
with alive_bar(len(all_vtts)) as progress_bar:
    for vtt in all_vtts:
        translate_vtt_to_np(vtt, data_dir+"/content/video_captions/")
