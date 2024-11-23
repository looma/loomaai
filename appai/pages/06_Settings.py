import streamlit as st
import json
import os
from common.config import *
from common.vectordb import VectorDB
from logzero import logging

st.set_page_config(page_title="Settings", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
st.title("⚙️ Settings")

def SettingsUI(cfg):
    config = cfg.json()
    col1, col2 = st.columns(2)
    with col1:
        setctr1 = st.container()
        config["name"] = st.text_input("Name", value=config["name"])
        
    with col2:
        setctr2 = st.container()
        config["datadir"] = st.text_input("Data Directory", value=config["datadir"])

    st.subheader("Qdrant Configuration")
    config["qdrant"]["host"] = st.text_input("Qdrant Host", value=config["qdrant"]["host"])
    config["qdrant"]["port"] = st.number_input("Qdrant Port", value=config["qdrant"]["port"], step=1)
    config["qdrant"]["index"] = st.text_input("Qdrant Index", value=config["qdrant"]["index"])

    st.link_button(
            url=f'http://{config["qdrant"]["host"]}:{config["qdrant"]["port"]}/dashboard',
            label=f'Qdrant Dashboard'
    )

if __name__ == "__main__":
    try:
        cfg = ConfigInit()
        SettingsUI(cfg)
    except Exception as e:
        st.error(str(e))
        logging.error(str(e))

