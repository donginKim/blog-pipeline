-- PostgreSQL 데이터베이스 초기화 스크립트

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 키워드 테이블
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 블로그 테이블
CREATE TABLE IF NOT EXISTS blogs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url_pattern VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 키워드-블로그 타겟 테이블
CREATE TABLE IF NOT EXISTS keyword_targets (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    blog_id INTEGER NOT NULL REFERENCES blogs(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keyword_id, blog_id)
);

-- 크롤링 실행 기록 테이블
CREATE TABLE IF NOT EXISTS crawl_runs (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE SET NULL,
    blog_id INTEGER REFERENCES blogs(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- 크롤링 결과 테이블
CREATE TABLE IF NOT EXISTS crawl_results (
    id SERIAL PRIMARY KEY,
    crawl_run_id INTEGER REFERENCES crawl_runs(id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    rank INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    blog_name VARCHAR(200),
    section VARCHAR(100),
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 설정 테이블
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_blogs_url_pattern ON blogs(url_pattern);
CREATE INDEX IF NOT EXISTS idx_keyword_targets_keyword_id ON keyword_targets(keyword_id);
CREATE INDEX IF NOT EXISTS idx_keyword_targets_blog_id ON keyword_targets(blog_id);
CREATE INDEX IF NOT EXISTS idx_crawl_runs_status ON crawl_runs(status);
CREATE INDEX IF NOT EXISTS idx_crawl_runs_started_at ON crawl_runs(started_at);
CREATE INDEX IF NOT EXISTS idx_crawl_results_crawl_run_id ON crawl_results(crawl_run_id);
CREATE INDEX IF NOT EXISTS idx_crawl_results_keyword ON crawl_results(keyword);
CREATE INDEX IF NOT EXISTS idx_crawl_results_rank ON crawl_results(rank);
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);

-- 기본 데이터 삽입

-- 기본 사용자 (비밀번호: admin123)
INSERT INTO users (username, email, hashed_password, is_active) 
VALUES ('admin', 'admin@example.com', 'admin123', TRUE)
ON CONFLICT (username) DO NOTHING;

-- 기본 설정
INSERT INTO settings (key, value) 
VALUES 
    ('notification_settings', '{"enabled": false, "phone": "", "notify_on_success": true, "notify_on_error": true}'),
    ('schedule_settings', '{"enabled": false, "time": "09:00", "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]}')
ON CONFLICT (key) DO NOTHING;

-- 트리거: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '✅ 데이터베이스 초기화 완료!';
    RAISE NOTICE '📋 기본 계정: username=admin, password=admin123';
END $$;

