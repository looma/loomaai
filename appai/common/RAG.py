import os
import sys
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
#from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from common.config import *
from langchain_openai import ChatOpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class gen: 
    def __init__(self):
        """
        Initializes model, tokenizer
        - Gets API key from config.py 
        - Initializes model 
        - Creates prompt template 
            - Question, Context where question is the user's query and context is the relevant documents for the RAG
        - Creates document chunker 
            - chunk_size: number of words in each document chunk
            - chunk_overlap: number of words shared between each chunk in order to maintain context 
        """
        cfg = ConfigInit()
        openai_api_key = cfg.getv("openai_api_key")

        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=openai_api_key) # Intializes model
        #self.llm = ChatOllama(model="llama3")

        # Creates prompt template in the form of Question, Context where question is the user's query and context is the relevant documents for the RAG
        self.prompt = PromptTemplate.from_template("Question: {question} \n Context: {context}") # Prompt template 

        # Creates document chunker
        self.textSplitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 20) # Splits text

    def makeChain(self, pdfPath):
        """
        Makes chain
        - Creates pdf loader
            - Takes in pdfPath which is path to file
        - Chunks text
            - Chunks the loaded pdf 
        - Embedding function
            - FastEmbed embeddings
                - Fast, python lightweight embeddings
            - HuggingFace embeddings
                - Hugging face sentence-transformers/all-mpnet-base-v2
        - Vector store
            - Chroma
                - Can be used standalone 
            - FAISS
                - Depends on vector_db which is generated from generate.py
        - Retriever
            - Searches vector store by similary-search and takes in top 3 documents
        - Chain
            - Chains together the context, which is retrieved from the retriever, query, llm
        """
        pdf = PyMuPDFLoader(pdfPath).load() # Loads pdf
        chunks = self.textSplitter.split_documents(pdf) # Splits pdf
        
        # FastEmbed embeddings
        embedding_func = FastEmbedEmbeddings() #OllamaEmbeddings(model="llama3")

        # Hugging Face Embeddings
        
        '''
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {}
        encode_kwargs = {'normalize_embeddings': False}
        embedding_func = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs)
        '''
           

        # Chroma vector store
        vectorStore = Chroma.from_documents(chunks, embedding=embedding_func)

        # Faiss vector store
        '''
        path = "../../loomadata/vector_db"
        path = "/app/data/vector_db"
        #vectorStore = FAISS.load_local(path, embedding_func, allow_dangerous_deserialization=True)
        '''

        self.retriever = vectorStore.as_retriever(search_type = "similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.1,}) # Retriever for k = 3 top documents 

        self.chain = {"context" : self.retriever , "question" : RunnablePassthrough()} | self.prompt | self.llm | StrOutputParser()  # Initalizes chain


    def ask(self, query: str): 
        """
        Queries the chain and returns the output from the chain
        """
        return self.chain.invoke(query) # Returns output from chain with parameter user query 
