import streamlit as st

from common.config import ConfigInit
from logzero import logger
st.title("LoomaAI")

try:
    cfg = ConfigInit()
    logger.debug("loomaai initialized")
    openai_api_key = cfg.getv("openai_api_key")
    datadir = cfg.getv("datadir")
    logger.debug("datadir: " + datadir)
except Exception as e:
    st.error(str(e))
