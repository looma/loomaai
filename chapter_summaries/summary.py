from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader

def extract_text(pdf_path: str):
    loader = PyPDFLoader(pdf_path, extract_images=True)
    pages = loader.load()
    return pages

def query_llm(llm, pages):
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.invoke(pages)
    return summary['output_text']