# backend/app/ai_blog.py
from __future__ import annotations
import os, re
from datetime import date
from pathlib import Path
from openai import OpenAI

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_client = None

def _client_lazy() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client

def _slug(s: str) -> str:
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"[^\w\-가-힣]", "", s)  # 파일명 안전
    return s[:60] or "post"

def write_post_md(keyword: str, today: date) -> str:
    """
    키워드 기준으로 블로그 글을 생성하고 /app/generated/에 저장.
    이미 오늘 생성된 동일 키워드 파일이 있으면 그대로 경로만 리턴.
    returns: 파일 경로 문자열
    """
    out_dir = Path("./generated")
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{today.strftime('%Y%m%d')}-{_slug(keyword)}.txt"
    fpath = out_dir / fname
    if fpath.exists():
        return str(fpath)

    prompt = f"""
    You are a strict DSL formatter. Output must use DSL only. Do NOT use Markdown, HTML, code blocks, backticks, links, or image syntax.

    [DSL Rules]
    - Allowed tags: [title][/title], [bold][/bold], [underline][/underline], [italic][/italic], [align=center]...[/align], [separator=LINE][/separator], [quote=TEXT], [img=INDEXES layout=collage][/img]
    - Tags must be properly closed, no unnecessary spaces or blank lines

    [Parameter Rules]
    - For [separator=LINE], LINE must be exactly one of: line1, line2, line3, line4, line5, line6, line7. Never output the literal "line1~7". If uncertain, use line3.
    - For [img=INDEXES layout=collage], INDEXES must be comma-separated integers such as "1,2" or "4,5". Use at most two images; omit the tag entirely if not needed.

    [Writing Rules]
    - Keyword: "{keyword}"
    - Length: 1200–1600 characters
    - Tone: professional but friendly, in polite Korean
    - Structure: Introduction → Main body (3–5 subheadings, 2–3 paragraphs each) → Checklist/Summary → Conclusion
    - SEO: include keyword naturally in the first paragraph and subheadings
    - Title uses [title], subheadings use [bold]
    - Use [underline], [italic], [quote] as needed
    - Use [separator] for visual breaks
    - [img] can be used 0–2 times

    [Extra]
    - The blog article must be written in Korean DSL.
    """
    client = _client_lazy()
    resp = client.responses.create(model=MODEL, input=prompt, temperature=0.4)
    md = resp.output_text.strip()
    fpath.write_text(md, encoding="utf-8")
    return str(fpath)