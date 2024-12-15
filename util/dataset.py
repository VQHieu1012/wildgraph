import torch
from torch.utils.data import Dataset, DataLoader

import h3

from sklearn.preprocessing import LabelEncoder
import geopandas as gpd
import numpy as np
from scipy.spatial.distance import pdist

class TrajDataset(Dataset):
    def __init__(self, df, sample_size, seq_length, is_tokenize_special_chars=False, distance=0.25, ablate_is_fixed_zoom=False, fixed_zoom_value=2):
        self.tokenizer = LabelEncoder()
        x, y, pos, sentences = self.load_data(df, sample_size, seq_length, is_tokenize_special_chars, distance, ablate_is_fixed_zoom, fixed_zoom_value)
        self.x = torch.tensor(x, dtype=torch.long)
        self.y = torch.tensor(y, dtype=torch.long)
        self.pos = torch.tensor(pos, dtype=torch.long)
        self.sentences = [int(x) for x in sentences]
        
    def size(self):
        return len(self.tokenizer.classes_)
    
    def __len__(self):
        return len(self.x)
    
    def __getitem__(self, index):
        return self.x[index], self.y[index], self.pos[index]
    
    def load_data(self, df, sample_size, seq_length, is_tokenize_special_chars, distance, ablate_is_fixed_zoom=False, fixed_zoom_value=2):
        init_resolution = 2
        if ablate_is_fixed_zoom:
            init_resolution = fixed_zoom_value
        
        # Update to use `geo_to_h3`
        df['h3_address'] = df.apply(lambda row: h3.geo_to_h3(row['location.lat'], row['location.long'], init_resolution), axis=1)

        def get_distance_split_targets(dfi, dist): 
            value_counts = dfi['h3_address'].value_counts()
            dup_list = value_counts[value_counts > 1].index.tolist()
            dup_list_filtered = []
            for h3_address in dup_list:
                dfii = dfi[dfi['h3_address'] == h3_address]
                distances = pdist(dfii[['location.lat', 'location.long']], metric='euclidean')
                d = max(distances)
                if d > dist:
                    dup_list_filtered.append(h3_address)
            return dup_list_filtered

        def granulate(row, resolution, dup_list):
            # Granulate H3 addresses if needed
            if row['h3_address'] in dup_list:
                return h3.geo_to_h3(row['location.lat'], row['location.long'], resolution)
            else:
                return row['h3_address']

        if not ablate_is_fixed_zoom:
            for zoom in range(3, 8):
                dup_list = get_distance_split_targets(df, distance)
                df['h3_address'] = df.apply(lambda row: granulate(row, zoom, dup_list), axis=1)

        self.density = len(df) / df['h3_address'].nunique()
        df = df.sort_values(by=['idx', 'label'])
        df['node'] = self.tokenizer.fit_transform(df['h3_address'])
        dot, pad, sos = -1, -1, -1
        if is_tokenize_special_chars:
            self.tokenizer.classes_ = np.append(self.tokenizer.classes_, '.')
            self.tokenizer.classes_ = np.append(self.tokenizer.classes_, '<pad>')
            self.tokenizer.classes_ = np.append(self.tokenizer.classes_, '<sos>')
            [sos, dot] = self.tokenizer.transform(['<sos>', '.'])

        export = df['node'].values.reshape(sample_size, seq_length)
        export1 = np.c_[np.ones(export.shape[0]) * -1, export]
        if is_tokenize_special_chars:
            export1 = np.c_[np.ones(export.shape[0]) * sos, export]
        datafile = export1
        edges_set = set()
        transitions = []
        X, y, pos = [], [], []
        sentences = []
        for sequence in datafile:
            sentences = np.append(np.append(sentences, [int(num) for num in sequence]), dot)
            for j in range(len(sequence) - 1):
                if sequence[j] != sequence[j + 1]:
                    edges_set.add((sequence[j], sequence[j + 1]))
                X.append(sequence[j]) 
                y.append(sequence[j + 1])
                pos.append(j)
                transitions.append((sequence[j], sequence[j + 1]))
        self.vocab_dim = int(max(y) + 1)
        edges_array = np.array(list(edges_set))
        self.edge_index = torch.tensor(edges_array.T, dtype=torch.long)
        self.transitions = transitions
        return X, y, pos, sentences
