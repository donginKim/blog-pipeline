#!/bin/bash

# Docker Compose 배포 스크립트

PUBLIC_IP=${1:-"49.50.134.250"}

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🐳 Docker Compose 배포"
echo "=========================================="
echo ""
echo -e "${BLUE}공인 IP: $PUBLIC_IP${NC}"
echo ""

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
    echo ""
    echo "설치 방법:"
    echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "   sudo sh get-docker.sh"
    echo ""
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose가 설치되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 확인 완료${NC}"

# .env 파일 생성
echo -e "${YELLOW}📝 .env 파일 생성...${NC}"

if [ ! -f ".env" ]; then
    if [ -f "env.production.example" ]; then
        cp env.production.example .env
        echo -e "${GREEN}✅ .env 파일 생성 완료 (env.production.example에서 복사)${NC}"
    else
        cat > .env << EOF
PUBLIC_IP=$PUBLIC_IP
BACKEND_PORT=8001
FRONTEND_PORT=3000
POSTGRES_USER=naver_monitor
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
POSTGRES_DB=naver_monitor
SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
CORS_ORIGINS=http://${PUBLIC_IP}:3000,http://localhost:3000
ALIGO_API_KEY=
ALIGO_USER_ID=
ALIGO_SENDER=
OPENAI_API_KEY=
EOF
        echo -e "${GREEN}✅ .env 파일 생성 완료 (기본 설정)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env 파일이 이미 존재합니다.${NC}"
    
    # PUBLIC_IP 업데이트
    if grep -q "^PUBLIC_IP=" .env; then
        sed -i.bak "s/^PUBLIC_IP=.*/PUBLIC_IP=$PUBLIC_IP/" .env && rm -f .env.bak
        echo -e "${GREEN}✅ PUBLIC_IP 업데이트: $PUBLIC_IP${NC}"
    else
        echo "PUBLIC_IP=$PUBLIC_IP" >> .env
        echo -e "${GREEN}✅ PUBLIC_IP 추가: $PUBLIC_IP${NC}"
    fi
    
    # CORS_ORIGINS 업데이트
    CORS_ORIGINS="http://${PUBLIC_IP}:3000,http://localhost:3000"
    if grep -q "^CORS_ORIGINS=" .env; then
        sed -i.bak "s|^CORS_ORIGINS=.*|CORS_ORIGINS=$CORS_ORIGINS|" .env && rm -f .env.bak
        echo -e "${GREEN}✅ CORS_ORIGINS 업데이트${NC}"
    else
        echo "CORS_ORIGINS=$CORS_ORIGINS" >> .env
        echo -e "${GREEN}✅ CORS_ORIGINS 추가${NC}"
    fi
fi

echo ""
echo -e "${BLUE}📋 .env 파일 내용:${NC}"
echo "---"
cat .env | grep -v PASSWORD | grep -v SECRET_KEY
echo "---"
echo ""

# 기존 컨테이너 중지
echo -e "${YELLOW}🛑 기존 컨테이너 중지...${NC}"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Docker Compose 빌드 및 시작
echo -e "${YELLOW}🔨 Docker 이미지 빌드 중... (5-10분 소요)${NC}"
if docker compose version &> /dev/null 2>&1; then
    docker compose -f docker-compose.prod.yml build
else
    docker-compose -f docker-compose.prod.yml build
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 빌드 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 빌드 완료${NC}"

# 컨테이너 시작
echo -e "${YELLOW}🚀 컨테이너 시작 중...${NC}"
if docker compose version &> /dev/null 2>&1; then
    docker compose -f docker-compose.prod.yml up -d
else
    docker-compose -f docker-compose.prod.yml up -d
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 컨테이너 시작 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 컨테이너 시작 완료${NC}"

# 컨테이너 상태 확인
echo ""
echo -e "${YELLOW}⏳ 서비스 시작 대기 중...${NC}"
sleep 10

echo ""
echo -e "${BLUE}📊 컨테이너 상태:${NC}"
if docker compose version &> /dev/null 2>&1; then
    docker compose -f docker-compose.prod.yml ps
else
    docker-compose -f docker-compose.prod.yml ps
fi

# 데이터베이스 초기화 확인
echo ""
echo -e "${YELLOW}🔍 데이터베이스 초기화 확인...${NC}"
sleep 5

DB_CHECK=$(docker exec naver-monitor-backend python3 -c "
import os
from sqlalchemy import create_engine, text
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM users'))
        count = result.fetchone()[0]
        if count > 0:
            print('OK')
        else:
            print('EMPTY')
except:
    print('ERROR')
" 2>/dev/null)

if [ "$DB_CHECK" = "OK" ]; then
    echo -e "${GREEN}✅ 데이터베이스 초기화 완료${NC}"
elif [ "$DB_CHECK" = "EMPTY" ]; then
    echo -e "${YELLOW}⚠️  사용자가 없습니다. 초기화 실행 중...${NC}"
    docker exec naver-monitor-backend python3 init-db-postgres.py
elif [ "$DB_CHECK" = "ERROR" ]; then
    echo -e "${YELLOW}⚠️  테이블이 없습니다. 초기화 실행 중...${NC}"
    docker exec naver-monitor-backend python3 init-db-postgres.py
else
    echo -e "${YELLOW}⚠️  데이터베이스 상태를 확인할 수 없습니다${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 접속 정보:${NC}"
echo "   - 프론트엔드: http://${PUBLIC_IP}:3000"
echo "   - 백엔드 API: http://${PUBLIC_IP}:8001"
echo "   - API 문서: http://${PUBLIC_IP}:8001/docs"
echo ""
echo -e "${BLUE}🔐 기본 로그인:${NC}"
echo "   - 사용자명: testuser"
echo "   - 비밀번호: testpassword123"
echo ""
echo -e "${YELLOW}⚠️  중요:${NC}"
echo "   1. 네이버 클라우드 ACG에서 포트 3000, 8001을 열어야 합니다"
echo "   2. 비밀번호를 변경하세요: docker exec -it naver-monitor-backend python3 change-password.py"
echo "   3. .env 파일에서 SECRET_KEY와 POSTGRES_PASSWORD를 변경하세요"
echo ""
echo -e "${BLUE}📊 로그 확인:${NC}"
if docker compose version &> /dev/null 2>&1; then
    echo "   - 전체: docker compose -f docker-compose.prod.yml logs -f"
    echo "   - 백엔드: docker compose -f docker-compose.prod.yml logs -f backend"
    echo "   - 프론트엔드: docker compose -f docker-compose.prod.yml logs -f frontend"
else
    echo "   - 전체: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   - 백엔드: docker-compose -f docker-compose.prod.yml logs -f backend"
    echo "   - 프론트엔드: docker-compose -f docker-compose.prod.yml logs -f frontend"
fi
echo ""
echo -e "${BLUE}🛑 서비스 중지:${NC}"
if docker compose version &> /dev/null 2>&1; then
    echo "   docker compose -f docker-compose.prod.yml down"
else
    echo "   docker-compose -f docker-compose.prod.yml down"
fi
echo ""
echo "=========================================="

