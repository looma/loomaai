from multilingual_pdf2text.pdf2text import PDF2Text
from multilingual_pdf2text.models.document_model.document import Document 
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pytesseract
import os
import fitz

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
    pdf = fitz.open(pdf_path)
    all_text = ''
    for page in pdf:
        text = page.get_text()
        all_text += text
    return all_text

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


