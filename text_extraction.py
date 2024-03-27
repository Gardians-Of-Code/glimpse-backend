import asyncio
import aiohttp
import requests
import bs4
from bs4 import BeautifulSoup
import spacy
import re
from urllib.parse import urlparse

class ScrapTool:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")


    async def visit_url(self, session, website_url):
        try:
            async with session.get(website_url, timeout=10) as response:
                if response.status == 403:                         
                    return {"website_url": website_url, "website_text": "Blocked"}
                content = await response.read()
                soup = bs4.BeautifulSoup(content, "lxml")
                return self.get_text_content(soup)
            
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return None


    def get_text_content(self, soup):
        tags_to_ignore = ['style', 'script', 'head', 'title', 'meta', '[document]', "h1", "h2", "h3", "h4", "h5", "h6", "noscript"]
        tags = soup.find_all(lambda tag: tag.name not in tags_to_ignore)
        result = []
        for tag in tags:
            if isinstance(tag, bs4.element.Comment) or not tag.text.strip():
                continue
            result.append(tag.get_text(strip=True))
        return ' '.join(result)


    async def extract_website_text(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.visit_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results
    
    
    def isIrrelevant(self, element):
        irrelevant_tags = ['header', 'footer', 'aside', 'nav']                
        for tag in irrelevant_tags:
            if element.find_parents(tag):
                return True
        return False


    def getParagraphText(self, soup):
        para_return=""
        allPara = soup.find_all('p')
        for para in allPara:
            if not self.isIrrelevant(para):
                para_text = para.get_text(separator=' ', strip=True).replace('\n', ' ')
                if para_text and any(char.isalnum() for char in para_text):

                    para_return+=para_text+"\n"
        return para_return
        


class TextExtraction:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.scrapper = ScrapTool()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840 Safari/537.36'}


    def extract_useful_words(self, doc):
        doc=doc[:1000000]
        doc = self.nlp(doc)
        useful_words = [token.text.lower().strip() for token in doc if not token.is_stop and not token.is_punct and not token.text.isnumeric() and token.text.isalnum()]
        useful_words = ' '.join(useful_words)
        return useful_words


    async def extract_imp_words(self, website_urls):
        website_texts = await self.scrapper.extract_website_text(website_urls)
        useful_word_lists = []
        for website_text in website_texts:
            if website_text and isinstance(website_text, str):
                useful_word_lists.append(self.extract_useful_words(website_text))
            else:
                useful_word_lists.append('Blocked')
        return useful_word_lists
     
     
    def extract_name(self, url):
        pattern = re.compile(r'(https?://|www\.)?(www\.)?([a-z0-9]+)(\..+)?')
        domain_name = pattern.sub(r'\3',url)
        return domain_name
    
    
    def extract_text(self,url):
        res = requests.get(url, headers=self.headers).content
        soup = BeautifulSoup(res, 'html.parser')
        extracted_text = self.scrapper.getParagraphText(soup)
        return extracted_text
    
    
    
