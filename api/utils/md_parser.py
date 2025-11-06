# api/utils/md_parser.py
from pathlib import Path
from .file_ops import read_text_file, write_text_file, write_json_block_to_md, read_json_block_from_md, ensure_dir
from typing import Tuple, List
import re


def read_people_md(path: Path) -> Tuple[List[dict], List[str]]:
    """
    Returns (people_list, categories_list).
    people_list is read from PEOPLE_DATA block; categories_list is read from '## Categories' section.
    """
    txt = read_text_file(path)
    categories = []
    people = []
    if not txt:
        return [], []
    # parse categories under '## Categories' header as markdown list items
    m = re.search(r"##\s+Categories\s*(.*?)\n##", txt, flags=re.S)
    if not m:
        # try until EOF
        m2 = re.search(r"##\s+Categories\s*(.*)", txt, flags=re.S)
        block = m2.group(1) if m2 else ""
    else:
        block = m.group(1)
    # extract lines that look like markdown list items
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- "):
            categories.append(line[2:].strip())
        elif line.startswith("* "):
            categories.append(line[2:].strip())
    # read people JSON block
    people = read_json_block_from_md(path, marker="PEOPLE_DATA")
    return people, categories


def write_people_md(path: Path, people: List[dict], categories: List[str]):
    ensure_dir(path.parent)
    header = "# People\n\n## Categories\n\n"
    for c in categories:
        header += f"- {c}\n"
    header += "\n## Directory\n\n"
    write_json_block_to_md(path, people, marker="PEOPLE_DATA", header=header)


def read_categories_from_people_md(path: Path) -> List[str]:
    _, cats = read_people_md(path)
    return cats


def ensure_category_in_md(path: Path, category: str):
    people, cats = read_people_md(path)
    if category in cats:
        return
    cats.append(category)
    write_people_md(path, people, cats)
