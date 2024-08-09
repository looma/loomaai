from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyMuPDFLoader
from multilingual_pdf2text.pdf2text import PDF2Text
from multilingual_pdf2text.models.document_model.document import Document 
from langchain_core.documents.base import Document as Langchain_Doc
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
os.environ['TESSDATA_PREFIX'] = r'/opt/homebrew/share/'

def extract_text(pdf_path, chapter_language: str):
    if chapter_language == "Nepali":
        pdf_document = Document(document_path= pdf_path, language='nep')
        pdf2text = PDF2Text(document=pdf_document)
        content = pdf2text.extract()
        doc = Langchain_Doc(page_content='')
        for page in content:
            text = page['text']
            doc.page_content += text
        return doc
    elif chapter_language == "English":
        pages = PyMuPDFLoader(pdf_path, extract_images=True).load()
        return pages

def query_llm(llm, pages, chapter_language):
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    if chapter_language == "Nepali":
        summary = chain.invoke([pages])
    elif chapter_language == "English":
        summary = chain.invoke(pages)
    return summary['output_text']
