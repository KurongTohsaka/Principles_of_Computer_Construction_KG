from transformers import AutoTokenizer
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
from torch.optim import AdamW
from torch import optim
import torch.nn as nn
import torch
from tqdm.auto import tqdm
import numpy as np

import datetime
import logging
import random
import time
import json
import os
import warnings

warnings.filterwarnings('ignore')

# 标签映射
label_to_id = {
    "COMP": 0, "DATA": 1, "ARCH": 2, "PROG": 3, "PROT": 4,
    "PERF": 5, "STOR": 6, "ALG": 7, "IO": 8, "TECH": 9, "INST": 10
}

# 关系抽取的标签设计
relation_to_id = {
    "contain": 0, "sequence": 1, "synonymy": 2, "related": 3, "attribute": 4
}


class RelationExtractionDataset(Dataset):
    def __init__(self, json_filename: str):
        with open(json_filename, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


def preprocess_data(batch_samples, num_relations, max_entities):
    sentences = []
    relation_labels = []
    masks = []

    for item in batch_samples:
        entity_text_to_id = {}
        sentence = item['sentence']
        entities = item['entities']
        relations = item['relations']

        # 按照实体的起始位置进行排序，确保替换时不会重叠
        entities = sorted(entities, key=lambda x: x['start'], reverse=True)

        # 加入实体标记
        for idx, entity in enumerate(entities):
            entity_text = entity['text']
            entity_start = entity['start']
            entity_end = entity['end']
            entity_id = f"{entity_text}_{entity_start}"
            entity_text_to_id[entity_id] = idx  # 使用索引作为ID
            entity_label = f"E{len(entities) - idx}"
            sentence = sentence[:entity_start] + f"[{entity_label}S]" + sentence[
                                                                        entity_start:entity_end] + f"[{entity_label}E]" + sentence[
                                                                                                                          entity_end:]
        sentences.append(sentence)

        # 初始化关系标签矩阵
        relation_vector = np.zeros((1, num_relations * max_entities * (max_entities - 1) // 2 + 1), dtype=int)

        # 转换关系标签
        # 建立一个实体id和相应位置实体的映射表
        # 然后根据实体id再去把对应的实体关系置1，这才是正确的操作
        # 下面的这份代码，操作逻辑乱七八糟
        # {'双倍数据率结构_0': 1, '预取结构_14': 2}
        entity_ids = {}
        for i, key in enumerate(entity_text_to_id.keys()):
            entity_ids[key] = len(entity_text_to_id) - i

        if not relations:
            relation_vector[0, -1] = 1
        else:
            for relation in relations:
                head = relation[0]
                relation_label = relation[1]
                tail = relation[2]

                # 这几句涉及多关系的实体重叠问题，必须要考虑到
                # 获取实体的起始位置
                head_entity_start = next(entity['start'] for entity in entities if entity['text'] == head)
                tail_entity_start = next(entity['start'] for entity in entities if entity['text'] == tail)
                # 通过位置来区分重叠实体
                head_entity = f"{head}_{head_entity_start}"
                tail_entity = f"{tail}_{tail_entity_start}"
                # 查找实体id，以确认标签位置
                # 标签位置公式，对于关系R_x(E_y,E_z)
                # entity_pair_start = (y-1)*(2*mas_entities-y)/2 + (z-y-1)
                # 标签位置 = entity_pair_start * num_relations + x

                if head_entity in entity_text_to_id and tail_entity in entity_text_to_id:
                    head_entity_id = entity_ids[head_entity]
                    tail_entity_id = entity_ids[tail_entity]
                    relation_type = relation_to_id[relation_label]
                    if tail_entity_id < head_entity_id:
                        entity_pair = (tail_entity_id, head_entity_id)
                    else:
                        entity_pair = (head_entity_id, tail_entity_id)
                    # (1,0)自然是没有的
                    # 这里涉及到关系是单向还是双向的，但是双向的关系之前已经被我处理为了两个单向，但是吧...，要是考虑单向关系会导致现有的标签维度翻倍
                    # 不涉及单向关系了，将实体对全部设置为标准形式
                    # 下面的两个公式计算似乎有误，还需要检查验证
                    # entity_pair_start = generate_entity_pair_positions(max_entities, num_relations)[entity_pair]
                    entity_pair_start = (entity_pair[0] - 1) * (2 * max_entities - entity_pair[0]) / 2 + (
                            entity_pair[1] - entity_pair[0] - 1)
                    label_idx = entity_pair_start * num_relations + relation_type
                    try:
                        relation_vector[0, int(label_idx)] = 1
                    except Exception:
                        print(f"Entity pair: {entity_pair}")
                        print(f"Get pair start: {entity_pair_start}")
                        print(f"Get Index: {label_idx}")
                        raise

        relation_labels.append(relation_vector)

        # 生成掩码
        mask = np.zeros((1, num_relations * max_entities * (max_entities - 1) // 2 + 1), dtype=int)
        mask[0, -1] = 1

        mask[0, :num_relations * len(entities) * (len(entities) - 1) // 2] = 1

        masks.append(mask)

    return sentences, relation_labels, masks


def get_dataloader(dataset, tokenizer, batch_size=4, shuffle=False, max_len=1024, num_relations=5, max_entities=32):
    def collate_fn(batch_samples):
        sentences, relation_labels, masks = preprocess_data(batch_samples, num_relations, max_entities)

        batch_inputs = tokenizer(
            sentences,
            max_length=max_len,
            padding=True,
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': batch_inputs['input_ids'],
            'attention_mask': batch_inputs['attention_mask'],
            'labels': torch.tensor(relation_labels, dtype=torch.long),
            'masks': torch.tensor(masks, dtype=torch.long)
        }

    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn)


if __name__ == '__main__':
    pretrained_model_name = 'bert-base-chinese'
    re_tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name)

    trainset_path = r'G:\python_codes\Principles_of_Computer_Construction_KG\output\[banned]\transformed_trainset.json'

    re_trainset = RelationExtractionDataset(json_filename=trainset_path)

    trainset_loader = get_dataloader(re_trainset, re_tokenizer, batch_size=1, shuffle=False)

    for i, batch in enumerate(trainset_loader):
        if i == 2:
            print(batch['input_ids'])
            print("Label: ", batch['labels'])
            print(batch['labels'].shape)
            print("Mask: ", batch['masks'])
            print(batch['masks'].shape)
            break
