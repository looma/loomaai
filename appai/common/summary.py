from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import fitz

class Summary:
    def __init__(self, cfg, pdf_path):
        self.filename = pdf_path
        openai_api_key = cfg.getv("openai_api_key")
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=openai_api_key)

#extracts the text from the chapter pdf
    def extract_text(self):
        pdf = fitz.open(self.filename)
        text_content = ''

        for page in pdf:
            text = page.get_text()
            text_content += text
        return text_content            

#use the extracted text to send to OpenAI to summarize in ChatGPT
    def summarize_text(self, text, chapter_language):
        summarize_prompt = PromptTemplate(
            input_variables=["text"],
            template="{text}\nPlease summarize the following text in one paragraph in " + str(chapter_language)
        )
        summarize_chain = summarize_prompt | self.llm | StrOutputParser()
        summary = summarize_chain.invoke({"text": text})
        return summary
    
#returning the summary
    def summarize_pdf(self, chapter_language):
        text_content = self.extract_text()
        summary = self.summarize_text(text_content, chapter_language)
        return summary
    
#translating the text into either Nepali or English
    def translate_text(self, text, tolanguage):
        translate_prompt = PromptTemplate(
                input_variables=["text"],
                template="Please translate the following text:\n{text} to" + str(tolanguage)
        )
        translate_chain = translate_prompt | self.llm | StrOutputParser()
        translated_text = translate_chain.invoke({"text": text})
        return translated_text
    
#Returning the translated text
    def translate_pdf(self, language):
        text_content = self.extract_text_from_pdf("Nepali")
        translated_content = self.translate_text(text_content, language)
        return translated_content