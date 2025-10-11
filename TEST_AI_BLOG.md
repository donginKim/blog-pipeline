# AI 블로그 작성 테스트 가이드

OpenAI API 없이도 로컬에서 테스트할 수 있는 방법을 안내합니다.

## 🧪 테스트 모드

### Mock 데이터 사용

OpenAI API Key가 없어도 **테스트용 Mock 블로그 글**이 자동으로 생성됩니다!

```
⚠️ OpenAI API를 사용할 수 없습니다. 
   테스트 모드로 블로그 글을 생성합니다.
🧪 테스트 모드: Mock 블로그 글 생성 - 파이썬 강의
✅ 블로그 글 생성 완료!
```

---

## 🚀 로컬 테스트 방법

### 1️⃣ 환경 설정 (OpenAI API 없이)

```bash
# 서버 시작
./start-test.sh

# 또는 수동 시작
cd /Users/amiro/Workshop/naver-monitor
source venv/bin/activate
python3 server-debug.py &
```

### 2️⃣ Mock 블로그 글 생성 테스트

#### 방법 A: CLI로 테스트

```bash
# 단순 키워드 테스트
python3 blog-writer.py --keyword "파이썬 강의"

# 출력:
# 🧪 테스트 모드: Mock 블로그 글 생성 - 파이썬 강의
# 📝 제목: [title]파이썬 강의 완벽 가이드...[/title]
# 📋 요약: 파이썬 강의에 대한 초보자를 위한...
# 🏷️ 태그: 파이썬 강의, 가이드, 초보자, 완벽정리, 실전활용
```

#### 방법 B: 자동 크롤링 시뮬레이션

```bash
# 1. 키워드 추가 (웹 UI)
http://localhost:3000 → 키워드 → "테스트 키워드" 추가

# 2. 블로그 추가 (웹 UI)
블로그 → "테스트 블로그" 추가 (url_pattern: test.blog.com)

# 3. 타겟 연결 (웹 UI)
타겟 → "테스트 키워드" + "테스트 블로그" 연결

# 4. 크롤링 실행 (웹 UI)
타겟 페이지에서 개별 크롤링 버튼 클릭

# 5. 생성된 글 확인
🤖 생성된 글 메뉴 → 자동 생성된 글 확인!
```

---

## 📋 생성되는 Mock 콘텐츠

### DSL 형식

```
[title]파이썬 강의 완벽 가이드 - 초보자부터 실전까지[/title]
[separator=line3][/separator]

안녕하세요! 오늘은 [underline]파이썬 강의[/underline]에 대해...

[separator=line3][/separator]
[bold]1. 파이썬 강의란 무엇인가요?[/bold]

파이썬 강의는 현대 사회에서...

[quote=파이썬 강의는 단순히 배우는 것을 넘어...]

[separator=line3][/separator]
[bold]2. 파이썬 강의의 핵심 포인트[/bold]

...

[separator=line3][/separator]
[bold]마무리[/bold]

지금까지 파이썬 강의에 대해 알아보았습니다...
여러분의 파이썬 강의 여정을 응원합니다! 화이팅! 💪
```

### 구조

- **제목**: DSL [title] 태그 포함
- **본문**: 1200-1600자 분량
- **섹션**: 5개 (서론, 3개 본론, 마무리)
- **DSL 태그**: [bold], [underline], [italic], [quote], [separator]
- **태그**: 5개 자동 생성

---

## 🎯 테스트 시나리오

### 시나리오 1: 기본 테스트

```bash
# 1. Mock 글 생성
python3 blog-writer.py --keyword "머신러닝"

# 2. 결과 확인
# - 제목 출력
# - 본문 DSL 형식 확인
# - 태그 확인
```

### 시나리오 2: 자동 생성 테스트

```bash
# 1. 웹 UI 접속
http://localhost:3000

# 2. 타겟 설정
키워드: "딥러닝"
블로그: "myblog.tistory.com"
타겟 연결

# 3. 크롤링 실행
타겟 페이지 → 개별 크롤링

# 4. 결과 확인
크롤링 결과에 타겟 블로그 없으면
→ 자동으로 Mock 블로그 글 생성!

# 5. 생성된 글 확인
🤖 생성된 글 메뉴
```

### 시나리오 3: 발행 준비 테스트

```bash
# 1. 발행 대기 글 목록
python3 naver-blog-publisher.py --list

# 2. 발행 준비
python3 naver-blog-publisher.py --publish 1

# 생성 파일:
# - blog_posts/post_1.html (HTML 미리보기)
# - blog_posts/post_1_dsl.txt (DSL 원본)

# 3. 파일 확인
cat blog_posts/post_1_dsl.txt
open blog_posts/post_1.html
```

---

## ✅ Mock vs 실제 OpenAI

### 비교표

| 항목 | Mock (테스트) | OpenAI API (실제) |
|------|---------------|-------------------|
| **비용** | 무료 | 유료 ($0.01-0.03/글) |
| **속도** | 즉시 | 3-10초 |
| **품질** | 템플릿 기반 | AI 맞춤형 |
| **키워드 적용** | 단순 치환 | 문맥 이해 |
| **다양성** | 항상 동일 구조 | 매번 다름 |
| **설정** | 불필요 | API Key 필요 |

### Mock 데이터의 장점

✅ **즉시 테스트**: API Key 없이 바로 테스트  
✅ **비용 절감**: 개발 중 비용 발생 없음  
✅ **안정성**: 네트워크 오류 없음  
✅ **예측 가능**: 항상 동일한 구조  

### OpenAI API의 장점

✅ **고품질**: 전문적인 콘텐츠  
✅ **맞춤형**: 키워드별 최적화  
✅ **다양성**: 매번 다른 내용  
✅ **SEO**: 검색 엔진 최적화  

---

## 🔧 개발 워크플로우

### 추천 순서

1. **Mock으로 개발** (로컬 테스트)
   - 기능 개발 및 디버깅
   - UI/UX 테스트
   - 데이터 흐름 확인

2. **OpenAI로 검증** (스테이징)
   - 실제 API 연동 테스트
   - 품질 확인
   - 비용 예측

3. **프로덕션 배포** (운영)
   - OpenAI API 사용
   - 실제 블로그 발행
   - 모니터링

---

## 📝 테스트 체크리스트

### 기능 테스트

- [ ] Mock 블로그 글 생성
- [ ] 데이터베이스 저장
- [ ] API 엔드포인트 조회
- [ ] 웹 UI에서 글 목록 확인
- [ ] DSL 복사 기능
- [ ] 미리보기 기능
- [ ] 발행 준비 기능
- [ ] 발행 완료 표시
- [ ] 글 삭제

### UI/UX 테스트

- [ ] 생성된 글 목록 표시
- [ ] 상세 모달 열기/닫기
- [ ] DSL 복사 버튼
- [ ] 태그 표시
- [ ] 상태 뱃지
- [ ] 발행 가이드 표시

---

## 🎯 실제 사용 전환

### Mock → OpenAI 전환

#### 1. OpenAI API Key 발급

```bash
# https://platform.openai.com/api-keys 에서 발급
```

#### 2. 환경 변수 설정

```bash
# .env 파일 편집
nano .env

# API Key 추가
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 3. 서버 재시작

```bash
./start-test.sh
```

#### 4. 확인

```
✅ OpenAI 패키지가 설치되어 있습니다
✅ OPENAI_API_KEY가 설정되어 있습니다
🤖 AI 블로그 글 생성 중: 파이썬 강의
✅ AI 블로그 글 생성 완료!
```

---

## 💡 개발 팁

### Mock 데이터 커스터마이징

`server-debug.py`의 `generate_mock_blog_post` 함수 수정:

```python
def generate_mock_blog_post(keyword: str) -> Dict:
    """커스텀 Mock 데이터"""
    
    # 키워드별 맞춤 콘텐츠
    if "파이썬" in keyword:
        content = "[title]파이썬 전문가가 알려주는...[/title]..."
    elif "자바" in keyword:
        content = "[title]자바 개발자 필수 가이드...[/title]..."
    else:
        content = f"[title]{keyword} 가이드[/title]..."
    
    return {
        "title": f"[title]{keyword} 맞춤 가이드[/title]",
        "content": content,
        ...
    }
```

### 자동 테스트 스크립트

```bash
#!/bin/bash
# test-ai-blog.sh

echo "🧪 AI 블로그 작성 기능 테스트"

# 1. Mock 글 생성
python3 blog-writer.py --keyword "테스트1"
python3 blog-writer.py --keyword "테스트2"

# 2. 데이터베이스 확인
sqlite3 naver_monitor.db "SELECT id, title FROM generated_posts;"

# 3. API 테스트
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"testuser","password":"testpassword123"}' \
  | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/generated-posts

echo "✅ 테스트 완료!"
```

---

## 📊 성능 비교

### 생성 시간

| 방식 | 시간 | 비고 |
|------|------|------|
| Mock | < 0.1초 | 즉시 |
| OpenAI GPT-3.5 | 3-5초 | 네트워크 포함 |
| OpenAI GPT-4 | 8-15초 | 더 느림 |

### 리소스 사용

| 방식 | CPU | 메모리 | 네트워크 |
|------|-----|--------|----------|
| Mock | 최소 | 최소 | 없음 |
| OpenAI | 최소 | 최소 | 중간 |

---

## 🎉 결론

### Mock 모드 사용 시기

- ✅ **개발 중**: 기능 개발 및 디버깅
- ✅ **테스트**: UI/UX 테스트
- ✅ **데모**: 고객 시연
- ✅ **교육**: 개발자 온보딩

### OpenAI 모드 사용 시기

- ✅ **스테이징**: 실제 품질 검증
- ✅ **프로덕션**: 실제 블로그 운영
- ✅ **대량 생성**: 많은 키워드 처리

---

## 📚 관련 문서

- [AI_BLOG_WRITER.md](AI_BLOG_WRITER.md) - AI 작성 기능 전체 가이드
- [NAVER_BLOG_GUIDE.md](NAVER_BLOG_GUIDE.md) - 네이버 발행 방법
- [README.md](README.md) - 프로젝트 전체 가이드

---

**OpenAI API 없이도 모든 기능을 테스트할 수 있습니다!** 🎉

실제 운영 시에는 OpenAI API Key를 설정하여 고품질 콘텐츠를 생성하세요.

