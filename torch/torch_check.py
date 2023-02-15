# Pytorch GPU check

# Pytorch
import torch

device_count = torch.cuda.device_count()
device_name = torch.cuda.get_device_name(0)
cuda_available = torch.cuda.is_available()

print("###################################")

print(f'device_count : {device_count}')
# 1

print(f'device_name : {device_name}')
# GeForce RTX 2080 Ti

print(f'cuda_available : {cuda_available}')
# True

print("###################################")