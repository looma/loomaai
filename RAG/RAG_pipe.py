from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.llms import HuggingFacePipeline




class gen: 
    def __init__(self):
        self.llm = ChatOllama(model="phi3")
        self.prompt = PromptTemplate.from_template("Question: {question} \n Context: {context}")
        self.textSplitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 20)

    def get_embeddings(docs_after_split):
        huggingface_embeddings = HuggingFaceBgeEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",  # alternatively use "sentence-transformers/all-MiniLM-l6-v2" for a light and faster experience.
            model_kwargs={'device':'cpu'}, 
            encode_kwargs={'normalize_embeddings': True}
        )
        sample_embedding = np.array(huggingface_embeddings.embed_query(docs_after_split[0].page_content))
        #print("Sample embedding of a document chunk: ", sample_embedding)
        #print("Size of the embedding: ", sample_embedding.shape)
        return huggingface_embeddings


    def loadPDF(self, pdfPath):
        pdf = PyPDFLoader(pdfPath).load()
        chunks = self.textSplitter.split_documents(pdf)
        embedding_func = OllamaEmbeddings(model="llama3")
        vectorStore = Chroma.from_documents(chunks, embedding=embedding_func)
        self.retriever = vectorStore.as_retriever(search_type = "similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.2,})

        self.chain = {"context" : self.retriever , "question" : RunnablePassthrough()} | self.prompt | self.llm | StrOutputParser() 

    def ask(self, query: str): 
        return self.chain.invoke(query)


#""" Test Code 
test = gen()
test.loadPDF("/Users/connorlee/Documents/loomaProgramsML/Looma24/Addition.pdf")
print(test.ask("What are the types of numbers in math 50 words"))
#"""