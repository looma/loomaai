import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.llms import Ollama 
from langchain_core.output_parsers import StrOutputParser
from common.config import *

st.title("LoomaAI")

try:
    cfg = ConfigInit()
    logger.debug("loomaai initialized")
    openai_api_key = cfg.getv("openai_api_key")
    datadir = cfg.getv("datadir")
    logger.debug("datadir: " + datadir)
except Exception as e:
    st.error(str(e))
