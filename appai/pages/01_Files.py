import streamlit as st

from common.config import *
from common.files import *
from common.utils import *


st.set_page_config(page_title="Files & Content", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
mod_page_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(mod_page_style, unsafe_allow_html=True)


def FilesUI(basedir):
    dirc = Directory(basedir)
    ctr1 = st.container()
    up_files = ctr1.file_uploader('Choose your files', type="pdf", accept_multiple_files=True)
    if up_files is not None:
        for file in up_files:
            ctr1.write(file)
            bytes_data = file.read()
            filename = dirc.dirname + "/" + file.name
            with open(filename, "wb") as f:
                f.write(bytes_data)
    all_files = dirc.files("*")
    st.session_state[dirc.dirname] = all_files
    df = dirc.df(st.session_state[dirc.dirname])
    edited_df = st.data_editor(
                    df,
                    key="file_selector",
                    column_config={
                        "Select": st.column_config.CheckboxColumn(),
                    },
                    use_container_width=True,
    )
    if len(edited_df[edited_df["Select"]]) > 0:
        col1, col2 = st.columns(2)
        with col1:
            actctr1 = st.container()
            #actctr1.write("Selected Files:")
            actctr1.dataframe(edited_df[edited_df["Select"]])
        with col2:
            actctr2 = st.container()
            accol1, accol2 = actctr2.columns(2)
            with accol1:
                actctr2.markdown(
                    """
                    <style>
                    [data-baseweb="select"] {
                        margin-top: -50px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                action = actctr2.selectbox("", ("Convert", "Delete"))
            with accol2:
                if action == "Convert":
                    cbutton = actctr2.button("Convert")
                    if cbutton:
                        dirc.convert_files(edited_df[edited_df["Select"]])
                if action == "Delete":
                    dbutton = actctr2.button("Delete")
                    if dbutton:
                        dirc.delete_files(edited_df[edited_df["Select"]])
    # TODO
    col1, col2 = st.columns(2)
    with col1:
        ctr1 = st.container()
        url = ctr1.text_input("Enter Document URL", value="")
        getdoc = ctr1.button("Get Docs")
        if getdoc:
            p = GetDocument(url)
            st.session_state[dirc.dirname].append(p)
    with col2:
        ctr2 = st.container()
        url = ctr2.text_input("Enter News Article URL", value="")
        getarticle = ctr2.button("Get Article")
        if getarticle:
            p = GetArticle(url)
            st.session_state[dirc.dirname].append(p)



try:
    cfg = ConfigInit()
    if 'datadir' not in st.session_state:
        st.session_state['datadir'] = cfg.getv("datadir")
    FilesUI(st.session_state['datadir'])
except Exception as e:
    st.error(str(e))
