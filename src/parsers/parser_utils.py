import json
import nltk
from nltk import FreqDist, word_tokenize
import random
import re
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))


class TextProcessor:

    def __init__(self, config):
        self.config = config
        self.token_counts = FreqDist()
        self.proba_dct = {}
        nltk.download('punkt_tab')


    def __call__(self, soup):
        if 'remove_section_headers' in self.config:
            soup = self.remove_section_headers(soup)
        text = self.extract_text(soup)
        if 'remove_non_ascii_symbols' in self.config:
            text = self.remove_non_ascii_symbols(text)
        if 'remove_references' in self.config:
            text = self.remove_references(text)
        sentence_lst = self.split_into_sentences(text)
        if 'remove_latex' in self.config:
            sentence_lst = self.remove_latex(sentence_lst)
        if 'strip_sentences' in self.config:
            sentence_lst = self.strip_sentences(sentence_lst)
        if 'remove_short_sentences' in self.config:
            sentence_lst = self.remove_short_sentences(sentence_lst, **self.config['remove_short_sentences'])
        if 'remove_frequent_tokens' in self.config:
            for sentence in sentence_lst:
                tokens = word_tokenize(sentence)
            self.token_counts.update(tokens)
        return sentence_lst
    

    def save_state(self, file_name):
        file_name = file_name + '.json' if not file_name.endswith('.json') else file_name
        with open(file_name, 'w') as f:
            json.dump(self.token_counts, f)


    def load_state(self, file_name):
        with open(file_name, 'r') as f:
            self.token_counts = json.load(f)
    

    def calc_probas(self):
        """Calc removal probability of each token. The higher the token occurence in text, the more the probability of removal"""
        if not len(self.token_counts):
            raise ValueError('You must calculate token counts before calculating probas. Use "__call__" first')
        # Calc removal probability = mean occurence / current token occurence
        mean_count = sum(self.token_counts.values()) / len(self.token_counts)
        for token, count in self.token_counts.items():
            proba_to_remove = max(0, 1 - mean_count / count)
            self.proba_dct.update({token: proba_to_remove})


    def remove_frequent_tokens(self, sentence):
        """Remove tokens based on calculated probas"""
        if not len(self.token_counts):
            raise ValueError('You must calculate probas before token removal. Use "calc_probas" first')
        
        # Tokenize and remove frequent tokens
        token_lst = word_tokenize(sentence)
        token_lst_new = [token for token in token_lst if random.random() > self.proba_dct.get(token, 0)]
        sentence_new = ' '.join(token_lst_new)
        sentence_new = sentence_new.strip()

        return sentence_new if sentence_new else sentence


    def remove_section_headers(self, soup):
        """Remove section headers"""
        for header in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
            header.decompose()
        return soup
    

    def extract_text(self, soup):
        return soup.get_text()


    def remove_non_ascii_symbols(self, text):
        return re.sub(r'[^\x00-\x7F]+', '', text)


    def remove_references(self, text):
        """Remove citations and references (e.g., [12])"""
        return re.sub(r'\[\d+\]', '', text)


    def split_into_sentences(self, text):
        """Split the text into sentences and remove empty strings"""
        sentences = re.split(r'(?<=\.|\?)\s+(?!")|\n+|(?<=\.)"', text)
        return [i for i in sentences if i]


    def remove_latex(self, sentences):
        """Remove parts like {\\displaystile ...}"""
        return [i for i in sentences if not i.startswith('{\\')]


    def strip_sentences(self, sentences):
        return [i.strip() for i in sentences]
    

    def remove_short_sentences(self, sentences, min_len=2):
        return [i for i in sentences if len(i) >= min_len]
