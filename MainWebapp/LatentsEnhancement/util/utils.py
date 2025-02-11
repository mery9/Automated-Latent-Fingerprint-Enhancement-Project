import os
import sys
import logging
import subprocess
import numpy as np


def get_gpus_memory_info():
    try:
        result = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'], encoding='utf-8')
        memory_available = []
        for line in result.strip().split('\n'):
            try:
                memory_available.append(int(line))
            except ValueError:
                memory_available.append(0)  # Handle 'N/A' or other non-integer values
        device_id = memory_available.index(max(memory_available))
        return device_id, memory_available
    except Exception as e:
        print(f"Error getting GPU memory info: {e}")
        return 0, [0]

def calc_parameters_count(model):
    return np.sum(np.prod(v.size()) for v in model.parameters())/1e6

def get_logger(log_dir):
    create_exp_dir(log_dir)
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format=log_format, datefmt='%m/%d %I:%M:%S %p')
    fh = logging.FileHandler(os.path.join(log_dir, 'run.log'))
    fh.setFormatter(logging.Formatter(log_format))
    logger = logging.getLogger('Nas Seg')
    logger.addHandler(fh)
    return logger

def create_exp_dir(path, desc='Experiment dir: {}'):
    if not os.path.exists(path):
        os.makedirs(path)
    print(desc.format(path))
