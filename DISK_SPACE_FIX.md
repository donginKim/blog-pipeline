# Docker 디스크 공간 부족 해결 가이드

Docker 빌드 시 "no space left on device" 오류를 해결하는 방법입니다.

## 🔥 오류 증상

```
ERROR: no space left on device
ERROR: failed to copy: write ... no space left on device
```

---

## 🚀 빠른 해결 (자동)

### 방법 1: 자동 정리 스크립트 (권장)

```bash
./cleanup-docker.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
1. ✅ 중지된 컨테이너 삭제
2. ✅ 사용하지 않는 이미지 삭제
3. ✅ 빌드 캐시 정리
4. ✅ 불필요한 볼륨 삭제
5. ✅ 네트워크 정리

---

## 🛠️ 수동 해결

### 1단계: 현재 상태 확인

```bash
# 전체 디스크 사용량
df -h

# Docker 사용량
docker system df

# 상세 확인
docker system df -v
```

**출력 예시:**
```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          15        2         8.5GB     7.2GB (84%)
Containers      10        3         1.2GB     800MB (66%)
Local Volumes   5         2         3.5GB     2.1GB (60%)
Build Cache     120       0         4.8GB     4.8GB (100%)
```

### 2단계: 정리 실행

#### 옵션 A: 전체 정리 (가장 효과적)

```bash
# ⚠️ 주의: 모든 중지된 컨테이너, 이미지, 볼륨, 네트워크 삭제
docker system prune -a --volumes

# 확인
Are you sure? [y/N]: y
```

#### 옵션 B: 선택적 정리

```bash
# 중지된 컨테이너만
docker container prune

# 사용하지 않는 이미지
docker image prune -a

# 빌드 캐시
docker builder prune -a

# 볼륨
docker volume prune

# 네트워크
docker network prune
```

### 3단계: 추가 정리

```bash
# Docker 로그 정리
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

# 임시 파일 정리
sudo rm -rf /tmp/*

# APT 캐시 정리
sudo apt-get clean
sudo apt-get autoclean
```

---

## 📊 디스크 공간 확보 방법

### 일반 파일 정리

```bash
# 큰 파일 찾기 (상위 20개)
sudo du -h / 2>/dev/null | sort -rh | head -20

# 로그 파일 정리
sudo find /var/log -type f -name "*.log" -mtime +30 -delete

# APT 캐시
sudo apt-get clean

# 오래된 커널 삭제
sudo apt-get autoremove --purge
```

### Docker 데이터 이동

```bash
# Docker 데이터를 다른 디스크로 이동
sudo systemctl stop docker

# 현재 Docker 데이터
sudo mv /var/lib/docker /mnt/new-disk/docker

# 심볼릭 링크 생성
sudo ln -s /mnt/new-disk/docker /var/lib/docker

# Docker 재시작
sudo systemctl start docker
```

---

## 🎯 배포 전 디스크 요구사항

### 최소 여유 공간

| 항목 | 크기 |
|------|------|
| Docker 이미지 (백엔드) | 1.2 GB |
| Docker 이미지 (프론트엔드) | 500 MB |
| 빌드 캐시 | 2 GB |
| 데이터베이스 | 100 MB |
| 로그 | 200 MB |
| **총 필요 공간** | **4 GB** |

### 권장 여유 공간

- 개발/테스트: **10 GB**
- 프로덕션: **20 GB**

---

## 💡 예방 방법

### 정기적인 정리

```bash
# Cron 작업 추가
sudo crontab -e

# 매주 일요일 새벽 2시에 정리
0 2 * * 0 docker system prune -af >> /var/log/docker-cleanup.log 2>&1
```

### Docker 로그 크기 제한

```bash
# /etc/docker/daemon.json 생성/편집
sudo nano /etc/docker/daemon.json

# 추가:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Docker 재시작
sudo systemctl restart docker
```

### 빌드 최적화

```dockerfile
# .dockerignore 활용
# 불필요한 파일 제외
node_modules/
.git/
*.log
__pycache__/

# Multi-stage 빌드
FROM python:3.9 AS builder
# ... 빌드 ...

FROM python:3.9-slim
COPY --from=builder /app /app
```

---

## 🔧 우회 방법

### Docker 없이 배포

```bash
# 로컬에서 직접 실행
./start-test.sh

# 또는 systemd 서비스로 등록
sudo systemctl enable naver-monitor
```

### 경량 이미지 사용

```bash
# Alpine Linux 기반 (가장 작음)
FROM python:3.9-alpine
# 크기: ~150MB (기본의 1/10)
```

---

## 📋 빠른 참조

### 디스크 확인

```bash
# 전체 디스크
df -h

# Docker 디스크
docker system df

# 상세
docker system df -v
```

### 빠른 정리

```bash
# 한 줄 정리
docker system prune -af --volumes

# 자동 스크립트
./cleanup-docker.sh
```

### 재배포

```bash
# 정리 후 재배포
./cleanup-docker.sh
./deploy-stable.sh
```

---

## 🆘 긴급 상황

### 디스크가 완전히 꽉 찬 경우

```bash
# 1. 실행 중인 컨테이너 중지
docker stop $(docker ps -aq)

# 2. 모든 컨테이너 삭제
docker rm $(docker ps -aq)

# 3. 모든 이미지 삭제
docker rmi $(docker images -q)

# 4. 모든 볼륨 삭제
docker volume rm $(docker volume ls -q)

# 5. 빌드 캐시 삭제
docker builder prune -a -f

# 6. 시스템 전체 정리
docker system prune -a --volumes -f

# 7. 디스크 확인
df -h
```

### 그래도 공간 부족 시

```bash
# 시스템 전체 큰 파일 찾기
sudo du -sh /* 2>/dev/null | sort -rh | head -20

# 로그 파일 전체 삭제
sudo rm -rf /var/log/*.log
sudo rm -rf /var/log/*/*.log

# Journal 로그 정리
sudo journalctl --vacuum-time=7d
sudo journalctl --vacuum-size=100M

# APT 캐시 정리
sudo apt-get clean
sudo rm -rf /var/cache/apt/archives/*
```

---

## ✅ 해결 완료 후

### 확인사항

```bash
# 디스크 여유 공간 확인 (최소 5GB 필요)
df -h

# Docker 상태 확인
docker system df

# 배포 재시도
./deploy-stable.sh
```

---

## 🎯 권장 대안

디스크 공간이 계속 부족하다면:

### 대안 1: 로컬 실행 (Docker 없이)

```bash
./start-test.sh
```

**장점:**
- ✅ Docker 불필요
- ✅ 디스크 공간 절약
- ✅ 즉시 실행

### 대안 2: 더 큰 디스크로 업그레이드

```bash
# 디스크 추가 마운트
sudo fdisk -l
sudo mount /dev/sdb1 /mnt/newdisk

# Docker 데이터 이동
sudo systemctl stop docker
sudo mv /var/lib/docker /mnt/newdisk/
sudo ln -s /mnt/newdisk/docker /var/lib/docker
sudo systemctl start docker
```

### 대안 3: 외부 서버 사용

- AWS EC2
- Google Cloud
- Azure
- DigitalOcean

최소 20GB 디스크 제공

---

## 📞 도움말

더 자세한 내용:
- [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
- [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)

---

**마지막 업데이트:** 2025-10-11

