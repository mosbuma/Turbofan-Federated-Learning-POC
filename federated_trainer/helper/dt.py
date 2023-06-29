import torch
import torch.nn as nn

class DecisionTree(nn.Module):
    def __init__(self, input_size):
        super(DecisionTree, self).__init__()
        self.fc = nn.Linear(input_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.fc(x)
        out = self.sigmoid(out)
        return out
    
def get_decision_tree_weights(model):
    weights = model.fc.weight.data.squeeze()
    biases = model.fc.bias.data.squeeze()
    return weights, biases

def split_tensor_evenly(tensor, num_chunks):
    total_size = tensor.size(0)
    chunk_size = total_size // num_chunks
    remainder = total_size % num_chunks

    chunks = []
    start = 0
    for i in range(num_chunks):
        # Calculate the chunk size, accounting for any remainder
        size = chunk_size + (1 if i < remainder else 0)
        # Slice the tensor and add it to the list of chunks
        chunks.append(tensor[start:start + size])
        start += size

    return chunks