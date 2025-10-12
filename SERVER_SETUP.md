# 우분투 서버 설정 가이드

디스크 공간이 부족한 서버에서 Docker 없이 Naver Monitor를 실행하는 방법입니다.

## 🎯 상황

```
디스크: 9.8GB (100% 사용 중)
환경: Ubuntu 서버
Docker: ❌ 사용 불가 (디스크 부족)
해결: 로컬 직접 실행 ✅
```

---

## 🚀 빠른 시작 (3단계)

### 1️⃣ 긴급 정리

```bash
./emergency-cleanup.sh
```

### 2️⃣ 서버 설정

```bash
./setup-server.sh
```

**설치 항목:**
- Python 가상환경 생성
- 필요한 패키지 설치
- Playwright 브라우저 설치
- 데이터베이스 초기화

### 3️⃣ 서버 시작

```bash
./start-server.sh
```

**완료!** 🎉

---

## 📋 상세 단계

### Step 1: 긴급 디스크 정리

```bash
chmod +x emergency-cleanup.sh
./emergency-cleanup.sh
```

**확인:**
```bash
df -h
# 최소 2GB 이상 확보 필요
```

---

### Step 2: 시스템 패키지 설치 (필요시)

```bash
# Python 및 개발 도구
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Node.js (프론트엔드용)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 기타 도구
sudo apt-get install -y curl wget git
```

---

### Step 3: 프로젝트 설정

```bash
# 저장소 클론 (아직 안 했으면)
git clone https://github.com/yourusername/naver-monitor.git
cd naver-monitor

# 설정 실행
chmod +x setup-server.sh
./setup-server.sh
```

**설정 내용:**
1. 가상환경 생성 (`venv/`)
2. Python 패키지 설치 (`requirements.txt`)
3. Playwright 브라우저 설치
4. 데이터베이스 초기화 (`naver_monitor.db`)
5. 디렉토리 생성 (`logs/`, `blog_posts/`)

---

### Step 4: 서버 시작

```bash
chmod +x start-server.sh
./start-server.sh
```

**시작 내용:**
1. 가상환경 활성화
2. 기존 프로세스 정리
3. 백엔드 서버 시작 (포트 8001)
4. 프론트엔드 서버 시작 (포트 3000)
5. PID 저장

---

### Step 5: 접속 확인

```bash
# API 서버 확인
curl http://localhost:8001/

# 브라우저 접속
http://your-server-ip:3000

# 로그인
사용자명: testuser
비밀번호: testpassword123
```

---

## 🔧 관리 명령어

### 서버 제어

```bash
# 시작
./start-server.sh

# 중지
./stop-server.sh

# 재시작
./stop-server.sh && ./start-server.sh

# 상태 확인
ps aux | grep server-debug.py
lsof -i:8001
lsof -i:3000
```

### 로그 확인

```bash
# 백엔드 로그 (실시간)
tail -f logs/server.log

# 프론트엔드 로그
tail -f logs/frontend.log

# 최근 100줄
tail -100 logs/server.log
```

### 데이터베이스 관리

```bash
# 백업
cp naver_monitor.db naver_monitor.db.backup.$(date +%Y%m%d)

# 확인
sqlite3 naver_monitor.db "SELECT COUNT(*) FROM keywords;"

# 복원
cp naver_monitor.db.backup.20250111 naver_monitor.db
```

---

## 🛡️ 서비스 등록 (영구 실행)

### systemd 서비스 생성

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/naver-monitor.service
```

**내용:**
```ini
[Unit]
Description=Naver Monitor API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/naver-monitor
Environment="PATH=/home/ubuntu/naver-monitor/venv/bin:/usr/bin"
ExecStart=/home/ubuntu/naver-monitor/venv/bin/python3 server-debug.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**활성화:**
```bash
# 서비스 등록
sudo systemctl daemon-reload
sudo systemctl enable naver-monitor

# 시작
sudo systemctl start naver-monitor

# 상태 확인
sudo systemctl status naver-monitor

# 로그 확인
sudo journalctl -u naver-monitor -f
```

---

## 🔥 문제 해결

### Q1: 가상환경 생성 실패

```bash
# python3-venv 설치
sudo apt-get install python3-venv

# 다시 시도
./setup-server.sh
```

---

### Q2: Playwright 설치 실패

```bash
# 시스템 의존성 수동 설치
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libgbm1

# Playwright 재설치
source venv/bin/activate
playwright install chromium
```

---

### Q3: 포트가 이미 사용 중

```bash
# 사용 중인 프로세스 확인
lsof -i:8001
lsof -i:3000

# 강제 종료
lsof -ti:8001 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# 재시작
./start-server.sh
```

---

### Q4: 프론트엔드가 시작되지 않음

```bash
# Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 프론트엔드 패키지 설치
cd frontend
npm install

# 빌드
npm run build

# 서빙
npx serve -s dist -p 3000
```

---

## 💾 디스크 모니터링

### 자동 모니터링 스크립트

```bash
# disk-monitor.sh
#!/bin/bash
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt 80 ]; then
    echo "⚠️ 디스크 사용량 경고: ${USAGE}%"
    # 자동 정리
    docker system prune -f
fi
```

### Cron 등록

```bash
sudo crontab -e

# 매시간 확인
0 * * * * /path/to/disk-monitor.sh
```

---

## 📊 리소스 최적화

### 로그 로테이션

```bash
# /etc/logrotate.d/naver-monitor
/home/ubuntu/naver-monitor/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 데이터베이스 최적화

```bash
# SQLite VACUUM (공간 재확보)
sqlite3 naver_monitor.db "VACUUM;"

# 오래된 데이터 삭제
sqlite3 naver_monitor.db "DELETE FROM crawl_results WHERE created_at < date('now', '-30 days');"
sqlite3 naver_monitor.db "VACUUM;"
```

---

## ✅ 완성된 스크립트

| 스크립트 | 용도 | 사용 시기 |
|----------|------|-----------|
| `emergency-cleanup.sh` | 긴급 디스크 정리 | 디스크 100% |
| `setup-server.sh` | 서버 초기 설정 | 최초 1회 |
| `start-server.sh` | 서버 시작 | 매번 |
| `stop-server.sh` | 서버 중지 | 필요 시 |
| `cleanup-docker.sh` | Docker 정리 | 주기적 |

---

## 🎯 전체 프로세스

```bash
# 1. 긴급 정리 (디스크 100%)
./emergency-cleanup.sh

# 2. 디스크 확인
df -h
# 최소 2GB 이상 확보되었는지 확인

# 3. 서버 설정 (최초 1회)
./setup-server.sh

# 4. 서버 시작
./start-server.sh

# 5. 브라우저 접속
http://your-server-ip:3000

# 6. 서버 중지 (필요 시)
./stop-server.sh
```

---

## 🚀 지금 바로 실행

```bash
# 한 번에 실행
./emergency-cleanup.sh && \
./setup-server.sh && \
./start-server.sh
```

**완료 후:**
- 🌐 http://your-server-ip:3000
- 👤 testuser / testpassword123

---

**디스크 공간이 부족해도 실행 가능합니다!** 🎉

