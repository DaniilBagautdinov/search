import os
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.corpus import stopwords
import pymorphy2
import re

BAD_TOKENS_TAGS = {"PREP", "CONJ", "PRCL", "INTJ", "LATN", "PNCT", "NUMB", "ROMN", "UNKN"}


def extract_text_from_html(file_path):
    with open(file_path) as f:
        soup = BeautifulSoup(f.read(), features="html.parser")
    return " ".join(soup.stripped_strings)


def process_documents(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            text = extract_text_from_html(file_path)
            tokenize_and_lemmatize(text)


def tokenize_and_lemmatize(text):
    words = re.findall(r'\b[А-Яа-я]+\b', text)
    for word in words:
        if (
                word.lower() not in stop_words
                and not any(char.isdigit() for char in word)
        ):
            morph = morph_analyzer.parse(word)[0]
            if (
                    any(tag in morph.tag for tag in BAD_TOKENS_TAGS)
                    or morph.score < 0.5
            ):
                continue
            lemma = morph.normal_form
            tokens.add(word)
            lemmas[lemma].add(word)


def write_tokens_to_file(tokens_file_path):
    with open(tokens_file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(tokens))


def write_lemmas_to_file(lemmas_file_path):
    with open(lemmas_file_path, "w", encoding="utf-8") as file:
        for lemma, tokens in lemmas.items():
            file.write(f"{lemma}: {' '.join(tokens)}\n")


if __name__ == "__main__":
    stop_words = set(stopwords.words("russian"))
    morph_analyzer = pymorphy2.MorphAnalyzer()
    tokens = set()
    lemmas = defaultdict(set)
    process_documents('./downloaded_pages')
    write_tokens_to_file("all_tokens.txt")
    write_lemmas_to_file("all_lemmas.txt")
