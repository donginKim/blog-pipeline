# app/notify.py
from __future__ import annotations
import os, re
from typing import List

PROVIDER = os.getenv("ALERT_PROVIDER", "LOG").upper()
ENV_ALERT_TO: List[str] = [x.strip() for x in os.getenv("ALERT_TO", "").split(",") if x.strip()]
# 옵션: 알림 본문에 모니터링 대상 블로그를 함께 표기할지 여부 (기본: 표기)
ALERT_SHOW_BLOGS = os.getenv("ALERT_SHOW_BLOGS", "1")
def _receivers_from_db() -> List[str]:
    """활성화된 BlogCredential.phone 목록을 DB에서 읽어 수신자 리스트로 반환"""
    try:
        # 순환 import 방지: 함수 안에서 지연 import
        from sqlalchemy import select
        from .db import SessionLocal
        from .models import BlogCredential

        db = SessionLocal()
        try:
            rows = (
                db.execute(
                    select(BlogCredential.phone).where(
                        BlogCredential.is_active == True,
                        BlogCredential.phone.is_not(None),
                        BlogCredential.phone != "",
                    )
                )
                .scalars()
                .all()
            )
        finally:
            db.close()

        # 숫자만 남기고 중복 제거
        out: List[str] = []
        seen = set()
        for ph in rows:
            n = _digits_kr(ph)
            if n and n not in seen:
                seen.add(n)
                out.append(n)
        return out
    except Exception as e:
        print(f"[ALERT][DB READ FAIL] {e}")
        return []

def _resolve_receivers() -> List[str]:
    """DB에서 수신자 읽기 → 없으면 환경변수 ALERT_TO 사용"""
    nums = _receivers_from_db()
    if nums:
        return nums
    out: List[str] = []
    seen = set()
    for x in ENV_ALERT_TO:
        n = _digits_kr(x)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out

# 활성화된 모니터링 대상 블로그 요약 라벨 (이름 또는 URL, 최대 5개 + 외 N개)
def _monitored_blogs_label() -> str:
    """활성화된 모니터링 대상 블로그 요약 라벨 (이름 또는 URL, 최대 5개 + 외 N개)"""
    try:
        # 순환 import 방지: 함수 안에서 지연 import
        from sqlalchemy import select
        from .db import SessionLocal
        from .models import Blog

        db = SessionLocal()
        try:
            rows = db.execute(
                select(Blog.name, Blog.url_pattern).where(Blog.is_active == True)
            ).all()
        finally:
            db.close()

        if not rows:
            return ""

        parts = []
        for name, url in rows[:5]:
            label = (name or "").strip() or (url or "").strip()
            if label:
                parts.append(label)
        more = max(len(rows) - 5, 0)
        s = ", ".join(parts)
        if more > 0:
            s += f" 외 {more}개"
        return s
    except Exception as e:
        print(f"[ALERT][BLOG READ FAIL] {e}")
        return ""

def send_alert(text: str) -> None:
    # 블로그 요약 라벨(있으면)만 계산하고, 실제 포함 여부는 SMS/LMS 판정에서 결정
    label = ""
    if ALERT_SHOW_BLOGS == "1":
        l = _monitored_blogs_label()
        if l:
            label = l

    if PROVIDER == "ALIGO_SMSG":
        # 오타 방지: 잘못된 PROVIDER가 들어올 수 있으므로 LOG로 fallback
        print(f"[ALERT][PROVIDER MISMATCH] fallback LOG: {text}")
        return

    if PROVIDER == "ALIGO_SMS":
        _send_aligo_sms(text, label)
    else:
        prefix = f"[대상 블로그] {label}\n" if label else ""
        print(f"[ALERT] {prefix}{text}")

def _digits_kr(num: str) -> str:
    # 010-1234-5678 → 01012345678
    return re.sub(r"\D", "", num or "")

def _sms_bytes(s: str) -> int:
    """
    SMS/LMS 구분을 위해 바이트 수를 계산.
    - 기본은 EUC-KR 기준(국내 통신사 80바이트 룰 대응)
    - 인코딩 불가 문자가 있으면 UTF-8 길이를 사용하여 보수적으로 판단
    """
    try:
        return len(s.encode("euc-kr"))
    except Exception:
        return len(s.encode("utf-8"))

def _send_aligo_sms(text: str, label: str = "") -> None:
    key = os.getenv("ALIGO_KEY", "")
    user_id = os.getenv("ALIGO_USER_ID", "")
    sender = _digits_kr(os.getenv("ALIGO_SENDER", ""))
    testmode = os.getenv("ALIGO_TESTMODE", "N").upper()
    force_lms = os.getenv("ALIGO_FORCE_LMS", "0") == "1"

    receivers = _resolve_receivers()

    if not (key and user_id and sender and receivers):
        # 설정이 안 되어 있으면 LOG로 대체 출력
        prefix = f"[대상 블로그] {label}\n" if label else ""
        print(f"[ALERT][ALIGO NOT CONFIGURED] {prefix}{text}")
        return

    # 본문 후보: 라벨 포함/미포함
    body_with_label = f"[대상 블로그] {label}\n{text}" if label else text
    bytes_with_label = _sms_bytes(body_with_label)
    bytes_plain = _sms_bytes(text)

    # 타입 결정: 바이트 기준 80 초과 → LMS (또는 강제 LMS)
    if force_lms or bytes_with_label > 80 or bytes_plain > 80:
        msg_type = "LMS"
        final_body = body_with_label
    else:
        # SMS일 땐 80바이트 초과 방지를 위해 라벨은 제외
        msg_type = "SMS"
        final_body = text

    payload = {
        "key": key,
        "user_id": user_id,
        "sender": sender,
        "receiver": ",".join(receivers),
        "msg": final_body,
        "msg_type": msg_type,                          # 미지정 시 자동 전환되지만, 명시적으로 지정
        "title": "네이버 모니터링" if msg_type == "LMS" else "",  # LMS 전용
        "testmode_yn": testmode,                       # Y 테스트 / N 실발송
    }

    print(f"[ALIGO] msg_type={msg_type} bytes≈{_sms_bytes(final_body)} (utf8≈{len(final_body.encode('utf-8'))}) receivers={len(receivers)}")

    import requests
    url = "https://apis.aligo.in/send/"
    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        j = r.json()
        # 성공: result_code == 1
        if str(j.get("result_code")) == "1":
            print(f"[ALIGO OK] queued ({len(receivers)} receivers)")
        else:
            print(f"[ALIGO ERROR] code={j.get('result_code')} msg={j.get('message')} body={j}")
    except Exception as e:
        print(f"[ALIGO EXC] {e}")