from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyMuPDFLoader
from multilingual_pdf2text.pdf2text import PDF2Text
from multilingual_pdf2text.models.document_model.document import Document 
from langchain_core.documents.base import Document as Langchain_Doc
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import pytesseract
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from appai.common.config import *

# Configuration for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
os.environ['TESSDATA_PREFIX'] = r'/opt/homebrew/share/tessdata'

def extract_text_nepali(pdf_path):
    pdf_document = Document(document_path=pdf_path, language='nep')
    pdf2text = PDF2Text(document=pdf_document)
    content = pdf2text.extract()
    
    text_content = ''
    for page in content:
        text_content += page['text']
    return text_content

def extract_text_english(pdf_path):
    pages = PyMuPDFLoader(pdf_path, extract_images=True).load()
    return ' '.join(page.page_content for page in pages)

def extract_text_from_pdf(pdf_path, chapter_language):
    if chapter_language == "Nepali":
        return extract_text_nepali(pdf_path)
    elif chapter_language == "English":
        return extract_text_english(pdf_path)
    else:
        raise ValueError("Not Nepali or English. Please enter a different document")

def summarize_text(llm, text, chapter_language):
    summarize_prompt = PromptTemplate(
        input_variables=["text"],
        template="Please summarize the following text in 50 words using the same language it is written in:\n{text}"
    )
    summarize_chain = summarize_prompt | llm | StrOutputParser()
    summary = summarize_chain.invoke({"text": text})
    return summary

def summarize_pdf(pdf_path, chapter_language, llm):
    text_content = extract_text_from_pdf(pdf_path, chapter_language)
    summary = summarize_text(llm, text_content, chapter_language)
    return summary


