#!/bin/bash

echo "🔄 데이터베이스 초기화"
echo "=========================================="
echo ""

# 백엔드 컨테이너 확인
if ! docker ps | grep -q naver-monitor-backend; then
    echo "❌ naver-monitor-backend 컨테이너가 실행 중이지 않습니다."
    echo ""
    echo "먼저 컨테이너를 시작하세요:"
    echo "  ./deploy-docker.sh 49.50.134.250"
    exit 1
fi

echo "✅ 백엔드 컨테이너 확인 완료"
echo ""

# 데이터베이스 연결 대기
echo "⏳ 데이터베이스 연결 대기 중..."
sleep 5

# 데이터베이스 초기화 실행
echo ""
echo "📝 데이터베이스 초기화 중..."
echo "---"

docker exec naver-monitor-backend python3 init-db-postgres.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 데이터베이스 초기화 완료!"
    echo "=========================================="
    echo ""
    echo "🔐 기본 로그인 정보:"
    echo "   사용자명: testuser"
    echo "   비밀번호: testpassword123"
    echo ""
    echo "🌐 로그인 URL:"
    echo "   - API 문서: http://49.50.134.250:8001/docs"
    echo "   - 프론트엔드: http://49.50.134.250:3000"
    echo ""
    echo "⚠️  첫 로그인 후 비밀번호를 변경하세요:"
    echo "   docker exec -it naver-monitor-backend python3 update-account.py"
    echo ""
else
    echo ""
    echo "❌ 데이터베이스 초기화 실패"
    echo ""
    echo "로그 확인:"
    echo "  docker logs naver-monitor-backend"
    echo ""
    exit 1
fi

