import os

from .summary import *
# from .config import *

from pymongo import MongoClient
from langdetect import detect
import nltk
#from nltk.tokenize import word_tokenize
from nepalikit.tokenization import Tokenizer

import string
import ssl
import re
            
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
    """def has_section(self, ch):
        search = re.search(r"([1-9]|10|11|12)(EN|S|SF|M|SS|N|H|V|CS)([0-9]{2})(\.[0-9]{2})?", ch, re.IGNORECASE)
        try:
            section = search[4]
            return section
        except:
            return False"""    
             
    def define_word(self, text):
        prompt_en = PromptTemplate(
            input_variables=["text"],
            template="{text}\n In english, please give every definition for the above word. Also make sure that an elementary schooler can understand it and it's less than 20 words. If the definition is unknown, only say 'Definition Not Found'."
        )
        prompt_np = PromptTemplate(
            input_variables=["text"],
            template="{text}\n नेपालीमा, कृपया माथिको शब्दको सबै परिभाषा दिनुहोस्। परिभाषा प्राथमिक विद्यालयका विद्यार्थीले बुझ्ने गरी र २० शब्दभित्र हुनुपर्छ। यदि परिभाषा थाहा छैन भने, 'Definition Not Found' मात्र लेख्नुहोस्।"
        )
        chain_en = prompt_en | self.llm | StrOutputParser()
        chain_np = prompt_np | self.llm | StrOutputParser()
        definition_en = chain_en.invoke({"text": text})
        definition_np = chain_np.invoke({"text": text})
        return definition_en, definition_np
            
    def word_part(self, text):
        prompt_en = PromptTemplate(
            input_variables=["text"],
            template="{text}\n In english, give the part of speech for the above word in under 13 characters"
        )
        prompt_np = PromptTemplate(
            input_variables=["text"],
            template="{text}\n नेपालीमा, माथिको शब्दको पदको प्रकार १३ वर्णभित्र दिनुहोस्"
        )
        chain_en = prompt_en | self.llm | StrOutputParser()
        chain_np = prompt_np | self.llm | StrOutputParser()
        part_en = chain_en.invoke({"text": text})
        part_np = chain_np.invoke({"text": text})
        return part_en, part_np
        
    def translate_word(self, text, lang):
        if lang == 'en':
            to_lang = 'Nepali'
        elif lang == 'np':
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
            try:
                 _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            nltk.download('punkt_tab')
            
            chapter_language = detect(chapter_content)
            other_lang = ''
            if chapter_language == "en":
                other_lang = "np"
            elif chapter_language == "ne":
                chapter_language = "np"
                other_lang = "np"

            grade_new = self.get_ch_data(new_chapter, "grade")
            sub_new = self.get_ch_data(new_chapter, "subject")
            number_new = self.get_ch_data(new_chapter, "number")
            #sect_new = self.has_section(new_chapter)
                
            db = client.get_database("looma")
            collection = db.get_collection("dict_test")
            
            if chapter_language == "en":
                word_tokens = nltk.word_tokenize(chapter_content)
            elif chapter_language == "np":
                tokenizer = Tokenizer()
                word_tokens = tokenizer.tokenize(chapter_content, level='word')
                   
            for word in word_tokens:
                try:
                    if chapter_language == "en":
                        word = word.lower()
                    word = word.translate(str.maketrans('', '', string.punctuation))
                    translation = self.translate_word(word, chapter_language)
                    
                    query1 = {chapter_language: word}
                    query2 = {other_lang: translation}
                    entry1 = collection.find_one(query1)
                    entry2 = collection.find_one(query2)
                    
                    if entry1 is None and entry2 is None and (len(word) > 2 or len(translation > 2)) and self.has_numbers(word) == False:
                        def_en, def_np = self.define_word(word)
                        if ("Definition Not Found" or "Please provide the word") not in def_en:
                            part_en, part_np = self.word_part(word)
                            entry = {
                                "en": word if chapter_language == "en" else translation,
                                "np": translation if chapter_language == "en" else word,
                                "meanings": [{"part_en": part_en, "part_np": part_np, "def_en": def_en, "def_np": def_np}],
                                "ch_id": [{sub_new: new_chapter}]
                            }
                            collection.insert_one(entry)
                    elif (entry1 is not None or entry2 is not None) and (len(word) > 2 or len(translation > 2)) and self.has_numbers(word) == False:
                        query = {chapter_language: word} if entry1 is not None else {other_lang: translation}
                        entry = entry1 if entry1 is not None else entry2
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
                            #sect_ori = self.has_section(ch_ori)
                            if (check not in entry['ch_id'] and grade_new < grade_ori) or (check not in entry['ch_id'] and grade_new == grade_ori and number_new < number_ori):
                                place = f'ch_id.{index}.{sub_new}'
                                new = {"$set": {place: new_chapter}}    
                                collection.update_one(query, new)
                except Exception as e:
                    pass
        except Exception as e:
                print(f"Error: {e}")
