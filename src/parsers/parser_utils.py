import os
import nltk
from nltk import FreqDist, word_tokenize
import random
import re

class TextProcessor:

    def __init__(self):
        self.token_counts = FreqDist()
        self.proba_dct = {}
        nltk.download('punkt_tab')


    def __call__(self, soup):
        text = self.remove_section_headers(soup)
        text = self.remove_non_ascii_symbols(text)
        text = self.remove_references(text)
        sentence_lst = self.split_into_sentences(text)
        sentence_lst = self.remove_latex(sentence_lst)
        sentence_lst = self.strip_sentences(sentence_lst)
        for sentence in sentence_lst:
            tokens = word_tokenize(sentence)
        self.token_counts.update(tokens)
        return sentence_lst
    

    def calc_probas(self):
        """Calc removal probability of each token. The higher the token occurence in text, the more the probability of removal"""
        if not len(self.token_counts):
            raise ValueError('You must calculate token counts before calculating probas. Use "__call__" first')
        # Calc removal probability = mean occurence / current token occurence
        mean_count = sum(self.token_counts.values()) / len(self.token_counts)
        for token, count in self.token_counts.items():
            proba_to_remove = max(0, 1 - mean_count / count)
        self.proba_dct.update({token: proba_to_remove})


    def remove_frequent_tokens(self, data_path):
        """Remove tokens based on calculated probas"""
        if not len(self.token_counts):
            raise ValueError('You must calculate probas before token removal. Use "calc_probas" first')
        for file in os.listdir(data_path):
            file_name = os.path.join(data_path, file)

            # Read sentence
            with open(file_name, 'r', encoding='utf-8') as f:
                sentence = f.read()

            # Tokenize and remove frequent tokens
            token_lst = word_tokenize(sentence)
            token_lst_new = [token for token in token_lst if random.random() > self.proba_dct[token]]
            sentence_new = ' '.join(token_lst_new)

            # Save updated sentence if it is not empty
            if sentence_new.strip():
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(sentence_new)


    def remove_section_headers(self, soup):
        """Remove section headers"""
        for header in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
            header.decompose()
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
