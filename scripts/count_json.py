import json 
import sys
from pathlib import Path

def get_json_statements(pth:Path):
    """helper function for counting statements"""
    with open(pth.as_posix()) as f:
        jsn = json.loads(f.read())
    parents = pth.parent.as_posix()
    parts = pth.parts
    ## PubMed was not batched so just call that batch 1 ## 
    batch = parts[2].removeprefix("batch_") if len(parts) > 3 else '1'
    src = parts[1]

    print(f"{src},{batch},{len(jsn)}")

if __name__ == "__main__":
    pth = sys.argv[1]
    get_json_statements(Path(pth))
