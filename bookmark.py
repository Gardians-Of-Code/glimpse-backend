from text_classify import TextClassifier
from text_extraction import TextExtraction

import asyncio
import aiohttp

import spacy
import joblib

import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

def spacy_tokenizer(doc):
        return [t.lemma_ for t in nlp(doc) if not t.is_punct and not t.is_space and not t.is_stop and t.is_alpha]
    
class Classifier:
    def __init__(self):
        global nlp
        nlp = spacy.load('en_core_web_sm')
        self.loaded_model=joblib.load("website_classifier_model.pkl")[1]
        self.text_extraction_tool = TextExtraction()
        self.text_classifier_tool = TextClassifier(self.loaded_model)


    async def get_tags_for_website(self,url):
        name = self.text_extraction_tool.extract_name(url)
        
        tags=[]
        text = await self.text_extraction_tool.extract_text([url])
        
        if text != ['Blocked']:
            tags = self.text_classifier_tool.assign_tag(text, self.loaded_model)
        
        return name,tags
    
        
if __name__ == "__main__":
    
    url = input("Enter the url:\n")
    name, tags = asyncio.run(Classifier().get_tags_for_website(url))
    print(f"Name: {name}\nTags: {tags}\n")
        