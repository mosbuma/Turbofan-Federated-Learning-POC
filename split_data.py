import pandas as pd
import numpy as np

path = '/Users/stanislavstefanov/Documents/repos/KLM/Test_Federated/CMaps/train_FD001.txt'

jet_data = pd.read_csv(path, sep=" ", header=None)
jet_data = jet_data.iloc[:, :-2]
print(jet_data)

split_data = np.array_split(jet_data, 3)

for i, n in enumerate(split_data):
    print(n)
    filename = f"node_dataset_{i}"
    np.savetxt(filename, n, newline="\n", fmt='%.4f')