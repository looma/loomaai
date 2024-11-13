import io
import os
import re
import fitz
import requests
from pymongo import MongoClient

#function takes in the variable connecting to MongoDB and the location of where the pdfs are supposed to go
def split(client: MongoClient, files_dir: str, textbooks: str): 
    #navigates to the chapter collection in the looma database
    db = client.get_database("looma")
    collection = db.get_collection("chapters")
    
    #filters depending on the textbooks parameter
    if textbooks == 'all':
        data = collection.find()
    else:
        prefix = re.compile(fr"^{textbooks}\d", re.IGNORECASE)
        data = collection.find({"_id": prefix})
        
    #iterates through all the chapters
    for chapter in data:
        try:
            #determines whether to use the pn and len fields, npn and nlen fields, or both
            nfirstPage = -1
            if 'pn' in chapter:
                if (chapter['npn'] == '' and chapter['pn'] != ''):
                    firstPage = chapter['pn'] - 1
                    lastPage = chapter['pn'] + chapter['len'] - 2
                    fn = 'fn'
                    lang1 = 'en'
                elif (chapter['npn'] != '' and chapter['pn'] != ''):
                    firstPage = chapter['pn'] - 1
                    lastPage = chapter['pn'] + chapter['len'] - 2
                    fn = 'fn'
                    lang1 = 'en'
                    nfirstPage = chapter['npn'] - 1
                    nlastPage = chapter['npn'] + chapter['nlen'] - 2
                    nfn = 'nfn'
                    lang2 = 'np'
                elif chapter['pn'] == '' and chapter['npn'] != '':
                    firstPage = chapter['npn'] - 1
                    lastPage = chapter['npn'] + chapter['nlen'] - 2
                    fn = 'nfn'
                    lang1 = 'np'
            elif 'pn' not in chapter:
                firstPage = chapter['npn'] - 1
                lastPage = chapter['npn'] + chapter['nlen'] - 2
                fn = 'nfn'
                lang1 = 'en'
            if firstPage == "" or lastPage == "":
                continue
            
            #searches the grade and subject of the textbook within the _id field to access the textbook through the prefix field for the textbook data
            groups = re.search(r"([1-9]|10|11|12)(EN|S|SF|M|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                                chapter['_id'], re.IGNORECASE)
            grade = groups[1]
            subject = groups[2]
            
            #finds the textbook the chapter is associated with, uses the textbook data to find the link to the textbook in looma website    
            textbook = db.textbooks.find_one({"prefix": grade + subject})
            if textbook is None:
                print(f"Textbook not found: {grade + subject}")
                continue
            url = "https://looma.website/content/" + textbook["fp"] + textbook[fn]
            
            #makes a request for the content of the textbook, converts it to bytes, and create the textbook pdf using the bytes
            resp = requests.get(url)
            pdf = io.BytesIO(resp.content)
            textbook_pdf = fitz.open(stream=pdf)
            
            #creates the chapter pdf and takes the chapter pages from the textbook pdf and inserts them into the new chapter pdf
            chapter_pdf = fitz.open()
            chapter_pdf.insert_pdf(textbook_pdf, from_page=firstPage, to_page=lastPage)

            #creates a variable with the save location and saves the pdf into that location
            save_loc = f'{files_dir}/{textbook["fp"]}{lang1}'
            os.makedirs(save_loc, exist_ok=True)
            save_name = f"{chapter['_id']}.pdf"
            save_info = os.path.join(save_loc, save_name)
            chapter_pdf.save(save_info)

            #if there is a English and Nepali version of the textbook, the code below does the process of creating the url, making the pdf, and saving it with the Nepali textbook data
            if nfirstPage != -1:
                url2 = "https://looma.website/content/" + textbook["fp"] + textbook[nfn]
                resp2 = requests.get(url2)
                pdf2 = io.BytesIO(resp2.content)
                ntextbook_pdf = fitz.open(stream=pdf2)

                nchapter_pdf = fitz.open()
                nchapter_pdf.insert_pdf(ntextbook_pdf, from_page=nfirstPage, to_page=nlastPage)

                nsave_loc = f'{files_dir}/{textbook["fp"]}{lang2}'
                os.makedirs(nsave_loc, exist_ok=True)
                nsave_name = f"{chapter['_id']}-nepali.pdf"
                nsave_info = os.path.join(nsave_loc, nsave_name)
                nchapter_pdf.save(nsave_info)
        except Exception as e:
            print(f"Error: {e}")