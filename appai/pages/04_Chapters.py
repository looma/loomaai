import streamlit as st

from common.config import ConfigInit

def ChaptersUI(cfg):
    st.title("Chapters")




if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        ChaptersUI(cfg)
    except Exception as e:
        st.error(str(e))
