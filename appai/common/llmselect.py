import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama, OllamaLLM

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

class LLMInfo:
    def __init__(self):
        """
        Initialize the LLMInfo class with a dictionary of available models
        for different LLM providers.
        """
        self.modellist = {
            "OpenAI": ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o", "gpt-4.1"],
            "Google": ["gemini-2.0-flash", "gemini-2.5-flash-preview-05-20"],
            "Ollama": ["mistral", "llama3.2:3b", "deepseek-r1:8b"],
        }
        self.default_model = {
            "OpenAI": "gpt-4.1-mini",
            "Google": "gemini-2.0-flash",
            "Ollama": "mistral",
        }

    def get_model_list(self, provider):
        """
        Get the list of models for a specific LLM provider.

        :param provider: The name of the LLM provider (e.g., "OpenAI", "Google").
        :return: A list of model names for the specified provider.
        """
        return self.modellist.get(provider, [])

    def get_providers(self):
        """
        Get the list of available LLM providers.
        :return: A list of LLM provider names.
        """
        return list(self.modellist.keys())

    def get_default_model(self, provider):
        """
        Get the default model for a specific LLM provider.
        :param provider: The name of the LLM provider (e.g., "OpenAI", "Google").
        :return: The default model name for the specified provider.
        """
        return self.default_model.get(provider, None)


class LLMSelect:
    def __init__(self):
        self.llm_list = LLMInfo().get_providers()
        self.selected_llm = None

    def llm(self):
        llm = self.select_llm(temperature=0.0)
        return llm

    def llm_namemodel(self):
        llm_preferred = os.getenv("LLM_PREFERRED")
        if llm_preferred not in self.llm_list:
            raise ValueError(
                f"LLM {llm_preferred} is not in the list of available LLMs: {self.llm_list}"
            )
        llm_model = os.getenv("LLM_MODEL")
        if llm_model is None:
            llm_model = LLMInfo().get_default_model(llm_preferred)
        return llm_preferred,llm_model

    def select_llm(self, temperature=0.0):
        llm_preferred = os.getenv("LLM_PREFERRED")
        llm_model = os.getenv("LLM_MODEL")
        print(f"LLM_PREFERRED: {llm_preferred}, LLM_MODEL: {llm_model}")
        if llm_preferred not in self.llm_list:
            raise ValueError(
                f"LLM {llm_preferred} is not in the list of available LLMs: {self.llm_list}"
            )
        if llm_model is None:
            llm_model = LLMInfo().get_default_model(llm_preferred)

        # let's check keys
        if llm_preferred == "OpenAI":
            if "OPENAI_API_KEY" not in os.environ:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
        elif llm_preferred == "GoogleGemini":
            if "GOOGLE_API_KEY" not in os.environ:
                raise ValueError("GOOGLE_API_KEY environment variable is not set.")
        elif llm_preferred == "Ollama":
            if "OLLAMA_URL" not in os.environ:
                raise ValueError("OLLAMA_URL environment variable is not set.")
        else:
            print("Using ", llm_preferred, " and ", llm_model, " as model.")

        match llm_preferred:
            case "OpenAI":
                from langchain_openai import ChatOpenAI

                openai_api_key = os.getenv("OPENAI_API_KEY")
                self.selected_llm = ChatOpenAI(
                    model_name=llm_model,
                    api_key=openai_api_key,
                )
            case "GoogleGemini":
                from langchain_google_gemini import ChatGoogleGemini

                google_api_key = os.getenv("GOOGLE_API_KEY")
                self.selected_llm = ChatGoogleGemini(
                    model_name=llm_model,
                    api_key=google_api_key,
                )
            case "Ollama":
                from langchain_ollama import ChatOllama
                ollama_url = os.getenv("OLLAMA_URL")
                '''
                self.selected_llm = ChatOllama(
                    model_name=llm_model,
                    base_url=ollama_url,
                    temperature=0,
                    num_ctx=32000,
                    num_predict=2048
                )
                '''
                self.selected_llm = OllamaLLM(
                    model=llm_model,
                    base_url=ollama_url,
                    format='',
                    verbose=True
                )
            case _:
                raise ValueError(
                    f"LLM {llm_preferred} is not supported. Please choose from {self.llm_list}"
                )
        return self.selected_llm
