from text_classify import TextClassifier
from text_extraction import TextExtraction

from tokenizer import *
import joblib

import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class Classifier:
    def __init__(self):
        # global nlp
        # nlp = spacy.load('en_core_web_sm')
        print("Loading model...")
        self.loaded_model = joblib.load("website_classifier_model.pkl")[1]
        self.text_extraction_tool = TextExtraction()
        self.text_classifier_tool = TextClassifier(self.loaded_model)

    async def get_tags_for_website(self, url):
        name = self.text_extraction_tool.extract_name(url)

        tags = []
        text = await self.text_extraction_tool.extract_text([url])

        if text != ["Blocked"]:
            tags = self.text_classifier_tool.assign_tag(text, self.loaded_model)

        return name, tags

