"""
For user CLI tests for RAG 
"""

import os
import sys
from langchain_openai import ChatOpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.RAG import *
from common.config import *

def test_RAG(query:str):
    test = gen()
    test.makeChain("") # Path to file for RAG
    out = test.ask(query)

    return out

test_RAG("Give me a summary in 50 words")
