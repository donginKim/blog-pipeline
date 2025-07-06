# parser.py

import re

def parse_post_file(file_path: str):
    """txt파일에서 제목과 본문을 분리하여 반환"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 제목 추출
    title_match = re.search(r"\[title\](.*?)\[/title\]", content, re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""

    # 본문 추출
    body = re.sub(r"\[title\].*?\[/title\]", "", content, flags=re.DOTALL).strip()
    body = body.replace("\n", "[br][/br]")

    return title, body