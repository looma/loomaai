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
        grade_level = groups[1]  # grade level
        subject = groups[2]
        
        if 'pn' in chapter:
            if (chapter['npn'] == '' and chapter['pn'] != '') or (chapter['npn'] != '' and chapter['pn'] != ''):
                firstPage = chapter['pn'] - 1
                lastPage = chapter['pn'] + chapter['len'] - 2
                fn = 'fn'
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
        
        textbook = db.textbooks.find_one({"prefix": grade_level + subject})
        url = "https://looma.website/content/" + textbook["fp"] + textbook[fn]
        resp = requests.get(url)
        pdf = io.BytesIO(resp.content)
        
        chapter_pdf = fitz.open()
        textbook_pdf = fitz.open(stream=pdf)
        chapter_pdf.insert_pdf(textbook_pdf, from_page=firstPage, to_page=lastPage)
        
        save_loc = "chapters"
        os.makedirs(save_loc, exist_ok=True)
        save_name = f"{chapter['_id']}.pdf"
        save_info = os.path.join(save_loc, save_name)
        chapter_pdf.save(save_info)
        pdf_loc = os.path.abspath(save_loc)
        print(f"{chapter['_id']} from this textbook {url} is a pdf in the folder {pdf_loc}")
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error: {e}")
        print(f"Traceback: {tb}")