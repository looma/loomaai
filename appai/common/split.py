import io
import os
import re
import fitz
import requests
from pymongo import MongoClient


# function takes in the variable connecting to MongoDB and the location of where the pdfs are supposed to go
def split(client: MongoClient, files_dir: str, prefixes: list[str] | str):
    db = client.get_database("looma")
    collection = db.get_collection("chapters")

    for prefix in prefixes:


        # searches the grade and subject of the textbook within the _id field to access the textbook through the prefix field for the textbook data
        groups = re.search(r"([1-9]|10|11|12)(EN|SF|SS|S|M|N|H|V|CS)",
                           prefix, re.IGNORECASE)
        grade = groups[1]
        subject = groups[2]

        # finds the textbook the chapter is associated with, uses the textbook data to find the link to the textbook in looma website
        textbook = db.textbooks.find_one({"prefix": grade + subject})
        if textbook is None:
            print(f"Textbook not found: {grade + subject}")
            continue

        fn = textbook['fn']
        textbook_pdf = None
        if fn != '':
            url = "https://looma.website/content/" + textbook["fp"] + fn
            # makes a request for the content of the textbook, converts it to bytes, and create the textbook pdf using the bytes
            resp = requests.get(url)
            pdf = io.BytesIO(resp.content)
            textbook_pdf = fitz.open(stream=pdf)
            print(f"have textbook {url}")

        nfn = textbook['nfn']
        ntextbook_pdf = None
        if nfn != '':
            url2 = "https://looma.website/content/" + textbook["fp"] + textbook['nfn']
            resp2 = requests.get(url2)
            pdf2 = io.BytesIO(resp2.content)
            ntextbook_pdf = fitz.open(stream=pdf2)
            print(f"have nepali textbook {url2}")


        rgx = re.compile(fr"^{prefix}\d", re.IGNORECASE)

        for chapter in collection.find({"_id": rgx}):
            try:
                if textbook_pdf is not None:
                    firstPage = chapter['pn'] - 1
                    lastPage = chapter['pn'] + chapter['len'] - 2

                    # creates the chapter pdf and takes the chapter pages from the textbook pdf and inserts them into the new chapter pdf
                    chapter_pdf = fitz.open()
                    chapter_pdf.insert_pdf(textbook_pdf, from_page=firstPage, to_page=lastPage)

                    # creates a variable with the save location and saves the pdf into that location
                    save_loc = f'{files_dir}/{textbook["fp"]}{'en'}'
                    os.makedirs(save_loc, exist_ok=True)
                    save_name = f"{chapter['_id']}.pdf"
                    save_info = os.path.join(save_loc, save_name)
                    chapter_pdf.save(save_info)
                    print("saved english ch")

                if ntextbook_pdf is not None:
                    nfirstPage = chapter['npn'] - 1
                    nlastPage = chapter['npn'] + chapter['nlen'] - 2

                    nchapter_pdf = fitz.open()
                    nchapter_pdf.insert_pdf(ntextbook_pdf, from_page=nfirstPage, to_page=nlastPage)

                    nsave_loc = f'{files_dir}/{textbook["fp"]}{'np'}'
                    os.makedirs(nsave_loc, exist_ok=True)
                    nsave_name = f"{chapter['_id']}-np.pdf"
                    nsave_info = os.path.join(nsave_loc, nsave_name)
                    nchapter_pdf.save(nsave_info)
                    print("saved nepali chapter ")
            except Exception as e:
                print(f"Error: {e}")
