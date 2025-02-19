import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import fitz
# import requests

class Summary:
    def __init__(self, url, nepali_url, prompt):
        self.prompt = prompt
        self.filename_en = url
        self.filename_np = nepali_url
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=openai_api_key)

    #extracts the text from the chapter pdf
    def extract_text(self):
        # request = requests.get(self.filename)
        # filestream = io.BytesIO(request.content)
        text_content = None
        if self.filename_en is not None:
            pdf = fitz.open(self.filename_en)
            text_content = ''

            for page in pdf:
                text = page.get_text()
                text_content += text

        text_content_np = None
        if self.filename_np is not None:
            pdf = fitz.open(self.filename_np)
            text_content_np = ''

            for page in pdf:
                text = page.get_text()
                text_content_np += text

        return text_content, text_content_np

    #use the extracted text to send to OpenAI to summarize in ChatGPT
    def prompt_text(self, text):
        summarize_prompt = PromptTemplate(
            input_variables=["text"],
            template=self.prompt
        )
        summarize_chain = summarize_prompt | self.llm | StrOutputParser()
        summary = summarize_chain.invoke({"text": text})
        return summary
    
    #returning the summary
    def prompt_pdf(self):
        text_content_en, text_content_np = self.extract_text()
        summary_en = None
        summary_np = None

        if text_content_en:
            summary_en = self.prompt_text(text_content_en)
        if text_content_np:
            summary_np = self.prompt_text(text_content_np)
        return summary_en, summary_np