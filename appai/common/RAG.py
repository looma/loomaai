from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough



class gen: 
    def __init__(self):
        self.llm = ChatOllama(model="phi3")
        self.prompt = PromptTemplate.from_template("Question: {question} \n Context: {context}")
        self.textSplitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 20)

    def loadPDF(self, pdfPath):
        pdf = PyMuPDFLoader(pdfPath).load()
        chunks = self.textSplitter.split_documents(pdf)
        embedding_func = OllamaEmbeddings(model="llama3")
        vectorStore = Chroma.from_documents(chunks, embedding=embedding_func)
        self.retriever = vectorStore.as_retriever(search_type = "similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.2,})

        self.chain = {"context" : self.retriever , "question" : RunnablePassthrough()} | self.prompt | self.llm | StrOutputParser() 

    def ask(self, query: str): 
        return self.chain.invoke(query)


""" Test Code 
test = gen()
test.clear()
test.loadPDF("./Addition.pdf")
print(test.ask("What are the types of numbers in math 50 words"))
"""