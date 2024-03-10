import pymorphy2
from bs4 import BeautifulSoup
import os
import re
from collections import defaultdict
from nltk.corpus import stopwords

BAD_TOKENS_TAGS = {"PREP", "CONJ", "PRCL", "INTJ", "LATN", "PNCT", "NUMB", "ROMN", "UNKN"}


def build_inverted_index_from_directory(directory_path, index_filename="inverted_index.txt"):
    if os.path.exists(index_filename):
        inverted_index = read_inverted_index(index_filename)
    else:
        inverted_index = defaultdict(list)
        for filename in os.listdir(directory_path):
            if filename.endswith(".html") or filename.endswith(".htm"):
                file_path = os.path.join(directory_path, filename)

                with open(file_path) as f:
                    soup = BeautifulSoup(f.read(), features="html.parser")
                text = " ".join(soup.stripped_strings)

                terms = tokenize(text)
                for term in set(terms):
                    inverted_index[term].append(filename)

        write_inverted_index(index_filename, inverted_index)

    return inverted_index


def read_inverted_index(index_filename):
    inverted_index = defaultdict(list)
    with open(index_filename, "r", encoding="utf-8") as index_file:
        for line in index_file:
            term, filenames = line.strip().split(": ")
            filenames = filenames.split(", ")
            inverted_index[term] = filenames
    return inverted_index


def write_inverted_index(index_filename, inverted_index):
    with open(index_filename, "w", encoding="utf-8") as index_file:
        for term, filenames in inverted_index.items():
            index_file.write(f"{term}: {', '.join(filenames)}\n")


def tokenize(text):
    stop_words = set(stopwords.words("russian"))
    morph_analyzer = pymorphy2.MorphAnalyzer()
    tokens = set()
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
            tokens.add(word)
    return tokens


def boolean_search(query, inverted_index):
    stack = []
    operators = set(['AND', 'OR', 'NOT'])
    for token in query.split():
        if token.upper() in operators:
            stack.append(token.upper())
        elif token.upper() == '(':
            stack.append(token.upper())
        elif token.upper() == ')':
            while stack and stack[-1] != '(':
                operator = stack.pop()
                if operator == 'AND':
                    operand1 = set(stack.pop())
                    operand2 = set(stack.pop())
                    stack.append(list(operand1.intersection(operand2)))
                elif operator == 'OR':
                    operand1 = set(stack.pop())
                    operand2 = set(stack.pop())
                    stack.append(list(operand1.union(operand2)))
                elif operator == 'NOT':
                    operand = set(stack.pop())
                    stack.append(list(set(inverted_index.keys()).difference(operand)))
            stack.pop()
        else:
            stack.append(inverted_index.get(token, []))

    result = stack.pop()
    return result if result else []


directory_path = "./downloaded_pages"
inverted_index = build_inverted_index_from_directory(directory_path)

query = "Большая"
result = boolean_search(query, inverted_index)
print("Результат булевого поиска:", result)
