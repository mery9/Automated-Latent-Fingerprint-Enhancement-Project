import torch

if torch.cuda.is_available():
    print("CUDA is available")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA is not available")