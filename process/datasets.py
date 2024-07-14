from torch.utils.data import Dataset

import json


class PCCDataset(Dataset):
    def __init__(self):
        super(PCCDataset, self).__init__()
        with open("output/datasets.json", "r", encoding="utf-8") as f:
            self.datasets = json.loads(f.read())

    def __getitem__(self, index):
        return self.datasets["corpus"][index], self.datasets["labels"][index]

    def __len__(self):
        return len(self.datasets["corpus"])
