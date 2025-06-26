import os

import streamlit as st
from common.llmselect import LLMSelect

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


st.title("LoomaAI")

def LoomaEntry():
    llm = LLMSelect().llm()
    llm_name, llm_model = LLMSelect().llm_namemodel()
    st.write(llm_name, "    ", llm_model)
    template = """Question: {question}
    Instructions: {instructions}"""
    with st.form("my_form"):
        qtext = st.text_area("Enter question:", "Please tell me a joke")
        instext = st.text_area("Enter instructions:", "Please be brief")
        submitted = st.form_submit_button("Submit")
        if submitted:
            prompt = ChatPromptTemplate.from_template(template)
            parser = StrOutputParser()
            chain = prompt | llm | parser
            st.info(
                chain.invoke({"question": qtext, "instructions": instext})
            )




try:
    print("loomaai initialized")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    datadir = os.getenv("DATADIR")
    print("datadir: " + datadir)
    LoomaEntry()
except Exception as e:
    st.error(str(e))
