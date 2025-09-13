FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

ENV TZ=Asia/Seoul \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
# 필요시 브라우저 강제 설치
# RUN python -m playwright install --with-deps chromium

COPY . /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]