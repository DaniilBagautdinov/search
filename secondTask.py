import os
import re
from bs4 import BeautifulSoup
from pymorphy2 import MorphAnalyzer


def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        return soup.get_text()


def process_text(text, morph):
    words = re.findall(r'\b[А-Яа-я]+\b', text)

    tokens = [word.lower() for word in words if
              word.isalpha() and word.lower() not in ('и', 'в', 'не', 'на', 'с', 'по', 'из')]

    lemmatized_words = [morph.parse(word)[0].normal_form for word in tokens]

    return tokens, lemmatized_words


def main():
    directory_path = './downloaded_pages'

    all_tokens = set()
    lemmas_with_tokens = {}
    morph = MorphAnalyzer()

    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            file_path = os.path.join(directory_path, filename)
            html_text = extract_text_from_html(file_path)

            tokens, lemmas = process_text(html_text, morph)

            all_tokens.update(tokens)

            for lemma, token in zip(lemmas, tokens):
                if lemma not in lemmas_with_tokens:
                    lemmas_with_tokens[lemma] = set()
                lemmas_with_tokens[lemma].add(token)

    with open('all_tokens.txt', 'w', encoding='utf-8') as token_file:
        token_file.write('\n'.join(all_tokens))

    with open('all_lemmas.txt', 'w', encoding='utf-8') as lemmatized_file:
        for lemma, tokens_with_lemma in lemmas_with_tokens.items():
            lemmatized_file.write(f"{lemma}: {' '.join(tokens_with_lemma)}\n")


if __name__ == "__main__":
    main()
