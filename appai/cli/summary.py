import os
import sys
import argparse 

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from appai.common.config import *
from appai.common.summary import *

def summary(filename, lang: str):
    cfg = ConfigInit()
    summarizer = Summary(cfg, filename)
    summary = summarizer.summarize_pdf(lang)
    print(summary)

def translate(filename, lang: str):
    cfg = ConfigInit()
    translator = Summary(cfg, filename)
    translated_text = translator.translate_pdf(lang)
    print(translated_text)

if __name__ == "__main__":
   # Create the parser
    parser = argparse.ArgumentParser(description="summary test tool")

    # Add the arguments
    parser.add_argument("command", type=str, help="The command to execute")
    parser.add_argument("filename", type=str, help="The filename to use")
    parser.add_argument("language", type=str, help="The language to use e.g. Nepali, English")

    # Parse the arguments
    args = parser.parse_args()
    if args.command == "summary":
        summary(args.filename, args.language)
    elif args.command == "translate":
        translate(args.filename, args.language)
    else:
        print(f"Unknown command '{args.command}'")