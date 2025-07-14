from deep_translator import GoogleTranslator
import os
from pathlib import Path
from alive_progress import alive_bar

from ..common.summary import prompt_text
from langchain_openai import ChatOpenAI

def list_files_recursive(directory):
    return [str(file) for file in Path(directory).rglob("*[!_np].vtt") if file.is_file()]


def translate_vtt_to_np(vtt_path, llm):
    # File paths
    input_vtt_path = vtt_path
    output_vtt_path = vtt_path.removesuffix(".vtt") + "_np.vtt"

    if os.path.exists(output_vtt_path):
        print("Skipping " + vtt + ": translation already on disk")
        return

    # Read the VTT file
    with open(input_vtt_path, "r", encoding="utf-8") as file:
        lines = file.read()

    # translator = GoogleTranslator(source="en", target="ne")
    messages = [
        (
            "system",
            "The user will supply a VTT caption track in English. You are to translate the caption track to Nepali, preserving the timestamps as they are, and only translating the english lines to nepali. Return a valid VTT caption track. ",
        ),
        ("user", lines),
    ]

    translated = llm.invoke(messages).content

    os.makedirs(os.path.dirname(output_vtt_path), exist_ok=True)
    with open(output_vtt_path, "w", encoding="utf-8") as file:
        file.write(translated)

data_dir = os.getenv("DATADIR")

all_vtts = list_files_recursive(data_dir + "/content/videos/")

llm = ChatOpenAI()

with alive_bar(len(all_vtts)) as progress_bar:
    for vtt in all_vtts:
        try:
            translate_vtt_to_np(vtt, llm)
            print("Success: " + vtt)
        except Exception as e:
            print(f"Error on {vtt}: {e}")
        progress_bar()
