import streamlit as st # type: ignore
from streamlit_js_eval import streamlit_js_eval
import pymupdf4llm
from common.config import *
from common.files import *
from logzero import logger


st.set_page_config(page_title="Files & Content", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
st.title("📂 Files & Content")
mod_page_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(mod_page_style, unsafe_allow_html=True)


def FilesBrowse(dirc):
    df = dirc.df(dirc.files("*"))
    df.drop(columns=["Parent"], inplace=True)
    df["Select"] = False
    st.session_state[dirc.dirname] = df
    edited_df = st.data_editor(
                    df,
                    key="file_selector",
                    hide_index=True,
                    column_config={
                        "Select": st.column_config.CheckboxColumn(),
                        "Type": st.column_config.TextColumn(),
                    },
                    use_container_width=True,
    )
    return edited_df

def FileVectorize(cfg, fname):
    st.write("Vectorizing file: ", fname)
    return

def FileActions(cfg, dirc, edited_df):
    col1, col2 = st.columns(2)
    with col1:
        actctr1 = st.container()
        actctr1.dataframe(edited_df[edited_df["Select"]], use_container_width=True)
    with col2:
        actctr2 = st.container()
        action = actctr2.selectbox("Actions", ("Convert", "Delete", "Show", "Vectorize"))
    match action:
        case "Convert":
            cbutton = actctr2.button("Convert")
            if cbutton:
                dirc.convert_files(edited_df[edited_df["Select"]])
                st.toast("Files converted!", icon="ℹ️")
                streamlit_js_eval(js_expressions="parent.window.location.reload()")
        case "Delete":
            dbutton = actctr2.button("Delete")
            if dbutton:
                dirc.delete_files(edited_df[edited_df["Select"]])
                st.toast("Filed deleted!", icon="ℹ️")
                streamlit_js_eval(js_expressions="parent.window.location.reload()")
        case "Show":
            sbutton = actctr2.button("Show")
            if sbutton:
                f = edited_df[edited_df["Select"]].iloc[0]["File"]
                fname = dirc.fullpath(f)
                st.write("Showing file: ", fname)
                # TODO: based on the file type pick up a different one
                md_text = pymupdf4llm.to_markdown(fname)
                st.markdown(md_text)
        case "Vectorize":
            sbutton = actctr2.button("Vectorize")
            if sbutton:
                f = edited_df[edited_df["Select"]].iloc[0]["File"]
                fname = dirc.fullpath(f)
                FileVectorize(cfg, fname)

def FilesUI(cfg):
    dirc = Directory(cfg.getv("datadir"))
    ctr1 = st.container()
    up_files = ctr1.file_uploader('Choose your files', accept_multiple_files=True, key="file_uploader")
    if up_files is not None:
        for file in up_files:
            ctr1.write(file)
            bytes_data = file.read()
            filename = dirc.dirname + "/" + file.name
            with open(filename, "wb") as f:
                f.write(bytes_data)
    edited_df = FilesBrowse(dirc)
    if len(edited_df[edited_df["Select"]]) > 0:
        FileActions(cfg, dirc, edited_df)


if __name__ == "__main__":
    try:
        cfg = ConfigInit()
        FilesUI(cfg)
    except Exception as e:
        st.error(str(e))
        logger.error(str(e))
