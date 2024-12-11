import streamlit as st
import os
from common.config import ConfigInit
from common.vectordb import VectorDB
from logzero import logging
from cProfile import label
from typing import Collection

st.set_page_config(page_title="Settings", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
st.title("⚙️ Settings")

def CollectionsUI(cfg):
    config = cfg.json()
    vurl = f'http://{config["qdrant"]["host"]}:{config["qdrant"]["port"]}'
    vdb = VectorDB(vurl)

    list_ctr = st.container()
    list_ctr.dataframe(vdb.collections_df(),
                        column_config={
                            "Collection": st.column_config.TextColumn(),
                            "Status": st.column_config.TextColumn(),
                        },
                        use_container_width=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Create Collection")
        create_ctr = st.container()
        col_name = create_ctr.text_input("Collection Name")
        if create_ctr.button("Create"):
            vdb.create_collection(col_name)
            st.success(f"Collection {col_name} created successfully")
    with col2:
        st.subheader("Delete Collection")
        delete_ctr = st.container()
        all = st.checkbox("Select all")
        if all:
            selected_collections = delete_ctr.multiselect("Select one or more collections:",
            vdb.collections(),vdb.collections())
        else:
            selected_collections =  delete_ctr.multiselect("Select one or more collections:",
                vdb.collections())
        if delete_ctr.button("Delete"):
            for col_name in selected_collections:
                vdb.delete_collection(col_name)
                st.success(f"Collection {col_name} deleted successfully")
    return

def SettingsUI(cfg):
    config = cfg.json()
    col1, col2 = st.columns(2)
    with col1:
        setctr1 = st.container()
        config["name"] = setctr1.text_input("Name", value=config["name"])

    with col2:
        setctr2 = st.container()
        config["datadir"] = setctr2.text_input("Data Directory", value=config["datadir"])

    st.subheader("Qdrant Configuration")
    config["qdrant"]["host"] = st.text_input("Qdrant Host", value=config["qdrant"]["host"])
    config["qdrant"]["port"] = st.number_input("Qdrant Port", value=config["qdrant"]["port"], step=1)
    config["qdrant"]["index"] = st.text_input("Qdrant Index", value=config["qdrant"]["index"])

    dashboard = st.checkbox ("Qdrant Dashboard")
    if dashboard:
        dashboard_ctr = st.container()
        dashboard_ctr.text("Qdrant Dashboard")
        url = dashboard_ctr.text_input("URL", value=f'http://{config["qdrant"]["host"]}:{config["qdrant"]["port"]}/dashboard')
        st.link_button(
                url=url,
                label='Qdrant Dashboard'
        )
    collection_mgmt = st.checkbox("Manage Collections")
    if collection_mgmt:
        CollectionsUI(cfg)


if __name__ == "__main__":
    try:
        cfg = ConfigInit()
        SettingsUI(cfg)
    except Exception as e:
        st.error(str(e))
        logging.error(str(e))
