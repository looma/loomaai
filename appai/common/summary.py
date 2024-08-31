from langchain_openai import ChatOpenAI
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


class Summary:
    def __init__(self, cfg, pdf_path):
        self.filename = pdf_path
        openai_api_key = cfg.getv("openai_api_key")
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=openai_api_key)

    def extract_text_nepali(self):
        pdf_document = Document(document_path=self.filename, language='nep')
        pdf2text = PDF2Text(document=pdf_document)
        content = pdf2text.extract()
        text_content = ''
        for page in content:
            text_content += page['text']
        return text_content

    def extract_text_english(self):
        pdf = fitz.open(self.filename)
        text_content = ''

        for page in pdf:
            text = page.get_text()
            text_content += text
        return text_content

    def extract_text_from_pdf(self, chapter_language):
        if chapter_language == "Nepali":
            return self.extract_text_nepali()
        elif chapter_language == "English":
            return self.extract_text_english()
        else:
            raise ValueError("Not Nepali or English. Please enter a different document")

    def summarize_text(self, text, chapter_language):
        summarize_prompt = PromptTemplate(
            input_variables=["text"],
            template="{text}\nPlease summarize the following text in one paragraph in " + str(chapter_language)
        )
        summarize_chain = summarize_prompt | self.llm | StrOutputParser()
        summary = summarize_chain.invoke({"text": text})
        return summary

    def summarize_pdf(self, chapter_language):
        text_content = self.extract_text_from_pdf(chapter_language)
        summary = self.summarize_text( text_content, chapter_language)
        return summary

    def translate_text(self, text, tolanguage):
        translate_prompt = PromptTemplate(
                input_variables=["text"],
                template="Please translate the following text:\n{text} to" + str(tolanguage)
        )
        translate_chain = translate_prompt | self.llm | StrOutputParser()
        translated_text = translate_chain.invoke({"text": text})
        return translated_text

    def translate_pdf(self, language):
        text_content = self.extract_text_from_pdf("Nepali")
        translated_content = self.translate_text(text_content, language)
        return translated_content