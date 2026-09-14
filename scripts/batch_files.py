"""
helper function for batching txt files
"""
from pathlib import Path 
from tqdm import tqdm
from sys import argv

SOURCES = ['pmc', 'not_pmc']
PROCESSED_DATA_PATH = Path("data/processed_data")

def batch_files(source:str, batch_size:int,):
    batch_num = 0
    source_base:Path = PROCESSED_DATA_PATH.joinpath(source)
    base_files = [x for x in source_base.iterdir() if x.is_file()]
    current_batch = base_files[batch_num * batch_size : (batch_num + 1) * batch_size ]
    while len(current_batch) > 0:
        batch_dir = source_base.joinpath(f"batch_{batch_num+1}")
        batch_dir.mkdir(parents=True, exist_ok=True)
        for f in current_batch:
            f.rename(batch_dir.joinpath(f.name))
        batch_num += 1
        current_batch = base_files[batch_num * batch_size : (batch_num + 1) * batch_size ]
if __name__ == "__main__":
    batch_size = int(argv[1])
    for source in tqdm(SOURCES, desc="Batching files"):
        batch_files(source=source, batch_size=batch_size)

        
