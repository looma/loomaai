from deep_translator import GoogleTranslator
import os
from pathlib import Path
from alive_progress import alive_bar

from ..common.summary import prompt_text
from ..common.llmselect import LLMSelect


def list_files_recursive(directory):
    return [str(file) for file in Path(directory).rglob("*") if file.is_file()]


def translate_vtt_to_np(vtt_path, vtts_dir, llm):
    # File paths
    input_vtt_path = vtt_path
    output_vtt_path = vtts_dir + "ne/" + vtt_path.removeprefix(vtts_dir + "en/")

    # Read the VTT file
    with open(input_vtt_path, "r", encoding="utf-8") as file:
        lines = file.read()

    # translator = GoogleTranslator(source="en", target="ne")

    translated = (
        prompt_text(
            llm,
            "Translate the following VTT captions to Nepali, preserving all formatting and timestamps, only translating the sentences, recognizing that they may span several lines. Return only valid VTT with no extra comments: {text}",
            lines,
        )
        .removeprefix("```")
        .removesuffix("```")
    )

    os.makedirs(os.path.dirname(output_vtt_path), exist_ok=True)
    with open(output_vtt_path, "w", encoding="utf-8") as file:
        file.write(translated)


data_dir = os.getenv("DATADIR")

all_vtts = list_files_recursive(data_dir + "/content/video_captions/en/")
vtts_dir = data_dir + "/content/video_captions/"

llm = LLMSelect().llm()  # This will use the default LLM selected in LLMSelect

with alive_bar(len(all_vtts)) as progress_bar:
    for vtt in all_vtts:
        try:
            if os.path.exists(vtts_dir + "ne/" + vtt.removeprefix(vtts_dir + "en/")):
                print("Skipping " + vtt + ": translation already on disk")
            else:
                translate_vtt_to_np(vtt, vtts_dir, llm)
                print("Translated " + vtt)
        except Exception as e:
            print(f"Error on {vtt}: {e}")
        progress_bar()
