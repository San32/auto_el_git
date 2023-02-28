"""
폰트, weight 파일 등이 있는지 확인한다.
"""

# Pytorch GPU check

# Pytorch
import torch
import os

def torch_check():

    device_count = torch.cuda.device_count()
    device_name = torch.cuda.get_device_name(0)
    cuda_available = torch.cuda.is_available()

    print("###################################")
    print(f'torch check start')
    print("###################################")

    print(f'device_count : {device_count}')
    # 1
    print(f'device_name : {device_name}')
    # GeForce RTX 2080 Ti
    print(f'cuda_available : {cuda_available}')
    # True
    print("###################################")
    print(f"torch check end")
    print("###################################")

def file_exists_check():
    current_working_directory = os.getcwd()
    file_path_log = current_working_directory+'/lib/log.py'
    file_path_pt = current_working_directory+'/lib/best.pt'
    print("###################################")
    print(f'file exists {file_path_log} : {os.path.isfile(file_path_log)}' )
    print(f'file exists {file_path_pt} : {os.path.isfile(file_path_pt)}' )
    print("###################################")


torch_check()
file_exists_check()