import os
import yaml

import streamlit as st
from common.llmselect import LLMSelect, LLMInfo

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def get_llm_services():
    docker_compose_path = "/app/docker-compose.yml"
    if os.path.exists(docker_compose_path):
        compose_path = docker_compose_path
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        compose_path = os.path.abspath(os.path.join(current_dir, "..", "docker-compose.yml"))
    print("Resolved docker-compose.yml path:", compose_path)
    if not os.path.exists(compose_path):
        raise FileNotFoundError(f"docker-compose.yml not found at {compose_path}")
    with open(compose_path, "r") as f:
        compose = yaml.safe_load(f)
    llm_providers = []
    for service in compose.get("services", {}).values():
        env = service.get("environment", [])
        for e in env:
            if "LLM_PREFERRED" in str(e):
                provider = str(e).split("=")[-1].strip()
                if provider and provider not in llm_providers:
                    llm_providers.append(provider)
    return llm_providers

st.title("LoomaAI")

def LoomaEntry():
    providers = LLMInfo().modellist.keys()
    selected_llm = st.selectbox("Select LLM Provider:", list(providers), index=0)
    models = LLMInfo().get_model_list(selected_llm)
    selected_model = st.selectbox("Select Model:", models, index=0)
    llm_selector = LLMSelect(selected_llm, selected_model)
    llm = llm_selector.llm()
    llm_name, llm_model = llm_selector.llm_namemodel()
    template = """Question: {question}
    Instructions: {instructions}"""
    with st.form("my_form"):
        qtext = st.text_area("Enter question:", "Please tell me about Mt. Annapurna")
        instext = st.text_area("Enter instructions:", "Please be brief")
        submitted = st.form_submit_button("Submit")
        if submitted:
            prompt = ChatPromptTemplate.from_template(template)
            parser = StrOutputParser()
            chain = prompt | llm | parser
            try:
                st.info(
                    chain.invoke({"question": qtext, "instructions": instext})
                )
            except Exception as e:
                st.write(e)

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    datadir = os.getenv("DATADIR")
    LoomaEntry()
except Exception as e:
    st.error(str(e))
