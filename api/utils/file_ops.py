# api/utils/file_ops.py
from pathlib import Path
import json
from typing import List, Any
from datetime import datetime
import os


def ensure_dir(p: Path):
    p = Path(p)
    if p.is_file():
        p.parent.mkdir(parents=True, exist_ok=True)
    else:
        p.mkdir(parents=True, exist_ok=True)


def read_text_file(path: Path) -> str:
    path = Path(path)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text_file(path: Path, content: str):
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")

# JSON-block-in-MD format helpers. We store a single JSON array between markers:
# <!--DATA_START-->
# <json array>
# <!--DATA_END-->


def _wrap_marker(marker: str):
    start = f"<!--{marker}_START-->"
    end = f"<!--{marker}_END-->"
    return start, end


def read_json_block_from_md(path: Path, marker: str = "DATA") -> List[Any]:
    path = Path(path)
    if not path.exists():
        return []
    txt = path.read_text(encoding="utf-8")
    start_marker, end_marker = _wrap_marker(marker)
    if start_marker in txt and end_marker in txt:
        start = txt.index(start_marker) + len(start_marker)
        end = txt.index(end_marker)
        raw = txt[start:end].strip()
        try:
            return json.loads(raw)
        except Exception:
            # graceful fallback: try lines of json objects
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            objs = []
            for line in lines:
                try:
                    objs.append(json.loads(line))
                except Exception:
                    continue
            return objs
    else:
        return []


def write_json_block_to_md(path: Path, data: list, marker: str = "DATA", header: str = "", footer: str = ""):
    ensure_dir(path.parent)
    start_marker, end_marker = _wrap_marker(marker)
    body = json.dumps(data, indent=2, default=str)
    if path.exists():
        txt = path.read_text(encoding="utf-8")
        if start_marker in txt and end_marker in txt:
            pre = txt[:txt.index(start_marker)]
            post = txt[txt.index(end_marker) + len(end_marker):]
            new = pre + start_marker + "\n" + body + "\n" + end_marker + post
        else:
            new = (header or "") + "\n" + start_marker + "\n" + \
                body + "\n" + end_marker + "\n" + (footer or "")
    else:
        new = (header or "") + "\n" + start_marker + "\n" + \
            body + "\n" + end_marker + "\n" + (footer or "")
    path.write_text(new, encoding="utf-8")


def remove_item_from_json_md(path: Path, marker: str, predicate):
    arr = read_json_block_from_md(path, marker=marker)
    new = [x for x in arr if not predicate(x)]
    write_json_block_to_md(path, new, marker=marker)
    return new


def timestamped_filename(base: str, ext: str = "md"):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe = f"{base}_{ts}.{ext}"
    return safe
