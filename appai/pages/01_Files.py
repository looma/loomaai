import os
import pathlib
import sys
import time

import pandas as pd
import streamlit as st
import pymupdf4llm
from streamlit.runtime.state import session_state 


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from common.config import *
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

def files_directory(dirname, pattern):
    p = pathlib.Path(dirname)
    all_files = []
    for i in p.rglob(pattern):
        parent = str(i.parent).split("/")[-1]
        name = parent + "/" + i.name
        all_files.append((name, parent, time.ctime(i.stat().st_ctime)))
    return all_files

def files_df(all_files):
    cols = ["File", "Parent", "Created"]
    df = pd.DataFrame.from_records(all_files, columns=cols)
    df["Select"]=False
    return df

def convert_file(file_path):
    file_name = os.path.basename(file_path)
    md_text = pymupdf4llm.to_markdown(file_path)
    #st.markdown(md_text)
    mdpath = file_path + "-mdown"
    if not os.path.exists(mdpath): 
        os.mkdir(mdpath)
    mdfile = os.path.join(mdpath,file_name+".md")
    with open(mdfile, "w") as f:
        f.write(md_text)

def convert_files(basedir, df):
    for f in df["File"]:
        convert_file(basedir + "/" + f)
        st.write("Converted ", f)

def delete_files(basedir, df):
    for f in df["File"]:
        os.remove(basedir + "/" + f)
        st.write(" Deleted : ", f)

def FilesUI(basedir):
    dirname = basedir + "/" + "files"
    col1, col2 = st.columns(2)
    with col1:
        ctr1 = st.container()
        pdf_files = ctr1.file_uploader('Choose your PDF', type="pdf", accept_multiple_files=True)
        if pdf_files is not None:
            for file in pdf_files:
                ctr1.write(file)
                bytes_data = file.read()
                filename = dirname + "/" + file.name
                with open(filename, "wb") as f:
                    f.write(bytes_data)
    with col2:
        ctr2 = st.container()
        url = ctr2.text_input("Enter Document URL", value="")
        getdoc = ctr2.button("Get Docs")
        if getdoc:
            p = GetDocument(url)
            st.session_state[dirname].append(p)
        url = ctr2.text_input("Enter News Article URL", value="")
        getarticle = ctr2.button("Get Article")
        if getarticle:
            p = GetArticle(url)
            st.session_state[dirname].append(p)
    option = st.selectbox(
        "Select the type of content",
        ("PDFs", "News Articles", "Documents", "Markdowns"))

    match option:
        case "PDFs":
            st.write("Files: " + dirname)
            all_files = files_directory(dirname, '*.pdf')
            st.session_state[dirname] = all_files
            df = files_df(st.session_state[dirname])
            edited_df = st.data_editor(
                            df,
                            key="file_selector",
                            column_config={
                                "Select": st.column_config.CheckboxColumn(),
                            },
                            use_container_width=True,
                        )
            if len(edited_df[edited_df["Select"]]) > 0:
                st.write("Selected Files:")
                st.dataframe(edited_df[edited_df["Select"]])
                action = st.selectbox("Action: ", ("Convert", "Delete"))
                if action == "Convert":
                    cbutton = st.button("Convert")
                    if cbutton:
                        convert_files(basedir, edited_df[edited_df["Select"]])
                if action == "Delete":
                    dbutton = st.button("Delete")
                    if dbutton:
                        delete_files(basedir, edited_df[edited_df["Select"]])

        case "News Articles":
            # TODO
            st.write("News Articles")
        case "Documents":
            # TODO
            st.write("Documents")
        case "Markdowns":
            st.write("Markdowns")
            all_files = files_directory(dirname, '*-mdown')
            st.session_state[dirname] = all_files
            df = files_df(st.session_state[dirname])
            edited_df = st.data_editor(
                            df,
                            key="file_selector",
                            column_config={
                                "Select": st.column_config.CheckboxColumn(),
                            },
                            use_container_width=True,
            )
        case _:
            st.write("Unknown")

try:
    cfg = ConfigInit()
    if 'datadir' not in st.session_state:
        st.session_state['datadir'] = cfg.getv("datadir")
    FilesUI(st.session_state['datadir'])
except Exception as e:
    st.error(str(e))
