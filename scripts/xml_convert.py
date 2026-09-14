"""helper for parsing PubMed XML"""
import xml.etree.ElementTree as ET
from pathlib import Path
from sys import argv
from typing import Tuple

def parse_xml(xml_pth:str)->Tuple[str, str]:
    path = Path(xml_pth)
    tree = ET.parse(path.as_posix())
    title_path = ".//ArticleTitle"
    title_nodes = tree.findall(title_path)
    if title_nodes is not None:
        title_texts = [x.text for x in title_nodes]
        title = " ".join([x.strip() for x in title_texts if x is not None])
    else:
        title = "" 
    abstract_path = ".//AbstractText"
    abstract_nodes = tree.findall(abstract_path)
    if abstract_nodes is not None:
        abstract_texts = [x.text for x in abstract_nodes]
        abstract = " ".join([x.strip() for x in abstract_texts if x is not None])
    else:
        abstract = ""
    if len(title) == 0:
        print(f"{xml_pth} has no title")
    if len(abstract) == 0:
        print(f"{xml_pth} has not abstract")
    return title, abstract
if __name__ == "__main__":
    title_text, abstract_text = parse_xml(argv[1])
    print(f"Title: {title_text}")
    print(f"Abstract: {abstract_text}")
            





