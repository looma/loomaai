import os
import sys
import streamlit as st
#from langchain_community.llms import OpenAI
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.llms import Ollama 
from langchain_core.output_parsers import StrOutputParser

from logzero import logger

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *

st.title("LoomaAI Search")

try:
    cfg = ConfigInit()
    logger.debug("loomaai initialized")
    openai_api_key = cfg.getv("openai_api_key")
    datadir = cfg.getv("datadir")
    if 'openai_api_key' not in st.session_state:
        st.session_state['openai_api_key'] = openai_api_key
    if 'datadir' not in st.session_state:
        st.session_state['datadir'] = datadir
    option = st.selectbox(
        "Select the model",
        ("OpenAI", "llama3"))

    with st.form('my_form'):
        text = st.text_area('Enter text:', 'Please tell me a joke')
        submitted = st.form_submit_button('Submit')
        if not openai_api_key.startswith('sk-'):
            st.warning('Please configure valid OpenAI API key!', icon='⚠')
        if submitted and openai_api_key.startswith('sk-'):
            if option == "OpenAI":
                MODEL="gpt-3.5-turbo"
                parser = StrOutputParser()
                #llm = OpenAI(temperature=0.7, openai_api_key=cfg.getv("openai_api_key"))
                llm = ChatOpenAI(api_key=cfg.getv("openai_api_key"), model=MODEL)
                chain = llm | parser
                st.info(chain.invoke(text))
            elif option == "llama3":
                llm = Ollama(model="llama3:latest")
                st.info(llm.invoke(text))
            else:
                st.write("Unknown Model")
except Exception as e:
    st.error(str(e))
