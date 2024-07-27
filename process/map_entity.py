import json


with open('output/entity.json', 'r', encoding='utf-8') as f:
    entity_list = json.loads(f.read())


print(entity_list[:50])



