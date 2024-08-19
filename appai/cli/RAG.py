"""
For user CLI tests for RAG 
"""

from ..common.RAG import *

def test_RAG(query:str):
    test = gen()
    test.makeChain("/Users/connorlee/Documents/GitHub/loomaai/data/files/chapters/textbooks/Class1/English/textbook_chapters/1EN01.02.pdf") # Path to file for RAG
    out = test.ask(query)

    return out

print(test_RAG("Give me a summary in 50 words"))
