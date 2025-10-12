# Naver Monitor API v2.0

🚀 **Advanced Naver blog monitoring system with real-time crawling and modern architecture**

## 📚 문서

### 🚀 빠른 시작
- **[Docker 배포](DOCKER_DEPLOY.md)** - ⭐ Docker로 빠르게 배포
- **[Docker 문제 해결](DOCKER_TROUBLESHOOTING.md)** - 빌드 오류 해결
- **[로컬 테스트](#로컬-테스트-환경)** - 개발 및 테스트

### 🤖 AI 기능
- **[AI 블로그 작성](AI_BLOG_WRITER.md)** - AI 자동 블로그 글 생성
- **[네이버 블로그 발행](NAVER_BLOG_GUIDE.md)** - 네이버 블로그 발행 가이드
- **[AI 테스트](TEST_AI_BLOG.md)** - OpenAI 없이 로컬 테스트

### 🛠️ 관리
- **[계정 관리](ACCOUNT_MANAGEMENT.md)** - 사용자 계정 관리
- **[배포 가이드](DEPLOYMENT.md)** - 프로덕션 배포 상세
- **[빠른 배포](QUICK_DEPLOY.md)** - 5분 안에 배포

## ✨ Features

- **🔐 Authentication**: JWT-based user authentication
- **📊 Real-time Dashboard**: Live monitoring of crawl progress
- **⚡ Async Crawling**: High-performance Playwright-based crawler
- **🔄 Background Tasks**: Celery-powered task queue
- **📈 Analytics**: Detailed performance metrics and statistics
- **🎯 Smart Filtering**: Advanced result filtering and search
- **📱 RESTful API**: Complete OpenAPI documentation
- **🐳 Docker Ready**: Full containerization support

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │   Celery        │
│   (Frontend)    │◄──►│   (API Gateway) │◄──►│   (Worker)      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5555    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │     Redis       │
                       │   (Database)    │    │   (Cache/Queue) │
                       │   Port: 5432    │    │   Port: 6379    │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** + **Pydantic v2** (API)
- **SQLAlchemy 2.0** + **Alembic** (ORM)
- **PostgreSQL** (Database)
- **Redis** (Cache/Queue)
- **Celery** (Background Tasks)
- **Playwright** (Web Scraping)
- **Pytest** (Testing)

### Frontend
- **React 18** + **TypeScript**
- **Vite** (빌드 도구)
- **Tailwind CSS** + **Headless UI**
- **React Query** (서버 상태 관리)
- **Chart.js** + **React-Chartjs-2**
- **React Router** (라우팅)

### DevOps
- **Docker Compose** (Development)
- **Prometheus** + **Grafana** (Monitoring)
- **ELK Stack** (Logging)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd naver-monitor
chmod +x setup-local.sh
./setup-local.sh
```

### 2. Start Local Development
```bash
# Start test environment
chmod +x start-local.sh
./start-local.sh
```

### 3. Run Services (in separate terminals)
```bash
# Terminal 1: Backend API
source venv/bin/activate
cd backend && uvicorn app.main:app --reload

# Terminal 2: Celery Worker
source venv/bin/activate
cd backend && celery -A app.core.celery worker --loglevel=info

# Terminal 3: Frontend
cd frontend && npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Flower (Celery)**: http://localhost:5555

### 5. Test Account
- **Username**: testuser
- **Password**: testpassword123

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend App**: http://localhost:3000

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Keywords
- `GET /api/keywords/` - List keywords
- `POST /api/keywords/` - Create keyword
- `GET /api/keywords/{id}` - Get keyword
- `PUT /api/keywords/{id}` - Update keyword
- `DELETE /api/keywords/{id}` - Delete keyword

### Blogs
- `GET /api/blogs/` - List blogs
- `POST /api/blogs/` - Create blog
- `GET /api/blogs/{id}` - Get blog
- `PUT /api/blogs/{id}` - Update blog
- `DELETE /api/blogs/{id}` - Delete blog

### Targets (Keyword-Blog Mappings)
- `GET /api/targets/` - List targets
- `POST /api/targets/` - Create target
- `POST /api/targets/{id}/crawl` - Trigger crawl for target

### Results
- `GET /api/results/` - List crawl results
- `GET /api/results/stats` - Get result statistics
- `GET /api/results/runs` - List crawl runs
- `POST /api/results/trigger-crawl` - Trigger full crawl

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activity

## 🎯 Usage Examples

### 1. Register and Login
```bash
# Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password123"
```

### 2. Create Keyword and Blog
```bash
# Create keyword
curl -X POST "http://localhost:8000/api/keywords/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "파이썬", "description": "Python programming"}'

# Create blog
curl -X POST "http://localhost:8000/api/blogs/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Blog", "url_pattern": "https://blog.naver.com/myid"}'
```

### 3. Create Target and Trigger Crawl
```bash
# Create target
curl -X POST "http://localhost:8000/api/targets/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keyword_id": 1, "blog_id": 1}'

# Trigger crawl
curl -X POST "http://localhost:8000/api/targets/1/crawl" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔍 Monitoring

### Flower (Celery Monitoring)
- **URL**: http://localhost:5555
- Monitor task progress, worker status, and task history

### Health Checks
- **API Health**: http://localhost:8000/health
- **Database**: PostgreSQL health check in Docker
- **Redis**: Redis health check in Docker

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --cov=app
```

## 📊 Database Schema

### Core Tables
- `users` - User accounts
- `keywords` - Search keywords
- `blogs` - Blog URL patterns
- `keyword_targets` - Keyword-Blog mappings
- `crawl_runs` - Crawl execution records
- `crawl_results` - Individual crawl results

### Key Relationships
- Users can manage multiple keywords and blogs
- Keywords can be mapped to multiple blogs
- Each crawl run contains multiple results
- Results link keywords, blogs, and crawl runs

## 📱 알리고 SMS 알림 설정

크롤링 완료/실패 시 자동으로 SMS 알림을 받을 수 있습니다.

### 1. 알리고 가입 및 설정

1. **알리고 회원가입**: https://smartsms.aligo.in
2. **API Key 발급**: 로그인 후 [API 연동] 메뉴에서 발급
3. **발신번호 등록**: [발신번호 관리]에서 본인 인증 후 등록
4. **캐시 충전**: SMS 발송을 위한 충전 (건당 약 15원)

### 2. 환경변수 설정

`.env` 파일에 다음 내용 추가:

```bash
ALIGO_API_KEY=발급받은_API_KEY
ALIGO_USER_ID=알리고_아이디
ALIGO_SENDER=등록된_발신번호
```

예시는 `env.aligo.example` 파일 참고

### 3. 웹에서 알림 설정

1. 로그인 후 **"설정"** 메뉴 클릭
2. **알림 활성화** 토글 ON
3. **전화번호 입력** (예: 010-1234-5678)
4. **알림 조건 선택** (성공 시/실패 시)
5. **"설정 저장"** 클릭
6. **"테스트 메시지 전송"**으로 확인

### 4. 알림 메시지 예시

**크롤링 성공 시:**
```
[Naver Monitor] 크롤링 완료
키워드: 파이썬
블로그: 네이버 블로그
결과: 15개 발견
```

**크롤링 실패 시:**
```
[Naver Monitor] 크롤링 실패
키워드: 자바스크립트
블로그: 티스토리
오류: Timeout exceeded
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Production settings
DEBUG=false
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0

# SMS Notification (Optional)
ALIGO_API_KEY=your-aligo-api-key
ALIGO_USER_ID=your-aligo-user-id
ALIGO_SENDER=your-sender-number
```

### Docker Compose Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: API docs at `/docs`
- **Monitoring**: Flower at `:5555`

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Celery**