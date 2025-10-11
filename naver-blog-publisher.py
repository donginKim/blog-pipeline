#!/usr/bin/env python3
"""
네이버 블로그 자동 발행 시스템
- 생성된 DSL 콘텐츠를 네이버 블로그 API로 발행
"""
import os
import sys
import json
from typing import Optional, Dict
import httpx
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 설정
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from sqlalchemy import create_engine, text

DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)


class NaverBlogPublisher:
    """네이버 블로그 발행 클래스"""
    
    def __init__(self):
        self.client_id = os.getenv("NAVER_CLIENT_ID", "")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
        self.access_token = os.getenv("NAVER_ACCESS_TOKEN", "")
        self.blog_id = os.getenv("NAVER_BLOG_ID", "")
        
        if not all([self.client_id, self.client_secret]):
            print("⚠️ 네이버 API 설정이 없습니다.")
            print("   NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 설정 필요")
    
    async def publish_post(
        self,
        title: str,
        content: str,
        category: str = "",
        tags: list = None
    ) -> Optional[Dict]:
        """
        네이버 블로그에 글 발행
        
        Args:
            title: 글 제목 (DSL 형식: [title]...[/title])
            content: 글 본문 (DSL 형식)
            category: 카테고리 (선택사항)
            tags: 태그 목록 (선택사항)
            
        Returns:
            발행 결과 정보
        """
        try:
            # DSL 제목에서 태그 제거
            clean_title = self._clean_dsl_tags(title)
            
            # 네이버 블로그 API 호출
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 네이버 블로그 글쓰기 API
                # 참고: 네이버는 공식 블로그 작성 API를 제공하지 않습니다.
                # 대신 스마트에디터 형식을 사용하여 웹 인터페이스로 발행해야 합니다.
                
                # 임시: 로컬에 저장하고 수동 발행을 위한 정보 반환
                result = {
                    "status": "prepared",
                    "title": clean_title,
                    "content": content,
                    "category": category,
                    "tags": tags or [],
                    "message": "네이버 블로그는 공식 작성 API가 없어 수동 발행이 필요합니다."
                }
                
                print(f"📝 발행 준비 완료: {clean_title}")
                print(f"   카테고리: {category or '미분류'}")
                print(f"   태그: {', '.join(tags or [])}")
                
                return result
                
        except Exception as e:
            print(f"❌ 발행 실패: {e}")
            return None
    
    def _clean_dsl_tags(self, text: str) -> str:
        """DSL 태그 제거"""
        import re
        # [title]...[/title] 형식에서 태그만 제거
        text = re.sub(r'\[title\](.*?)\[/title\]', r'\1', text)
        text = re.sub(r'\[bold\](.*?)\[/bold\]', r'\1', text)
        text = re.sub(r'\[underline\](.*?)\[/underline\]', r'\1', text)
        text = re.sub(r'\[italic\](.*?)\[/italic\]', r'\1', text)
        text = re.sub(r'\[separator=.*?\]\[/separator\]', '', text)
        text = re.sub(r'\[quote=(.*?)\]', r'\1', text)
        text = re.sub(r'\[align=.*?\](.*?)\[/align\]', r'\1', text)
        text = re.sub(r'\[img=.*?\]\[/img\]', '', text)
        return text.strip()
    
    def save_to_html(
        self,
        post_id: int,
        title: str,
        content: str,
        output_dir: str = "blog_posts"
    ) -> str:
        """
        DSL 콘텐츠를 HTML로 변환하여 저장
        네이버 블로그 스마트에디터에 붙여넣을 수 있는 형식
        
        Args:
            post_id: 글 ID
            title: 제목
            content: DSL 본문
            output_dir: 저장 디렉토리
            
        Returns:
            저장된 파일 경로
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # DSL을 HTML로 변환
        html_content = self._dsl_to_html(content)
        
        # HTML 파일 생성
        html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._clean_dsl_tags(title)}</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #000;
        }}
        h2 {{
            font-size: 22px;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 15px;
            color: #333;
        }}
        .underline {{
            text-decoration: underline;
            color: #0066cc;
        }}
        .italic {{
            font-style: italic;
            color: #666;
        }}
        .quote {{
            background: #f8f9fa;
            border-left: 4px solid #0066cc;
            padding: 15px 20px;
            margin: 20px 0;
            font-weight: 500;
        }}
        .separator {{
            border: 0;
            height: 1px;
            background: #ddd;
            margin: 30px 0;
        }}
        .center {{
            text-align: center;
        }}
        p {{
            margin: 15px 0;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # 파일 저장
        filename = f"{output_dir}/post_{post_id}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✅ HTML 파일 저장: {filename}")
        return filename
    
    def _dsl_to_html(self, dsl_content: str) -> str:
        """DSL을 HTML로 변환"""
        import re
        
        html = dsl_content
        
        # [title]...[/title]
        html = re.sub(r'\[title\](.*?)\[/title\]', r'<h1>\1</h1>', html)
        
        # [bold]...[/bold]
        html = re.sub(r'\[bold\](.*?)\[/bold\]', r'<h2>\1</h2>', html)
        
        # [underline]...[/underline]
        html = re.sub(r'\[underline\](.*?)\[/underline\]', r'<span class="underline">\1</span>', html)
        
        # [italic]...[/italic]
        html = re.sub(r'\[italic\](.*?)\[/italic\]', r'<span class="italic">\1</span>', html)
        
        # [separator=...]
        html = re.sub(r'\[separator=.*?\]\[/separator\]', '<hr class="separator">', html)
        
        # [quote=...]
        html = re.sub(r'\[quote=(.*?)\]', r'<div class="quote">\1</div>', html)
        
        # [align=center]...[/align]
        html = re.sub(r'\[align=center\](.*?)\[/align\]', r'<div class="center">\1</div>', html)
        
        # [img=...] (이미지는 제거 또는 placeholder)
        html = re.sub(r'\[img=.*?\]\[/img\]', '', html)
        
        # 줄바꿈을 <p> 태그로
        paragraphs = html.split('\n\n')
        html = ''.join([f'<p>{p.strip()}</p>' if p.strip() and not p.strip().startswith('<') else p for p in paragraphs])
        
        return html


class NaverBlogAutoPublisher:
    """자동 발행 시스템"""
    
    def __init__(self):
        self.publisher = NaverBlogPublisher()
        self.engine = engine
    
    def publish_generated_post(self, post_id: int) -> bool:
        """
        생성된 글을 네이버 블로그에 발행
        
        Args:
            post_id: generated_posts 테이블의 글 ID
            
        Returns:
            발행 성공 여부
        """
        try:
            with self.engine.connect() as conn:
                # 생성된 글 조회
                result = conn.execute(
                    text("""
                        SELECT gp.id, gp.title, gp.content, gp.summary, gp.tags, 
                               k.keyword
                        FROM generated_posts gp
                        JOIN keywords k ON gp.keyword_id = k.id
                        WHERE gp.id = :post_id AND gp.status = 'generated'
                    """),
                    {"post_id": post_id}
                )
                
                row = result.fetchone()
                if not row:
                    print(f"❌ 글을 찾을 수 없거나 이미 발행되었습니다: {post_id}")
                    return False
                
                post_id, title, content, summary, tags_json, keyword = row
                
                # 태그 파싱
                import json
                tags = json.loads(tags_json) if tags_json else []
                
                print(f"📝 발행 준비: {self.publisher._clean_dsl_tags(title)}")
                
                # HTML 파일로 저장
                html_file = self.publisher.save_to_html(
                    post_id=post_id,
                    title=title,
                    content=content
                )
                
                # DSL 원본도 저장
                dsl_file = html_file.replace('.html', '_dsl.txt')
                with open(dsl_file, 'w', encoding='utf-8') as f:
                    f.write(f"제목:\n{title}\n\n")
                    f.write(f"본문:\n{content}\n\n")
                    f.write(f"요약:\n{summary}\n\n")
                    f.write(f"태그:\n{', '.join(tags)}\n")
                
                print(f"✅ DSL 파일 저장: {dsl_file}")
                
                # 발행 상태 업데이트 (준비 완료)
                conn.execute(
                    text("""
                        UPDATE generated_posts 
                        SET status = 'ready_to_publish'
                        WHERE id = :post_id
                    """),
                    {"post_id": post_id}
                )
                conn.commit()
                
                print(f"✅ 발행 준비 완료!")
                print(f"   HTML: {html_file}")
                print(f"   DSL: {dsl_file}")
                print("")
                print("📋 다음 단계:")
                print("   1. 네이버 블로그 접속")
                print("   2. 글쓰기 → 스마트에디터")
                print(f"   3. HTML 모드로 전환 후 {html_file} 내용 붙여넣기")
                print("   4. 또는 일반 모드에서 DSL 파일 내용 직접 입력")
                
                return True
                
        except Exception as e:
            print(f"❌ 발행 준비 실패: {e}")
            return False
    
    def list_ready_posts(self) -> list:
        """발행 대기 중인 글 목록"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT gp.id, gp.title, gp.created_at, k.keyword, gp.status
                    FROM generated_posts gp
                    JOIN keywords k ON gp.keyword_id = k.id
                    WHERE gp.status IN ('generated', 'ready_to_publish')
                    ORDER BY gp.created_at DESC
                """)
            )
            
            posts = []
            for row in result:
                posts.append({
                    "id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "keyword": row[3],
                    "status": row[4]
                })
            
            return posts
    
    def mark_as_published(self, post_id: int, blog_url: str = "") -> bool:
        """발행 완료로 표시"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        UPDATE generated_posts 
                        SET status = 'published', published_at = CURRENT_TIMESTAMP
                        WHERE id = :post_id
                    """),
                    {"post_id": post_id}
                )
                conn.commit()
                
                print(f"✅ 발행 완료로 표시: {post_id}")
                if blog_url:
                    print(f"   URL: {blog_url}")
                
                return True
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            return False


def main():
    """메인 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description="네이버 블로그 자동 발행")
    parser.add_argument("--list", action="store_true", help="발행 대기 글 목록")
    parser.add_argument("--publish", type=int, metavar="POST_ID", help="글 발행 준비")
    parser.add_argument("--mark-published", type=int, metavar="POST_ID", help="발행 완료 표시")
    parser.add_argument("--url", type=str, help="발행된 블로그 URL")
    
    args = parser.parse_args()
    
    publisher = NaverBlogAutoPublisher()
    
    if args.list:
        # 발행 대기 글 목록
        posts = publisher.list_ready_posts()
        
        if not posts:
            print("📝 발행 대기 중인 글이 없습니다.")
            return
        
        print("\n📋 발행 대기 글 목록")
        print("=" * 80)
        for post in posts:
            clean_title = publisher.publisher._clean_dsl_tags(post["title"])
            status_emoji = "✅" if post["status"] == "ready_to_publish" else "⏳"
            print(f"{status_emoji} ID: {post['id']:3d} | {post['keyword']:15s} | {clean_title[:40]}")
            print(f"        생성: {post['created_at']} | 상태: {post['status']}")
            print("-" * 80)
        
    elif args.publish:
        # 글 발행 준비
        publisher.publish_generated_post(args.publish)
        
    elif args.mark_published:
        # 발행 완료 표시
        publisher.mark_as_published(args.mark_published, args.url or "")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

