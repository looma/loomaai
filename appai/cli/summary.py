import os
import sys
import argparse 

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from langchain_openai import ChatOpenAI
from appai.common.config import *
from appai.common.summary import *

def summary(filename, lang: str):
    cfg = ConfigInit()
    openai_api_key = cfg.getv("openai_api_key")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=openai_api_key)
    summary = summarize_pdf(filename, lang, llm)
    print(summary)

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
    else:
        print(f"Unknown command '{args.command}'")

