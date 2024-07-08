import os
import sys

import streamlit as st
from logzero import logger
from langchain_community.llms import OpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.config import *

st.title('Quick Sample App')

#openai_api_key = st.sidebar.text_input('OpenAI API Key')
#openai_api_key="sk-57Edk7h1xmWxFZhtKVfSiT3BlbkFJESSvjicmFy2KkxSVDNO8"

try:
    cfg = ConfigInit()
    logger.debug("loomaai initialized")
    openai_api_key = cfg.getv("openai_api_key")
    datadir = cfg.getv("datadir")
    if 'openai_api_key' not in st.session_state:
        st.session_state['openai_api_key'] = openai_api_key
    if 'datadir' not in st.session_state:
        st.session_state['datadir'] = datadir
    with st.form('my_form'):
        text = st.text_area('Enter text:', 'What are most well known mountains in Nepal ?')
        submitted = st.form_submit_button('Submit')
        if not openai_api_key.startswith('sk-'):
            st.warning('Please configure valid OpenAI API key!', icon='⚠')
        if submitted and openai_api_key.startswith('sk-'):
            llm = OpenAI(temperature=0.7, openai_api_key=cfg.getv("openai_api_key"))
            st.info(llm(text))
except Exception as e:
    st.error(str(e))
