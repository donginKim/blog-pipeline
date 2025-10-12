#!/bin/bash

# Naver Monitor 안정적 배포 스크립트

set -e

echo "🚀 Naver Monitor 안정적 배포 시작"
echo "=========================================="

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
    echo "설치: sudo apt-get install docker.io docker-compose"
    exit 1
fi

echo -e "${GREEN}✅ Docker 확인 완료${NC}"

# 데이터베이스 초기화
if [ ! -f naver_monitor.db ]; then
    echo -e "${YELLOW}🔧 데이터베이스 초기화...${NC}"
    if command -v python3 &> /dev/null; then
        python3 init-db.py
        echo -e "${GREEN}✅ 데이터베이스 초기화 완료${NC}"
    else
        echo -e "${RED}❌ Python3가 필요합니다. 먼저 데이터베이스를 초기화하세요:${NC}"
        echo "   python3 init-db.py"
        exit 1
    fi
fi

# 디렉토리 생성
mkdir -p logs blog_posts

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다. 기본값을 사용합니다.${NC}"
    echo -e "${BLUE}💡 .env 파일 생성 방법:${NC}"
    echo "   cp env.aligo.example .env"
    echo "   nano .env"
    echo ""
fi

# 기존 컨테이너 정리 확인
read -p "기존 컨테이너를 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 정리 중...${NC}"
    docker-compose -f docker-compose.stable.yml down 2>/dev/null || true
fi

# 빌드
echo -e "${YELLOW}🔨 이미지 빌드 중... (3-5분 소요)${NC}"
docker-compose -f docker-compose.stable.yml build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 빌드 실패${NC}"
    echo ""
    echo -e "${YELLOW}📋 문제 해결 방법:${NC}"
    echo "1. 인터넷 연결 확인: ping -c 3 google.com"
    echo "2. Docker 재시작: sudo systemctl restart docker"
    echo "3. 캐시 삭제: docker system prune -a"
    echo "4. 로컬 실행: ./start-test.sh"
    echo ""
    echo "상세 가이드: cat DOCKER_TROUBLESHOOTING.md"
    exit 1
fi

echo -e "${GREEN}✅ 빌드 완료${NC}"

# 시작
echo -e "${YELLOW}🚀 컨테이너 시작 중...${NC}"
docker-compose -f docker-compose.stable.yml up -d

echo -e "${GREEN}✅ 시작 완료${NC}"

# 대기
echo -e "${YELLOW}⏳ 서비스 시작 대기...${NC}"
sleep 10

# 상태 확인
echo ""
echo "📊 서비스 상태:"
docker-compose -f docker-compose.stable.yml ps

# 접속 정보
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 접속 정보:${NC}"
echo "   - 프론트엔드: http://localhost:3000"
echo "   - 백엔드 API: http://localhost:8001"
echo "   - API 문서: http://localhost:8001/docs"
echo ""
echo -e "${BLUE}🔧 기본 계정:${NC}"
echo "   - 사용자명: testuser (또는 admin)"
echo "   - 비밀번호: testpassword123 (또는 admin123)"
echo ""
echo -e "${BLUE}📊 관리 명령어:${NC}"
echo "   - 로그: docker-compose -f docker-compose.stable.yml logs -f"
echo "   - 중지: docker-compose -f docker-compose.stable.yml down"
echo "   - 재시작: docker-compose -f docker-compose.stable.yml restart"
echo ""
echo -e "${BLUE}💾 백업:${NC}"
echo "   cp naver_monitor.db naver_monitor.db.backup"
echo ""
echo "=========================================="

