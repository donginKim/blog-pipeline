from typing import List, Dict, Any

def print_result(keyword: str, results: List[Dict[str, Any]]):
    print(f"\n===== 🔍 [{keyword}] 검색 결과 =====\n")
    if not results:
        print("(검색 결과가 없습니다.)")
        return
    for i, item in enumerate(results, start=1):
        print(f"{i}. [섹션] {item['span']}")
        for box in item["article_boxes"]:
            print(f"[ {box['box_index']} 위] ")
            for link in box["links"]:
                print(f"    - 링크: {link['href']}")
                print(f"    - 텍스트: {link['text']}")
    print(f"\n===== ✅ [{keyword}] 완료 =====\n")

def find_specific_blog(results: List[Dict[str, Any]], blog_url: str):
    found = False
    for result in results:
        span = result["span"]
        for box in result["article_boxes"]:
            box_index = box["box_index"]
            for link in box["links"]:
                if link["href"].strip() == blog_url:
                    print(f"✅ 블로그 [{blog_url}] 발견됨")
                    print(f"   [SPAN] {span}")
                    print(f"   [BOX #{box_index}]\n")
                    found = True
    if not found:
        print(f"❌ 블로그 [{blog_url}] 발견되지 않음\n")
