import io
import os
import re
import traceback

import fitz
import requests
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:47017/")
db = client.get_database("looma")
collection = db.get_collection("chapters")

for chapter in collection.find():
    try:
        groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                            chapter['_id'], re.IGNORECASE)
        grade_level = groups[1]
        subject_ab = groups[2]
        
        nfirstPage = -1
        if 'pn' in chapter:
            if (chapter['npn'] == '' and chapter['pn'] != ''):
                firstPage = chapter['pn'] - 1
                lastPage = chapter['pn'] + chapter['len'] - 2
                fn = 'fn'
            elif (chapter['npn'] != '' and chapter['pn'] != ''):
                firstPage = chapter['pn'] - 1
                lastPage = chapter['pn'] + chapter['len'] - 2
                fn = 'fn'
                nfirstPage = chapter['npn'] - 1
                nlastPage = chapter['npn'] + chapter['nlen'] - 2
                nfn = 'nfn' 
            elif chapter['pn'] == '' and chapter['npn'] != '':
                firstPage = chapter['npn'] - 1
                lastPage = chapter['npn'] + chapter['nlen'] - 2
                fn = 'nfn'  
        elif 'pn' not in chapter:
            firstPage = chapter['npn'] - 1
            lastPage = chapter['npn'] + chapter['nlen'] - 2
            fn = 'nfn' 
        if firstPage == "" or lastPage == "":
            continue
        
        textbook = db.textbooks.find_one({"prefix": grade_level + subject_ab})
        class_level = textbook['class']
        subject = textbook['subject']    
        url = "https://looma.website/content/" + textbook["fp"] + textbook[fn]
        resp = requests.get(url)
        pdf = io.BytesIO(resp.content)
        
        chapter_pdf = fitz.open()
        textbook_pdf = fitz.open(stream=pdf)
        chapter_pdf.insert_pdf(textbook_pdf, from_page=firstPage, to_page=lastPage)
        
        if subject == 'social studies':
            save_loc = f'textbooks/{class_level}/SocialStudies/textbook chapters'
        else:
            save_loc = f'textbooks/{class_level}/{subject}/textbook chapters'
        
        os.makedirs(save_loc, exist_ok=True)
        save_name = f"{chapter['_id']}.pdf"
        save_info = os.path.join(save_loc, save_name)
        chapter_pdf.save(save_info)
        pdf_loc = os.path.abspath(save_loc)
        print(f"{chapter['_id']} from this textbook {url} is a pdf in the folder {pdf_loc}")
        
        if nfirstPage != -1:
            print("has nfirstpage")
            url2 = "https://looma.website/content/" + textbook["fp"] + textbook[nfn]
            resp2 = requests.get(url2)
            pdf2 = io.BytesIO(resp2.content)
            
            nchapter_pdf = fitz.open()
            ntextbook_pdf = fitz.open(stream=pdf2)
            nchapter_pdf.insert_pdf(ntextbook_pdf, from_page=nfirstPage, to_page=nlastPage)
            
            if subject == 'social studies':
                nsave_loc = f'textbooks/{class_level}/SocialStudies/textbook chapters - Nepali'
            else:
                nsave_loc = f'textbooks/{class_level}/{subject}/textbook chapters - Nepali'
                
            os.makedirs(nsave_loc, exist_ok=True)
            nsave_name = f"{chapter['_id']}-Nepali.pdf"
            nsave_info = os.path.join(nsave_loc, nsave_name)
            nchapter_pdf.save(nsave_info)
            npdf_loc = os.path.abspath(nsave_loc)
            print(f"{nsave_name} from this textbook {url} is a pdf in the folder {pdf_loc}")       
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error: {e}")
        print(f"Traceback: {tb}")
