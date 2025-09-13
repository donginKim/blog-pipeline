import os
import re
import glob
from playwright.sync_api import Frame
from smarteditor_utils.formatting import insert_formatted_text
from smarteditor_utils.quote import insert_quote
from smarteditor_utils.alignment import set_text_alignment
from smarteditor_utils.separator import insert_separator
from smarteditor_utils.image import insert_images


def parse_and_execute_dsl(frame: Frame, dsl_text: str):
    """
    DSL 텍스트를 파싱하고 명령어에 따라 스마트에디터 동작을 실행한다.
    일반 텍스트와 줄바꿈, 중첩 태그도 함께 처리된다.
    :param frame: mainFrame 객체
    :param dsl_text: DSL 문법으로 구성된 텍스트
    """
    tag_pattern = re.compile(r"\[([a-zA-Z0-9_-]+)([^\]]*)\](.*?)\[/\1\]", re.DOTALL)

    def process_segment(segment: str):
        pos = 0
        for match in tag_pattern.finditer(segment):
            if match.start() > pos:
                plain = segment[pos:match.start()]
                if plain.strip():
                    frame.page.keyboard.type(plain.strip())
                    frame.page.wait_for_timeout(200)

            tag = match.group(1)
            attr = match.group(2)
            inner = match.group(3).strip()
            attr_val = attr[1:] if attr else None

            if tag in {"bold", "italic", "underline", "strikethrough"}:
                insert_formatted_text(frame, tag, inner)
            elif tag == "quote":
                insert_quote(frame, inner)
            elif tag == "align":
                if attr_val not in {"left", "center", "right", "justify"}:
                    raise ValueError(f"정렬 값이 올바르지 않습니다: {attr_val}")
                set_text_alignment(frame, attr_val)
                process_segment(inner)
            elif tag == "separator":
                insert_separator(frame, line_type=attr_val or "default")
            elif tag == "img":
                if not attr:
                    raise ValueError("img 태그에는 이미지 파일명이 필요합니다.")

                # 속성 파싱
                attr_text = attr.strip()
                match_img = re.search(r"=([^ \]]+)", attr_text)
                match_layout = re.search(r"layout=([가-힣a-zA-Z]+)", attr_text)

                if not match_img:
                    raise ValueError("img 태그에 이미지 파일명이 없습니다.")

                image_names = [x.strip() for x in match_img.group(1).split(",")]
                layout = match_layout.group(1) if match_layout else "photo"

                image_paths = []
                for name in image_names:
                    matches = glob.glob(f"temp/{name}.*")
                    if matches:
                        image_paths.append(matches[0])
                    else:
                        print(f"[!] 이미지 파일을 찾을 수 없습니다: {name}")

                if image_paths:
                    insert_images(frame, image_paths, layout=layout)
            elif tag == "br":
                frame.page.keyboard.press("Enter")
                frame.page.wait_for_timeout(100)
            else:
                raise ValueError(f"알 수 없는 DSL 태그: [{tag}]")

            pos = match.end()

        if pos < len(segment):
            rest = segment[pos:]
            if rest.strip():
                frame.page.keyboard.type(rest.strip())
                frame.page.wait_for_timeout(200)

    process_segment(dsl_text)