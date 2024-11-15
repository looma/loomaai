import streamlit as st

from common.config import ConfigInit

def TextbookUI(cfg):
    st.title('Textbook')





if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        TextbookUI(cfg)
    except Exception as e:
        st.error(str(e))
    
