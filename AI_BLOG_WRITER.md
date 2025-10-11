# AI 자동 블로그 작성 가이드

Naver Monitor의 AI 기반 자동 블로그 글 작성 기능을 안내합니다.

## 목차

- [개요](#개요)
- [작동 원리](#작동-원리)
- [설정 방법](#설정-방법)
- [사용 방법](#사용-방법)
- [생성된 글 관리](#생성된-글-관리)
- [문제 해결](#문제-해결)

---

## 개요

### 기능 설명

Naver Monitor는 **예약된 크롤링 실행 시** 검색 결과에 등록된 타겟 블로그가 없을 경우, **OpenAI GPT를 사용하여 자동으로 SEO 최적화된 블로그 글을 생성**합니다.

### 주요 특징

✅ **자동 감지**: 타겟 블로그가 검색 결과에 없을 때 자동 실행  
✅ **고품질 콘텐츠**: GPT-3.5-turbo/GPT-4 기반 전문 블로그 글  
✅ **SEO 최적화**: 검색 엔진 최적화를 고려한 제목과 내용  
✅ **마크다운 형식**: 즉시 사용 가능한 마크다운 포맷  
✅ **자동 알림**: SMS로 생성 완료 알림 (선택사항)  

---

## 작동 원리

### 자동 실행 흐름

```
1. 예약된 크롤링 실행
   ↓
2. 검색 결과 수집
   ↓
3. 타겟 블로그 확인
   ↓
4. [타겟 블로그 없음] → AI 블로그 글 생성
   ↓
5. 데이터베이스에 저장
   ↓
6. SMS 알림 발송 (선택사항)
```

### 타겟 블로그 확인 로직

```python
# 등록된 타겟 블로그 URL 패턴
target_patterns = ["blog.naver.com/myid", "myblog.tistory.com"]

# 크롤링 결과에서 확인
for result in crawl_results:
    if any(pattern in result.url for pattern in target_patterns):
        # 타겟 발견! → AI 글 생성 안 함
        return
    
# 타겟 없음! → AI 블로그 글 생성 시작
```

### AI 프롬프트 구조

```
시스템 프롬프트:
- 역할: 전문 블로거, SEO 전문가
- 원칙: 실용적, 가독성, 키워드 최적화

사용자 프롬프트:
- 키워드: {검색 키워드}
- 요구사항: 2000-3000자, 마크다운, 실습 예제 포함
- 출력 형식: JSON (title, summary, content, tags)
```

---

## 설정 방법

### 1️⃣ OpenAI API Key 발급

#### Step 1: OpenAI 계정 생성
1. https://platform.openai.com 접속
2. 회원가입 또는 로그인

#### Step 2: API Key 발급
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 키 이름 입력 (예: "Naver Monitor")
4. 생성된 키 복사 (**한 번만 표시됨!**)

#### Step 3: 요금제 설정
1. https://platform.openai.com/account/billing 접속
2. 결제 수단 등록
3. 사용량 제한 설정 (권장: $10-20/월)

### 2️⃣ 환경 변수 설정

```bash
# .env 파일 편집
nano .env

# OpenAI API Key 추가
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

또는 예시 파일 사용:
```bash
cp env.aligo.example .env
nano .env
```

### 3️⃣ OpenAI 패키지 설치

```bash
# 가상환경 활성화
source venv/bin/activate

# OpenAI 패키지 설치
pip install openai>=1.3.0
```

### 4️⃣ 서버 재시작

```bash
# 서버 재시작
./start-test.sh
```

---

## 사용 방법

### 자동 실행

AI 블로그 작성은 **자동으로** 실행됩니다:

1. **타겟 블로그 등록**
   ```
   키워드: "파이썬 강의"
   타겟 블로그: blog.naver.com/myid
   ```

2. **스케줄 설정**
   - 설정 페이지에서 자동 크롤링 시간 설정
   - 예: 매일 오전 9시

3. **자동 실행**
   - 예약된 시간에 크롤링 실행
   - 타겟 블로그 없으면 AI 글 자동 생성

### 수동 테스트

개발/테스트 목적으로 수동 실행:

```bash
# 단순 테스트 (키워드만)
python3 blog-writer.py --keyword "파이썬 강의"

# 실제 크롤링과 연동
python3 blog-writer.py --keyword-id 1 --crawl-run-id 5
```

### API 엔드포인트

```bash
# 생성된 글 목록 조회
curl http://localhost:8001/api/generated-posts

# 특정 키워드의 글만 조회
curl http://localhost:8001/api/generated-posts?keyword_id=1

# 특정 글 상세 조회
curl http://localhost:8001/api/generated-posts/1

# 글 삭제
curl -X DELETE http://localhost:8001/api/generated-posts/1
```

---

## 생성된 글 관리

### 데이터베이스 구조

```sql
CREATE TABLE generated_posts (
    id INTEGER PRIMARY KEY,
    keyword_id INTEGER,
    crawl_run_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT,  -- JSON 배열
    status TEXT DEFAULT 'generated',
    created_at TIMESTAMP,
    published_at TIMESTAMP
);
```

### 글 상태

| 상태 | 설명 |
|------|------|
| `generated` | AI로 생성됨 (미발행) |
| `published` | 블로그에 발행됨 |
| `failed` | 생성 실패 |

### 생성된 글 조회

```bash
# 모든 생성된 글 조회
sqlite3 naver_monitor.db "SELECT id, title, created_at FROM generated_posts;"

# 특정 키워드의 글
sqlite3 naver_monitor.db "SELECT title FROM generated_posts WHERE keyword_id = 1;"

# 최근 10개 글
sqlite3 naver_monitor.db "SELECT id, title, created_at FROM generated_posts ORDER BY created_at DESC LIMIT 10;"
```

### 글 내용 확인

```bash
# 글 상세 내용
sqlite3 naver_monitor.db "SELECT title, summary, content FROM generated_posts WHERE id = 1;"

# 마크다운 파일로 저장
sqlite3 naver_monitor.db "SELECT content FROM generated_posts WHERE id = 1;" > post.md
```

---

## 문제 해결

### Q1: AI 글이 생성되지 않음

**증상:**
```
⚠️ OpenAI 패키지가 설치되지 않았습니다.
```

**해결:**
```bash
pip install openai>=1.3.0
```

---

### Q2: API Key 오류

**증상:**
```
⚠️ OPENAI_API_KEY가 설정되지 않았습니다.
```

**해결:**
```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# API Key 추가
echo "OPENAI_API_KEY=sk-proj-xxxxx" >> .env

# 서버 재시작
./start-test.sh
```

---

### Q3: 비용 초과

**증상:**
```
Error: You exceeded your current quota
```

**해결:**
1. https://platform.openai.com/account/billing 접속
2. 결제 수단 확인 및 충전
3. Usage limits 설정

**비용 절감 팁:**
- GPT-3.5-turbo 사용 (GPT-4보다 저렴)
- 생성 빈도 제한
- `max_tokens` 줄이기 (현재: 2000)

---

### Q4: 생성된 글 품질 개선

**문제:** 생성된 글이 기대에 미치지 못함

**해결:**

1. **프롬프트 수정** (`server-debug.py`)
```python
prompt = f"""다음 키워드로 블로그 글을 작성해주세요:

키워드: {keyword}

요구사항:
1. 3000-5000자 분량 (더 길게)
2. 실전 예제 5개 이상 포함
3. 초보자부터 중급자까지 이해 가능
4. 코드 블록 사용
5. 이미지 설명 포함

스타일:
- 친근하고 대화하듯이
- 실용적이고 따라하기 쉽게
- SEO 키워드 자연스럽게 포함
"""
```

2. **모델 변경**
```python
# GPT-4 사용 (더 높은 품질)
model="gpt-4"

# 창의성 조절
temperature=0.8  # 0.7 → 0.8 (더 창의적)
```

3. **수동 검토 후 수정**
```bash
# 생성된 글 확인
curl http://localhost:8001/api/generated-posts/1

# 수정 후 데이터베이스 업데이트
sqlite3 naver_monitor.db "UPDATE generated_posts SET content = '수정된 내용' WHERE id = 1;"
```

---

### Q5: 타겟 블로그 감지 안 됨

**문제:** 타겟 블로그가 있는데도 AI 글이 생성됨

**원인:** URL 패턴 불일치

**해결:**
```bash
# 1. 크롤링 결과 확인
sqlite3 naver_monitor.db "SELECT url FROM crawl_results WHERE crawl_run_id = 1;"

# 2. 타겟 블로그 URL 패턴 확인
sqlite3 naver_monitor.db "SELECT url_pattern FROM blogs;"

# 3. URL 패턴 수정
sqlite3 naver_monitor.db "UPDATE blogs SET url_pattern = 'blog.naver.com/myid' WHERE id = 1;"
```

**URL 패턴 예시:**
```
✅ 올바른 패턴: blog.naver.com/myid
✅ 올바른 패턴: myblog.tistory.com
❌ 잘못된 패턴: https://blog.naver.com/myid  (프로토콜 포함)
❌ 잘못된 패턴: blog.naver.com  (ID 없음)
```

---

## 비용 정보

### OpenAI API 요금 (2024년 기준)

| 모델 | 입력 | 출력 | 글 1개당 예상 비용 |
|------|------|------|-------------------|
| GPT-3.5-turbo | $0.0015/1K | $0.002/1K | $0.01 - $0.03 |
| GPT-4 | $0.03/1K | $0.06/1K | $0.30 - $0.50 |

### 예상 월 비용

**시나리오 1: 소규모**
- 키워드: 5개
- 크롤링 빈도: 매일 1회
- 타겟 미발견: 평균 2회/일
- 모델: GPT-3.5-turbo
- **월 비용: ~$1-2**

**시나리오 2: 중규모**
- 키워드: 20개
- 크롤링 빈도: 매일 2회
- 타겟 미발견: 평균 10회/일
- 모델: GPT-3.5-turbo
- **월 비용: ~$10-15**

**시나리오 3: 대규모**
- 키워드: 100개
- 크롤링 빈도: 매일 3회
- 타겟 미발견: 평균 50회/일
- 모델: GPT-4
- **월 비용: ~$500-750**

---

## 고급 설정

### 프롬프트 커스터마이징

`server-debug.py` 파일의 `generate_blog_post_ai` 함수를 수정:

```python
# 토대 변경
tone = "professional"  # professional, friendly, technical, casual

# 섹션 구성 변경
sections = ["서론", "핵심 내용", "실습", "FAQ", "마무리"]

# 길이 조절
max_tokens = 3000  # 기본: 2000

# 온도 조절 (창의성)
temperature = 0.9  # 기본: 0.7 (높을수록 창의적)
```

### 생성 조건 변경

타겟 블로그 순위 기준 추가:

```python
# 타겟 블로그가 10위 밖이면 생성
if target_rank > 10 or not has_target:
    generate_blog_post_ai(keyword)
```

### 발행 자동화

생성된 글을 자동으로 블로그에 발행:

```python
# 네이버 블로그 API 연동
def publish_to_naver_blog(post):
    # 네이버 블로그 API 호출
    response = requests.post(
        "https://openapi.naver.com/blog/writePost.json",
        headers={"Authorization": f"Bearer {NAVER_TOKEN}"},
        json={"title": post["title"], "content": post["content"]}
    )
    return response.json()
```

---

## 모범 사례

### ✅ 권장 사항

1. **테스트 먼저**
   - OpenAI API Key 발급 후 수동 테스트
   - 생성된 글 품질 확인

2. **비용 제한 설정**
   - OpenAI Dashboard에서 월 사용량 제한
   - 예상치 못한 비용 방지

3. **생성 빈도 조절**
   - 처음에는 일 1-2회만
   - 품질 확인 후 점차 증가

4. **수동 검토**
   - 생성된 글은 반드시 검토 후 발행
   - AI는 보조 도구일 뿐

5. **키워드 최적화**
   - 명확하고 구체적인 키워드 사용
   - "파이썬" (X) → "파이썬 웹 크롤링 초보 가이드" (O)

### ❌ 주의사항

1. **저작권 확인**
   - AI 생성 콘텐츠도 저작권 고려
   - 사실 확인 필수

2. **과도한 생성 방지**
   - 검색 엔진 패널티 가능
   - 품질 > 양

3. **API Key 보안**
   - .env 파일 절대 공유 금지
   - GitHub 등에 업로드 금지

---

## 참고 자료

- [OpenAI API 문서](https://platform.openai.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [GPT Best Practices](https://platform.openai.com/docs/guides/gpt-best-practices)

---

**마지막 업데이트:** 2025-10-10  
**버전:** 1.0.0

