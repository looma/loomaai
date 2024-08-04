from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import sys
import os
from langchain_community.document_loaders import PyMuPDFLoader

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def extract_text(pdf_path: str):
    #loader = PyPDFLoader(pdf_path, extract_images=True)
    #pages = loader.load()

    pages = PyMuPDFLoader(pdf_path).load()
    return pages

def query_llm(llm, pages, size):
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.invoke(pages)
    return summary['output_text']