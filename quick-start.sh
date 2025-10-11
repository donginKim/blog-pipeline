#!/bin/bash

echo "🚀 Naver Monitor 빠른 시작"
echo ""

# Kill existing processes
pkill -f server-with-auth.py 2>/dev/null || true
pkill -f simple-server.py 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Start backend
echo "🔧 백엔드 시작 중..."
source venv/bin/activate
python3 server-with-auth.py &
sleep 3

# Start frontend
echo "🎨 프론트엔드 시작 중..."
cd frontend
npm run dev &
cd ..

sleep 5

echo ""
echo "✅ 준비 완료!"
echo "🌐 프론트엔드: http://localhost:3001"
echo "🔧 API 서버: http://localhost:8001"
echo "📚 API 문서: http://localhost:8001/docs"
echo ""
echo "👤 테스트 계정: testuser / testpassword123"
echo ""
echo "⚠️  종료: Ctrl+C"

# Keep running
wait
