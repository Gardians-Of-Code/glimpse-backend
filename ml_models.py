from text_classify import TextClassifier
from text_extraction import TextExtraction, ScrapTool
from text_summarize import TextSummarizer

from tokenizer import *
import joblib

import asyncio
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class Models:
    def __init__(self):
        print("Loading model...")
        self.loaded_model = joblib.load("website_classifier_model.pkl")[1]
        self.text_extraction_tool = TextExtraction()
        self.text_classifier_tool = TextClassifier(self.loaded_model)
        self.text_summarization_tool = TextSummarizer()
        
        
    async def get_tags_for_website(self, url):
        name = self.text_extraction_tool.extract_name(url)
        tags = []
        text = await self.text_extraction_tool.extract_imp_words([url])
        if text != ["Blocked"]:
            tags = self.text_classifier_tool.assign_tag(text, self.loaded_model)
        return name, tags
    
    
    def summarize_website(self, url):
        extracted_text = self.text_extraction_tool.extract_text(url)
        extracted_text = self.text_summarization_tool.truncate(extracted_text)
        chunks = self.text_summarization_tool.get_chunks(extracted_text)
        summary = self.text_summarization_tool.get_summary(chunks)
        return summary
    
    
    def estimate_reading_time(self, url):
        extracted_text = self.text_extraction_tool.extract_text_v2(url)
        doc=nlp(extracted_text)
        tokens = [t.text for t in doc if not t.is_punct and not t.is_space]
        return max(1,len(tokens)//200)
