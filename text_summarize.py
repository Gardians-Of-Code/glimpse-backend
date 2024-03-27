from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
nltk.download('punkt')


class TextSummarizer:
  
  def __init__(self):
    self.checkpoint = "facebook/bart-large-cnn"
    self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint, max_length=1024, truncation=True)
    self.model_s = AutoModelForSeq2SeqLM.from_pretrained(self.checkpoint)
    self.tok_len = self.tokenizer.max_len_single_sentence


  def get_chunks(self,extracted_text):
    sentences = nltk.tokenize.sent_tokenize(extracted_text)
    length = 0; chunk = ""; chunks = []
    for sentence in sentences:
      sent_len = len(self.tokenizer.tokenize(sentence))
      combined_length = sent_len + length
      if combined_length <= self.tok_len//2:
        chunk += sentence + " "
        length = combined_length  
      else:
        chunks.append(chunk.strip())
        length = 0
        chunk = "" 
        while sent_len > self.tok_len//2:
          chunks.append((sentence[:self.tok_len//2]+'\n').strip())
          sentence=sentence[:self.tok_len//2]
          sent_len=len(self.tokenizer.tokenize(sentence))  
        else:  
          chunk += sentence + '\n'
          length = sent_len
    if chunk:
      chunks.append(chunk.strip())
    return chunks


  def truncate(self,extracted_text):
      if(len(extracted_text)>=100000):
          extracted_text=extracted_text[:100000]
      return extracted_text


  def get_summary(self,chunks):
      inputs = [self.tokenizer(chunk, return_tensors="pt") for chunk in chunks]
      summary=""
      for input in inputs:
          output = self.model_s.generate(**input, max_length=1024)
          summary+=self.tokenizer.decode(*output, skip_special_tokens=True)+"\n"
      return summary
