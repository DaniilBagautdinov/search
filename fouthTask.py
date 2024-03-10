import math
import os
import shutil
import pymorphy2
from collections import Counter, defaultdict
from pathlib import Path
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer

FILES_PATH = "./downloaded_pages"
TOKENS_PATH = "token_tf_idf"
LEMMAS_PATH = "lemma_tf_idf"
BAD_TOKENS_TAGS = {"PREP", "CONJ", "PRCL", "INTJ", "LATN", "PNCT", "NUMB", "ROMN", "UNKN"}

def extract_text_from_html(file_path):
    with open(file_path) as f:
        soup = BeautifulSoup(f.read(), features="html.parser")
    return " ".join(soup.stripped_strings)


def idf_word_counter(files_texts, word):
    count = sum(word in text for text in files_texts.values())
    if count > 100:
        print(word, count)
    return count


def tokenize_and_lemmatize(text):
    tokens = tokenizer.tokenize(text)
    for token in tokens:
        if (
                token.isalpha()
                and token not in stop_words
                and not any(char.isdigit() for char in token)
        ):
            morph = morph_analyzer.parse(token)[0]
            if (
                    any(tag in morph.tag for tag in BAD_TOKENS_TAGS)
                    or morph.score < 0.5
            ):
                continue
            lemma = morph.normal_form
            all_tokens.add(token)
            lemmas[lemma].add(token)


if __name__ == "__main__":
    if not os.path.exists(TOKENS_PATH):
        os.makedirs(TOKENS_PATH, exist_ok=True)
    if not os.path.exists(LEMMAS_PATH):
        os.makedirs(LEMMAS_PATH, exist_ok=True)
        
    files_texts = {}
    for filename in os.listdir(FILES_PATH):
        if filename.endswith(".html"):
            file_path = os.path.join(FILES_PATH, filename)
            text = extract_text_from_html(file_path)
            files_texts[filename] = text

    for file_name, text in files_texts.items():
        stop_words = set(stopwords.words("russian"))
        tokenizer = WordPunctTokenizer()
        morph_analyzer = pymorphy2.MorphAnalyzer()
        all_tokens = set()
        lemmas = defaultdict(set)
        tokenize_and_lemmatize(text)
        words_counter = Counter(tokenizer.tokenize(text))

        for token in all_tokens:
            tf = words_counter[token] / len(tokenizer.tokenize(text))
            idf = math.log(len(files_texts) / (1 + idf_word_counter(files_texts, token)))
            tf_idf = tf * idf
            with open(Path(TOKENS_PATH) / f"{os.path.splitext(file_name)[0]}.txt", "a") as f:
                f.write(f"{token} {idf} {tf_idf}\n")

        for lemma, tokens in lemmas.items():
            tf_n = sum(words_counter[token] for token in tokens)
            count = sum(any(token in text for token in tokens) for text in files_texts.values())
            tf = tf_n / len(tokenizer.tokenize(text))
            idf = math.log(len(files_texts) / (1 + count))
            tf_idf = tf * idf
            with open(Path(LEMMAS_PATH) / f"{os.path.splitext(file_name)[0]}.txt", "a") as f:
                f.write(f"{lemma} {idf} {tf_idf}\n")