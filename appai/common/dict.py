import os

from .summary import *
# from .config import *

from pymongo import MongoClient
# from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import string
import nltk
# import ssl
import re

nltk.download('stopwords')
nltk.download('punkt_tab')
stop_words = set(stopwords.words('english'))
            
class Dictionary:
    def __init__ (self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=openai_api_key)
    def has_numbers(self, inputString):
        return any(char.isdigit() for char in inputString)
    def get_ch_data(self, ch, field):
        # search = re.search(r"([1-9]|10|11|12)(EN|S|SF|M|SS|N|H|V|CS)([0-9]{2})(\.[0-9]{2})?", ch, re.IGNORECASE)
        search = re.search(r"([1-9]|10|11|12)(EN|S|SF|M|SS|N|H|V|CS)([0-9]{2}\.[0-9]{2})?", ch, re.IGNORECASE)
        if field == "grade":
            grade = search[1]
            return int(grade)
        elif field == "subject":
            subject = search[2]
            return subject
        elif field == "number":
            number = search[3]
            return number 
    def has_section(self, ch):
        search = re.search(r"([1-9]|10|11|12)(EN|S|SF|M|SS|N|H|V|CS)([0-9]{2})(\.[0-9]{2})?", ch, re.IGNORECASE)
        try:
            section = search[4]
            return section
        except:
            return False     
    def define_word(self, text):
        prompt = PromptTemplate(
            input_variables=["text"],
            template="{text}\nPlease give every definition for the above word. Also make sure that an elementary schooler can understand it and it's less than 20 words. If the definition is unknown, only say 'Definition Not Found'."
        )
        chain = prompt | self.llm | StrOutputParser()
        definition = chain.invoke({"text": text})
        return definition
    def word_part(self, text):
        prompt = PromptTemplate(
            input_variables=["text"],
            template="{text}\n Give the part of speech for the above word in under 13 characters"
        )
        chain = prompt | self.llm | StrOutputParser()
        translation = chain.invoke({"text": text})
        return translation
    def translate_word(self, text, lang):
        if lang == 'en':
            to_lang = 'Nepali'
        elif lang == 'ne':
            to_lang = 'English'
        prompt = PromptTemplate(
            input_variables=["text", "lang"],
            template="{text}\n Only give the above text translated into {lang}"
        )
        chain = prompt | self.llm | StrOutputParser()
        translation = chain.invoke({"text": text, "lang": to_lang})
        return translation
        
    def dict_update(self, new_chapter: str, chapter_content: str, client: MongoClient):
        try:
            # try:
            #     _create_unverified_https_context = ssl._create_unverified_context
            # except AttributeError:
            #     pass
            # else:
            #     ssl._create_default_https_context = _create_unverified_https_context
            # nltk.download('stopwords')
            # nltk.download('punkt_tab')
            # stop_words = set(stopwords.words('english'))
            
            # chapter_language = detect(chapter_content)
            # if chapter_language == "ne":
            #     chapter_content = self.translate_word(chapter_content, "ne")

            grade_new = self.get_ch_data(new_chapter, "grade")
            sub_new = self.get_ch_data(new_chapter, "subject")
            number_new = self.get_ch_data(new_chapter, "number")
            sect_new = self.has_section(new_chapter)
                
            db = client.get_database("looma")
            collection = db.get_collection("dictionary")

            word_tokens = word_tokenize(chapter_content)

            # filtered_text = []
            filtered_text = set()

            for w in word_tokens:
                word = w.lower()
                if word not in stop_words:
                    #filtered_text.append(word)
                    filtered_text.add(word)

            for word in filtered_text:
                word = word.translate(str.maketrans('', '', string.punctuation))
                # found = collection.count_documents({"en": word})
                query = {"en": word}
                entry = collection.find_one(query)
                #  if found == 0 and len(word) > 2 and self.has_numbers(word) == False:
                if entry is None and len(word) > 2 and self.has_numbers(word) == False:
                    definition = self.define_word(word)
                    if ("Definition Not Found" or "Please provide the word") not in definition:
                        np_word = self.translate_word(word, "en")
                        part = self.word_part(word)
                        entry = {
                            "en": word,
                            "np": np_word,
                            "meanings": [{"part": part, "def": definition}],
                            "ch_id": [{sub_new: new_chapter}]
                        }
                        collection.insert_one(entry)
                elif entry is not None and len(word) > 2 and self.has_numbers(word) == False:
                    # query = {"en": word}
                    # entry = collection.find_one(query)
                    check = {sub_new: new_chapter}
                    
                    index = 0
                    status = "same"
                    if 'ch_id' not in entry:
                        entry['ch_id'] = [] 
                        collection.update_one(query, {'$set': entry}) 
                    for i in entry['ch_id']:
                        try:
                            ch_ori = i[sub_new]
                            status = "changed"
                            break
                        except:
                            index += 1
                            continue
                
                    if status == "same":
                        place = "ch_id"
                        new = {"$push": {place: {sub_new: new_chapter}}}    
                        collection.update_one(query, new)
                    if status == "changed":
                        grade_ori = self.get_ch_data(ch_ori, "grade")
                        number_ori = self.get_ch_data(ch_ori, "number")
                        sect_ori = self.has_section(ch_ori)
                        if (check not in entry['ch_id'] and grade_new < grade_ori) or (check not in entry['ch_id'] and grade_new == grade_ori and number_new < number_ori):
                    
                            place = f'ch_id.{index}.{sub_new}'
                            new = {"$set": {place: new_chapter}}    
                            collection.update_one(query, new)
            print("dictionary is updated")
        except Exception as e:
                print(f"Error: {e}")