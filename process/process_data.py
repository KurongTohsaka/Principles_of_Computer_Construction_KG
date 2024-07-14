import json


def remove_unlabled_shots_from_corpus(corpus: dict, blank_seq: list):
    for n in blank_seq:
        for idx in range(n * 8, (n + 1) * 8):
            del corpus[str(idx)]
    return corpus

def remove_null_dict_from_labels(corpus_labels: dict, blank_seq: list):
    for n in blank_seq:
        del corpus_labels[n]
    return corpus_labels

def initial_dataset(corpus: dict, corpus_labels: dict):
    dataset_dict = {"corpus": [], "labels": []}
    for key, value in corpus.items():
        dataset_dict['corpus'].append(value)
    for key, value in corpus_labels.items():
        for i in value:
            dataset_dict['labels'].append(i)

    return dataset_dict

def process_labels(dataset_dict: dict):
    dataset_dict['new_labels'] = []
    for i, sentence in enumerate(dataset_dict['corpus']):
        tmp = ['O'] * len(sentence)
        labels = dataset_dict['labels'][i]['output']
        for label in labels:
            for idx in range(label['start'], label['end']):
                tmp[idx] = f'I-{label['type']}'
        dataset_dict['new_labels'].append(tmp)

    return dataset_dict

if __name__ == "__main__":
    with open("corpus/texts_sentence.json", "r", encoding="utf-8") as f:
        corpus = json.loads(f.read())
    with open("corpus/corpus_labels.txt", "r", encoding="utf-8") as f:
        corpus_labels = eval(f.read())

    blank_seq = []
    for k, v in corpus_labels.items():
        if not v:
            blank_seq.append(k)

    new_corpus = remove_unlabled_shots_from_corpus(corpus, blank_seq)
    new_corpus_labels = remove_null_dict_from_labels(corpus_labels, blank_seq)
    dataset_dict = initial_dataset(new_corpus, new_corpus_labels)
    new_dataset_dict = process_labels(dataset_dict)

    with open('output/datasets.json', 'w', encoding='utf-8') as f:
        new_dataset_dict['labels'] = dataset_dict['new_labels'].copy()
        del new_dataset_dict['new_labels']
        f.write(json.dumps(new_dataset_dict))