"""
For user CLI tests for RAG 
"""

from ..common.RAG import *

def test_RAG(query:str):
    test = gen()
    test.makeChain("") # Path to file for RAG
    out = test.ask(query)

    return out

test_RAG("Give me a summary in 50 words")
