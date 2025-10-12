#!/bin/bash

# Naver Monitor 간단한 배포 스크립트 (PostgreSQL 없이 SQLite 사용)

set -e

echo "🚀 Naver Monitor 간단 배포 시작 (SQLite)"
echo "=========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 환경 변수 파일 확인 (선택사항)
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다. 기본값을 사용합니다.${NC}"
    echo -e "${BLUE}💡 .env 파일을 만들어 설정을 커스터마이징할 수 있습니다:${NC}"
    echo "   cp env.aligo.example .env"
    echo "   nano .env"
    echo ""
else
    echo -e "${GREEN}✅ 환경 변수 파일 확인 완료${NC}"
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되지 않았습니다.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose가 설치되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 환경 확인 완료${NC}"

# 데이터베이스 초기화 확인
if [ ! -f naver_monitor.db ]; then
    echo -e "${YELLOW}🔧 데이터베이스 초기화 중...${NC}"
    python3 init-db.py
    echo -e "${GREEN}✅ 데이터베이스 초기화 완료${NC}"
fi

# 로그 및 출력 디렉토리 생성
mkdir -p logs blog_posts

# 기존 컨테이너 정리 (선택사항)
read -p "기존 컨테이너를 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 기존 컨테이너 정리 중..."
    docker-compose -f docker-compose.simple.yml down
    echo -e "${GREEN}✅ 정리 완료${NC}"
fi

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose -f docker-compose.simple.yml build

echo -e "${GREEN}✅ 이미지 빌드 완료${NC}"

# 컨테이너 시작
echo "🚀 컨테이너 시작 중..."
docker-compose -f docker-compose.simple.yml up -d

echo -e "${GREEN}✅ 컨테이너 시작 완료${NC}"

# 헬스체크 대기
echo "⏳ 서비스 헬스체크 중..."
sleep 10

# 서비스 상태 확인
echo ""
echo "📊 서비스 상태:"
docker-compose -f docker-compose.simple.yml ps

# 접속 정보 출력
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
echo "   - 사용자명: admin"
echo "   - 비밀번호: admin123"
echo "   ${RED}⚠️  첫 로그인 후 반드시 비밀번호를 변경하세요!${NC}"
echo ""
echo -e "${BLUE}📊 로그 확인:${NC}"
echo "   - 전체 로그: docker-compose -f docker-compose.simple.yml logs -f"
echo "   - 백엔드: docker-compose -f docker-compose.simple.yml logs -f backend"
echo "   - 프론트엔드: docker-compose -f docker-compose.simple.yml logs -f frontend"
echo ""
echo -e "${BLUE}🔧 관리 명령어:${NC}"
echo "   - 중지: docker-compose -f docker-compose.simple.yml down"
echo "   - 재시작: docker-compose -f docker-compose.simple.yml restart"
echo "   - 재배포: ./deploy-simple.sh"
echo ""
echo -e "${BLUE}💾 데이터베이스:${NC}"
echo "   - 위치: ./naver_monitor.db (SQLite)"
echo "   - 백업: cp naver_monitor.db naver_monitor.db.backup"
echo ""
echo "=========================================="

