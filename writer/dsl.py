from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List

TITLE_RE = re.compile(r"\[title\](.*?)\[/title\]", re.S | re.I)
IMG_RE = re.compile(r"\[img=(?P<idxs>\d+(?:\s*,\s*\d+)*)\s+layout=(?P<layout>\w+)\]\s*\[/img\]", re.I)
SEP_RE = re.compile(r"\[separator=(line[1-7])\]\s*\[/separator\]", re.I)

def extract_title(dsl: str):
    m = TITLE_RE.search(dsl)
    if not m:
        return None, dsl
    title = m.group(1).strip()
    body = dsl[:m.start()] + dsl[m.end():]
    return title, body

@dataclass
class ImageBlock:
    indexes: List[int]
    layout: str

def extract_images(dsl: str):
    imgs: List[ImageBlock] = []
    def repl(m: re.Match) -> str:
        idxs = [int(x.strip()) for x in m.group("idxs").split(",")]
        layout = m.group("layout").strip().lower()
        imgs.append(ImageBlock(indexes=idxs, layout=layout))
        return ""
    body = IMG_RE.sub(repl, dsl)
    return imgs, body

def to_html(dsl_body: str) -> str:
    def align_repl(m: re.Match) -> str:
        inner = m.group(1)
        return f'<div style="text-align:center">{inner}</div>'
    dsl_body = re.sub(r"\[align=center\](.*?)\[/align\]", align_repl, dsl_body, flags=re.S|re.I)

    dsl_body = re.sub(r"\[bold\](.*?)\[/bold\]", r"<strong>\1</strong>", dsl_body, flags=re.S|re.I)
    dsl_body = re.sub(r"\[underline\](.*?)\[/underline\]", r"<u>\1</u>", dsl_body, flags=re.S|re.I)
    dsl_body = re.sub(r"\[italic\](.*?)\[/italic\]", r"<em>\1</em>", dsl_body, flags=re.S|re.I)

    def sep_repl(m: re.Match) -> str:
        style = m.group(1).lower()
        return f'<hr data-style="{style}"/>'
    dsl_body = SEP_RE.sub(sep_repl, dsl_body)

    html = dsl_body.strip()
    parts = [p.strip() for p in re.split(r"\n\s*\n", html) if p.strip()]
    html = "".join(f"<p>{p}</p>" for p in parts)
    return html