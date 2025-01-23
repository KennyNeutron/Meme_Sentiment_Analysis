# Create a tensor and move it to the GPU
import torch
from torch import rand

# Define the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

x = torch.rand(3, 3)
x_gpu = x.to(device)

print("Tensor on GPU:")
print(x_gpu)
