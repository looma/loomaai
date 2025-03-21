# Commented out file because of dependency on langchain_community
# import hashlib
# import json
# import os
# import time
# from typing import Iterable
# from urllib.request import urlretrieve
#
# from langchain.chains import (LLMChain, MapReduceDocumentsChain,
#                               ReduceDocumentsChain, StuffDocumentsChain)
# from langchain_community.document_loaders import NewsURLLoader
# from langchain_community.llms import CTransformers
# from langchain.prompts import PromptTemplate
# from langchain.schema import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import WebBaseLoader
# from logzero import logger
#
#
# class DocumentFetcher:
#     def __init__(self, url, type):
#         self.url = url
#         self.type = type
#     def GetFilename(self):
#         hv = hashlib.sha256(self.url.encode()).hexdigest()
#         iname = self.url.split('/')[2]
#         filename = iname + "." + hv[:6]
#         return filename
#     def SaveDocs(self, filename, array: Iterable[Document]):
#         with open(filename, 'w') as f:
#             for doc in array:
#                 f.write(doc.json() + '\n')
#         return filename
#     def LoadDocs(self, filename)->Iterable[Document]:
#         array = []
#         with open(filename, 'r') as f:
#             for line in f:
#                 data = json.loads(line)
#                 obj = Document(**data)
#                 array.append(obj)
#         return array
#     def Fetch(self):
#         if self.type == "doc":
#             filename = self.GetFilename()
#             path, headers = urlretrieve(self.url, filename)
#             logger.info("Saved: ", path)
#         elif self.type == "news":
#             filename = self.GetFilename()
#             loader = NewsURLLoader([self.url])
#             docs = loader.load()
#             # TODO:
#             path = self.SaveDocs(filename, docs)
#             logger.info("Saved: ", path)
#         else:
#             logger.error("Unknown type: ", self.type)
#     def FetchLinks(self, urllist):
#         filename = "links"
#         loader = WebBaseLoader(urllist)
#         docs = loader.load()
#         path = self.SaveDocs(filename, docs)
#         logger.info("Saved: ", path)
#
#
# def GetDocument(url):
#     doc = DocumentFetcher(url, "doc")
#     path = doc.Fetch()
#     return path
#
# def GetArticle(url):
#     doc = DocumentFetcher(url, "news")
#     path = doc.Fetch()
#     return path
#
# def get_article(article_url):
#     # Load article
#     loader = NewsURLLoader([article_url])
#     docs = loader.load()
#     return docs
#
# # TODO
# def summarize_files(project, filelist):
#     logger.debug(project.Name())
#     for f in filelist:
#         logger.debug(f)
#
# def summarize_article(article_url):
#     # Load article
#     loader = NewsURLLoader([article_url])
#     docs = loader.load()
#
#     # Load LLM
#     config = {'max_new_tokens': 4096, 'temperature': 0.7, 'context_length': 4096}
#     llm = CTransformers(model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
#                         model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
#                         config=config,
#                         threads=os.cpu_count())
#
#     # Map template and chain
#     map_template = """<s>[INST] The following is a part of an article:
#     {docs}
#     Based on this, please identify the main points.
#     Answer:  [/INST] </s>"""
#     map_prompt = PromptTemplate.from_template(map_template)
#     map_chain = LLMChain(llm=llm, prompt=map_prompt)
#
#     # Reduce template and chain
#     reduce_template = """<s>[INST] The following is set of summaries from the article:
#     {doc_summaries}
#     Take these and distill it into a final, consolidated summary of the main points.
#     Construct it as a well organized summary of the main points and should be between 3 and 5 paragraphs.
#     Answer:  [/INST] </s>"""
#     reduce_prompt = PromptTemplate.from_template(reduce_template)
#     reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
#
#     # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
#     combine_documents_chain = StuffDocumentsChain(
#         llm_chain=reduce_chain, document_variable_name="doc_summaries"
#     )
#
#     # Combines and iteratively reduces the mapped documents
#     reduce_documents_chain = ReduceDocumentsChain(
#         # This is final chain that is called.
#         combine_documents_chain=combine_documents_chain,
#         # If documents exceed context for `StuffDocumentsChain`
#         collapse_documents_chain=combine_documents_chain,
#         # The maximum number of tokens to group documents into.
#         token_max=4000,
#     )
#
#
#     # Combining documents by mapping a chain over them, then combining results
#     map_reduce_chain = MapReduceDocumentsChain(
#         # Map chain
#         llm_chain=map_chain,
#         # Reduce chain
#         reduce_documents_chain=reduce_documents_chain,
#         # The variable name in the llm_chain to put the documents in
#         document_variable_name="docs",
#         # Return the results of the map steps in the output
#         return_intermediate_steps=True,
#     )
#
#
#     # Split documents into chunks
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=4000, chunk_overlap=0
#     )
#     split_docs = text_splitter.split_documents(docs)
#
#
#     # Run the chain
#     start_time = time.time()
#     result = map_reduce_chain.__call__(split_docs, return_only_outputs=True)
#     time_taken = time.time() - start_time
#     return result['output_text'], time_taken
