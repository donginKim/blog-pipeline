#!/usr/bin/env python3
"""
AI 블로그 자동 작성 시스템
- 크롤링 결과에 등록된 블로그가 없을 때 자동으로 블로그 글 생성
- OpenAI API를 사용한 고품질 콘텐츠 생성
"""
import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, List
import openai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 설정
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# 데이터베이스 설정
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from sqlalchemy import create_engine, text

DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'naver_monitor.db')}"
engine = create_engine(DATABASE_URL)


class BlogWriter:
    """AI 블로그 작성 클래스"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", use_mock: bool = False):
        self.model = model
        self.max_tokens = 2500
        self.temperature = 0.7
        self.use_mock = use_mock or not openai.api_key
        
    def generate_blog_post(
        self, 
        keyword: str, 
        tone: str = "professional",
        include_sections: List[str] = None
    ) -> Dict[str, str]:
        """
        블로그 글 생성
        
        Args:
            keyword: 주제 키워드
            tone: 글의 톤 (professional, friendly, technical, casual)
            include_sections: 포함할 섹션 목록
            
        Returns:
            Dict with 'title', 'content', 'summary', 'tags'
        """
        # Mock 모드 또는 API Key 없으면 테스트 데이터 생성
        if self.use_mock or not openai.api_key:
            print(f"🧪 테스트 모드: Mock 블로그 글 생성 - {keyword}")
            return self._generate_mock_post(keyword)
        
        # 기본 섹션
        if include_sections is None:
            include_sections = ["서론", "본론", "실습/예제", "마무리"]
        
        # 프롬프트 생성
        prompt = self._create_prompt(keyword, tone, include_sections)
        
        try:
            print(f"🤖 AI 블로그 글 생성 중: {keyword}")
            
            # OpenAI API 호출
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            result = self._parse_response(content)
            
            print(f"✅ 블로그 글 생성 완료: {result['title']}")
            return result
            
        except Exception as e:
            print(f"❌ 블로그 글 생성 실패: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트"""
        return """You are a strict DSL formatter and professional Korean blog writer. Output must use DSL only.

[DSL Rules]
- Allowed tags: [title][/title], [bold][/bold], [underline][/underline], [italic][/italic], [align=center]...[/align], [separator=LINE][/separator], [quote=TEXT], [img=INDEXES layout=collage][/img]
- Tags must be properly closed, no unnecessary spaces between tags
- Do NOT use Markdown, HTML, code blocks, backticks, links, or image syntax
- Write in Korean only

[Parameter Rules]
- [separator=LINE]: LINE must be exactly one of: line1, line2, line3, line4, line5, line6, line7. Never output "line1~7". Use line3 if uncertain.
- [img=INDEXES layout=collage]: INDEXES must be comma-separated integers (e.g., "1,2" or "3,4"). Use at most two images per tag.

[Writing Rules]
- Length: 1200–1600 characters (Korean characters)
- Tone: professional but friendly, polite Korean (존댓말)
- Structure: Introduction → Main body (3–5 subheadings) → Checklist/Summary → Conclusion
- SEO: include keyword naturally in first paragraph and subheadings (2–3 times total)
- Title uses [title], subheadings use [bold]
- Use [underline], [italic], [quote] for emphasis
- Use [separator] for visual breaks between sections
- [img] can be used 0–2 times (omit if not needed)

[Output Format]
Return JSON only:
{
    "title": "DSL formatted title with [title] tags",
    "content": "Full DSL formatted blog post",
    "summary": "Brief summary 100-150 characters",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}"""
    
    def _create_prompt(
        self, 
        keyword: str, 
        tone: str,
        sections: List[str]
    ) -> str:
        """사용자 프롬프트 생성"""
        tone_guide = {
            "professional": "전문적이고 신뢰감 있는 톤",
            "friendly": "친근하고 대화하듯이 편안한 톤",
            "technical": "기술적이고 상세한 설명 위주의 톤",
            "casual": "캐주얼하고 가벼운 톤"
        }
        
        section_guide = "\n".join([f"{i+1}. {section}" for i, section in enumerate(sections)])
        
        return f"""Write a blog post for this keyword: "{keyword}"

Requirements:
1. Use DSL format strictly (no Markdown)
2. Tone: {tone_guide.get(tone, tone)}
3. Start with [title]...[/title]
4. First paragraph must include keyword "{keyword}"
5. Suggested sections (use as subheadings with [bold]...[/bold]):
{section_guide}
6. Each section 2-3 paragraphs
7. Use [separator=line3] between major sections
8. Include practical tips or checklist
9. End with friendly conclusion
10. Add [quote=...] for key points (1-2 times)
11. Output as JSON with "title", "content", "summary", "tags"

Example DSL structure:
[title]매력적인 제목: {keyword} 완벽 가이드[/title]
[separator=line3][/separator]

안녕하세요! 오늘은 [underline]{keyword}[/underline]에 대해 알아보겠습니다...

[separator=line3][/separator]
[bold]1. 첫 번째 소제목[/bold]

본문 내용...

[quote=핵심 포인트를 요약]

[separator=line3][/separator]
[bold]2. 두 번째 소제목[/bold]

본문 내용...

[separator=line3][/separator]
[bold]마무리[/bold]

마무리 멘트...

Write in Korean, 1200-1600 characters."""
    
    def _generate_mock_post(self, keyword: str) -> Dict[str, str]:
        """테스트용 Mock 블로그 글 생성"""
        mock_content = f"""[title]{keyword} 완벽 가이드 - 초보자부터 실전까지[/title]
[separator=line3][/separator]

안녕하세요! 오늘은 [underline]{keyword}[/underline]에 대해 자세히 알아보는 시간을 가져보겠습니다. 이 가이드를 통해 {keyword}의 기초부터 실전까지 완벽하게 이해하실 수 있습니다.

[separator=line3][/separator]
[bold]1. {keyword}란 무엇인가요?[/bold]

{keyword}는 현대 사회에서 매우 중요한 주제입니다. 많은 분들이 {keyword}에 관심을 가지고 계시는데요, 그 이유는 실생활에 바로 적용할 수 있는 실용적인 내용이기 때문입니다.

{keyword}를 처음 접하시는 분들도 쉽게 이해하실 수 있도록 기초부터 차근차근 설명드리겠습니다.

[quote={keyword}는 단순히 배우는 것을 넘어 실제로 활용할 수 있어야 진정한 가치를 발휘합니다]

[separator=line3][/separator]
[bold]2. {keyword}의 핵심 포인트[/bold]

{keyword}를 제대로 이해하기 위해서는 다음 3가지 핵심 포인트를 알아야 합니다.

첫째, 기본 개념을 정확히 이해하는 것이 중요합니다. 기초가 탄탄해야 응용도 쉽게 할 수 있습니다.

둘째, 실전 경험이 필수적입니다. 이론만으로는 부족하며, 직접 해보면서 배우는 것이 가장 효과적입니다.

셋째, 지속적인 학습이 필요합니다. {keyword}는 계속 발전하고 있기 때문에 꾸준한 관심과 학습이 중요합니다.

[separator=line3][/separator]
[bold]3. {keyword} 시작하기[/bold]

이제 본격적으로 {keyword}를 시작해볼까요? 초보자분들도 쉽게 따라하실 수 있는 단계별 가이드를 준비했습니다.

먼저 기본적인 준비사항을 확인해보겠습니다. 필요한 도구나 지식이 있다면 미리 준비하시면 좋습니다.

그 다음으로는 간단한 예제부터 시작하는 것을 추천드립니다. 처음부터 어려운 것에 도전하기보다는 쉬운 것부터 하나씩 익혀나가시는 것이 좋습니다.

[separator=line3][/separator]
[bold]4. 실전 활용 방법[/bold]

{keyword}를 실제로 어떻게 활용할 수 있을까요? 여기 몇 가지 실전 활용 사례를 소개해드립니다.

실무에서는 이론과 다른 상황들을 많이 마주하게 됩니다. 그럴 때마다 당황하지 마시고, 기본 원칙을 떠올리며 차근차근 해결해나가시면 됩니다.

또한 다른 사람들의 경험담을 참고하는 것도 큰 도움이 됩니다. 커뮤니티나 블로그를 통해 다양한 사례를 접해보시기 바랍니다.

[separator=line3][/separator]
[bold]5. 자주 묻는 질문 (FAQ)[/bold]

Q1. {keyword}를 처음 시작하는데 어디서부터 해야 할까요?
A1. 기초 개념부터 차근차근 시작하시는 것을 추천드립니다.

Q2. 얼마나 시간이 걸릴까요?
A2. 개인차가 있지만, 꾸준히 하시면 3-6개월 정도면 기본은 익히실 수 있습니다.

Q3. 혼자서도 가능한가요?
A3. 네, 충분히 가능합니다. 다만 커뮤니티나 스터디 그룹을 활용하시면 더 효과적입니다.

[separator=line3][/separator]
[bold]마무리[/bold]

지금까지 {keyword}에 대해 알아보았습니다. 이 가이드가 {keyword}를 시작하시는 분들에게 도움이 되었으면 좋겠습니다.

중요한 것은 [italic]꾸준함[/italic]입니다. 조금씩이라도 매일 실천하다 보면 어느새 큰 발전을 이루실 수 있을 것입니다.

여러분의 {keyword} 여정을 응원합니다! 화이팅! 💪"""

        return {
            "title": f"[title]{keyword} 완벽 가이드 - 초보자부터 실전까지[/title]",
            "content": mock_content,
            "summary": f"{keyword}에 대한 초보자를 위한 완벽한 가이드입니다. 기초 개념부터 실전 활용까지 단계별로 자세히 설명합니다.",
            "tags": [keyword, "가이드", "초보자", "완벽정리", "실전활용"]
        }
    
    def _parse_response(self, content: str) -> Dict[str, str]:
        """AI 응답 파싱"""
        try:
            # JSON 파싱 시도
            if "```json" in content:
                # 코드 블록에서 JSON 추출
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                # 일반 코드 블록에서 JSON 추출
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content.strip()
            
            result = json.loads(json_str)
            
            # 필수 필드 확인
            required_fields = ["title", "content", "summary", "tags"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"필수 필드 누락: {field}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 실패, 원본 텍스트 사용: {e}")
            # JSON 파싱 실패 시 원본 텍스트 사용
            return {
                "title": f"{content[:50]}...",
                "content": content,
                "summary": content[:150],
                "tags": []
            }


class AutoBlogWriter:
    """자동 블로그 작성 시스템"""
    
    def __init__(self):
        self.writer = BlogWriter()
        self.engine = engine
    
    def check_and_write(self, keyword_id: int, crawl_run_id: int) -> Optional[Dict]:
        """
        크롤링 결과 확인 후 자동 글 작성
        
        Args:
            keyword_id: 키워드 ID
            crawl_run_id: 크롤링 실행 ID
            
        Returns:
            생성된 글 정보 또는 None
        """
        with self.engine.connect() as conn:
            # 키워드 정보 가져오기
            keyword_result = conn.execute(
                text("SELECT keyword FROM keywords WHERE id = :keyword_id"),
                {"keyword_id": keyword_id}
            )
            keyword_row = keyword_result.fetchone()
            if not keyword_row:
                print(f"❌ 키워드를 찾을 수 없습니다: {keyword_id}")
                return None
            
            keyword = keyword_row[0]
            
            # 등록된 타겟 블로그 URL 패턴 가져오기
            targets_result = conn.execute(
                text("""
                    SELECT b.url_pattern 
                    FROM keyword_targets kt
                    JOIN blogs b ON kt.blog_id = b.id
                    WHERE kt.keyword_id = :keyword_id AND kt.is_active = 1
                """),
                {"keyword_id": keyword_id}
            )
            target_patterns = [row[0] for row in targets_result.fetchall()]
            
            if not target_patterns:
                print(f"ℹ️ 등록된 타겟 블로그가 없습니다: {keyword}")
                return None
            
            # 크롤링 결과에서 타겟 블로그 확인
            results = conn.execute(
                text("""
                    SELECT url 
                    FROM crawl_results 
                    WHERE crawl_run_id = :crawl_run_id
                """),
                {"crawl_run_id": crawl_run_id}
            )
            
            found_target = False
            for result in results:
                url = result[0]
                for pattern in target_patterns:
                    if pattern in url:
                        found_target = True
                        break
                if found_target:
                    break
            
            if found_target:
                print(f"✅ 타겟 블로그가 검색 결과에 있습니다: {keyword}")
                return None
            
            # 타겟 블로그가 없으면 자동 글 작성
            print(f"⚠️ 타겟 블로그가 검색 결과에 없습니다!")
            print(f"🤖 자동 블로그 글 작성 시작: {keyword}")
            
            try:
                # AI 블로그 글 생성
                blog_post = self.writer.generate_blog_post(
                    keyword=keyword,
                    tone="professional",
                    include_sections=["서론", "주요 내용", "실습 예제", "마무리"]
                )
                
                # 생성된 글 저장
                self._save_generated_post(
                    keyword_id=keyword_id,
                    crawl_run_id=crawl_run_id,
                    post_data=blog_post
                )
                
                print(f"✅ 블로그 글 생성 및 저장 완료!")
                return blog_post
                
            except Exception as e:
                print(f"❌ 블로그 글 생성 실패: {e}")
                
                # 실패 기록
                conn.execute(
                    text("""
                        INSERT INTO generated_posts 
                        (keyword_id, crawl_run_id, status, error_message, created_at)
                        VALUES (:keyword_id, :crawl_run_id, 'failed', :error, CURRENT_TIMESTAMP)
                    """),
                    {
                        "keyword_id": keyword_id,
                        "crawl_run_id": crawl_run_id,
                        "error": str(e)
                    }
                )
                conn.commit()
                
                return None
    
    def _save_generated_post(
        self, 
        keyword_id: int, 
        crawl_run_id: int,
        post_data: Dict
    ):
        """생성된 글 저장"""
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO generated_posts 
                    (keyword_id, crawl_run_id, title, content, summary, tags, status, created_at)
                    VALUES 
                    (:keyword_id, :crawl_run_id, :title, :content, :summary, :tags, 'generated', CURRENT_TIMESTAMP)
                """),
                {
                    "keyword_id": keyword_id,
                    "crawl_run_id": crawl_run_id,
                    "title": post_data["title"],
                    "content": post_data["content"],
                    "summary": post_data["summary"],
                    "tags": json.dumps(post_data["tags"], ensure_ascii=False)
                }
            )
            conn.commit()


def main():
    """테스트 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI 블로그 자동 작성")
    parser.add_argument("--keyword", type=str, help="테스트 키워드")
    parser.add_argument("--keyword-id", type=int, help="키워드 ID")
    parser.add_argument("--crawl-run-id", type=int, help="크롤링 실행 ID")
    
    args = parser.parse_args()
    
    if args.keyword:
        # 단순 테스트: 키워드로 글 생성
        writer = BlogWriter()
        result = writer.generate_blog_post(args.keyword)
        
        print("\n" + "="*60)
        print(f"📝 제목: {result['title']}")
        print(f"📋 요약: {result['summary']}")
        print(f"🏷️ 태그: {', '.join(result['tags'])}")
        print("="*60)
        print("\n📄 본문:")
        print(result['content'])
        print("="*60)
        
    elif args.keyword_id and args.crawl_run_id:
        # 자동 블로그 작성 시스템 실행
        auto_writer = AutoBlogWriter()
        result = auto_writer.check_and_write(args.keyword_id, args.crawl_run_id)
        
        if result:
            print("\n✅ 블로그 글이 자동으로 생성되었습니다!")
        else:
            print("\n❌ 블로그 글 생성이 필요하지 않거나 실패했습니다.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

