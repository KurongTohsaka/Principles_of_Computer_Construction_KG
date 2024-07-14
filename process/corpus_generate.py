import numpy as np

import re
import json


def trip_blank(raw_texts):
    tb_texts = re.sub(r"\s+", "", raw_texts)
    with open("corpus/tb_pcc_texts.txt", "w", encoding='utf-8') as f:
        f.write(tb_texts)
    return tb_texts


def trip_special_chars(tb_texts):
    tsc_texts = re.sub(r"[^\u4e00-\u9fa5，。：；！、？‘’“”（）]", "", tb_texts)
    with open("corpus/tsc_pcc_texts.txt", "w", encoding='utf-8') as f:
        f.write(tsc_texts)
    return tsc_texts


def cut_token_by_spliting_sentences(tsc_texts):
    sentences = tsc_texts.split("。")
    texts_sentence = {}
    ct_texts = {}
    for i, sentence in enumerate(sentences):
        tokens = [c for c in sentence]
        ct_texts[i] = tokens
        texts_sentence[i] = sentence
    ct_texts_json = json.dumps(ct_texts)
    texts_sentence_json = json.dumps(texts_sentence)
    with open("corpus/texts_token.json", "w", encoding='utf-8') as f:
        f.write(ct_texts_json)
    with open("corpus/texts_sentence.json", "w", encoding='utf-8') as f:
        f.write(texts_sentence_json)

    return ct_texts


if __name__ == "__main__":
    with open("raw_corpus/计算机组成原理第3版 (唐朔飞).txt", "r", encoding='utf-8') as f:
        raw_texts_1 = f.read()
    with open('raw_corpus/spider_raw_data.txt', 'r', encoding='utf-8') as f:
        raw_texts_2 = f.read()
    with open("raw_corpus/计算机组成原理-第6版.txt", 'r', encoding='utf-8') as f:
        raw_texts_3 = f.read()
    with open('raw_corpus/ppts.txt', 'r', encoding='utf-8') as f:
        raw_texts_4 = f.read()
    raw_texts = raw_texts_1 + '。' + raw_texts_2 + '。' + raw_texts_3 + '。' + raw_texts_4
    tb_texts = trip_blank(raw_texts)
    tsc_texts = trip_special_chars(tb_texts)
    ct_texts = cut_token_by_spliting_sentences(tsc_texts)

    print(len(raw_texts))
    print(len(tb_texts))
    print(len(tsc_texts))
    print(len(ct_texts))
    print(ct_texts[0])
