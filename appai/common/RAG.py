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

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class gen: 
    def __init__(self):
        self.llm = ChatOllama(model="phi3")
        self.prompt = PromptTemplate.from_template("Question: {question} \n Context: {context}")
        self.textSplitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 20)

    def makeChain(self, pdfPath):
        pdf = PyMuPDFLoader(pdfPath).load()
        chunks = self.textSplitter.split_documents(pdf)
        
        # FastEmbed embeddings
        #embedding_func = FastEmbedEmbeddings() #OllamaEmbeddings(model="llama3")

        # Hugging Face Embeddings
        
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {}
        encode_kwargs = {'normalize_embeddings': False}
        embedding_func = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs)
           


        # Chroma vector store
        #vectorStore = Chroma.from_documents(chunks, embedding=embedding_func)

        # Faiss vector store
        vectorStore = FAISS.load_local("../../loomadata/vector_db", embedding_func, allow_dangerous_deserialization=True)

        self.retriever = vectorStore.as_retriever(search_type = "similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.1,})

        self.chain = {"context" : self.retriever , "question" : RunnablePassthrough()} | self.prompt | self.llm | StrOutputParser() 


    def ask(self, query: str): 
        return self.chain.invoke(query)


#""" Test Code 
test = gen()
test.makeChain("/Users/connorlee/Documents/GitHub/loomaai/appai/textbooks/Class10/Math/textbook_chapters/10M01.pdf")
print(test.ask("Can you give me a summary in 50 words"))
#"""