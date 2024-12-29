import io

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import fitz
import requests

class Summary:
    def __init__(self, cfg, url):
        self.filename = url
        openai_api_key = cfg.getv("openai_api_key")
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=openai_api_key)

#extracts the text from the chapter pdf
    def extract_text(self):
        request = requests.get(self.filename)
        filestream = io.BytesIO(request.content)
        pdf = fitz.open(stream=filestream, filetype="pdf")
        text_content = ''

        for page in pdf:
            text = page.get_text()
            text_content += text
        return text_content            

#use the extracted text to send to OpenAI to summarize in ChatGPT
    def summarize_text(self, text):
        summarize_prompt = PromptTemplate(
            input_variables=["text"],
            template="Please summarize the following text in one paragraph in the same language it is written in \n if the text is in Nepali keep it in Nepali and if the text is in English keep it in English\n{text}"
        )
        summarize_chain = summarize_prompt | self.llm | StrOutputParser()
        summary = summarize_chain.invoke({"text": text})
        return summary
    
#returning the summary
    def summarize_pdf(self):
        text_content = self.extract_text()
        summary = self.summarize_text(text_content)
        return summary
    
#returning the quiz
    def quiz_pdf(self):
        text_content = self.extract_text()
        quiz = self.quiz_text(text_content)
        return quiz
    def quiz_text(self, text):
        quiz_prompt = PromptTemplate(
            input_variables=["text"],
            template="Please make a quiz of the following text in the same language it is written in. Make an answer key but make sure answers are not shown at all on the quiz itself. If the text is in Nepali keep it in Nepali and if the text is in English keep it in English \n {text}"
        )
        quiz_chain = quiz_prompt | self.llm | StrOutputParser()
        quiz = quiz_chain.invoke({"text": text})
        return quiz
    
    def detailSummary_text(self, text):
        summarize_prompt = PromptTemplate(
            input_variables=["text"],
            template="Please summarize the following text in one paragraph in the same language it is written in \n if the text is in Nepali keep it in Nepali and if the text is in English keep it in English\n{text}"
        )
        summarize_chain = summarize_prompt | self.llm | StrOutputParser()
        summary = summarize_chain.invoke({"text": text})
        return summary
    
#returning the summary
    def detailSummary_pdf(self):
        text_content = self.extract_text()
        summary = self.detailSummary_text(text_content)
        return summary
    
    def topic_text(self, text):
        topic_prompt = PromptTemplate(
            input_variables=["text"],
            template="Please give me the main and sub topics of the text in the same language it is written in \n if the text is in Nepali keep it in Nepali and if the text is in English keep it in English\n{text}"
        )
        topic_chain = topic_prompt | self.llm | StrOutputParser()
        topic = topic_chain.invoke({"text": text})
        return topic
    
#returning the summary
    def topic_pdf(self):
        text_content = self.extract_text()
        topic = self.topic_text(text_content)
        return topic
    
    def translate_pdf(self):
        text_content = self.extract_text()
        translate = self.translate_text(text_content)
        return translate
    
    def translate_text(self, text):
        translate_prompt = PromptTemplate(
            input_variables=["text"],
            template="If the following text is in English, please translate it to Nepali. If the following text is in Nepali, please translate it to English.{text}"
        )
        translate_chain = translate_prompt | self.llm | StrOutputParser()
        translate = translate_chain.invoke({"text": text})
        return translate