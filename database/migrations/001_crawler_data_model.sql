-- =====================================================
-- 爬虫数据模块数据库迁移脚本
-- 版本: 1.0.0
-- 日期: 2026-01-23
-- =====================================================

-- 1. 学科分类表
CREATE TABLE IF NOT EXISTS major_categories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    parent_id INT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_major_categories_parent ON major_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_major_categories_code ON major_categories(code);

-- 2. 专业信息表
CREATE TABLE IF NOT EXISTS majors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    category_name VARCHAR(100),
    description TEXT,
    core_courses TEXT[],
    employment_rate DECIMAL(5,2),
    avg_salary VARCHAR(100),
    heat_index DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_majors_category ON majors(category_id);
CREATE INDEX IF NOT EXISTS idx_majors_name ON majors(name);
CREATE INDEX IF NOT EXISTS idx_majors_employment ON majors(employment_rate DESC);
CREATE INDEX IF NOT EXISTS idx_majors_heat ON majors(heat_index DESC);

ALTER TABLE majors ADD CONSTRAINT IF NOT EXISTS fk_majors_category 
    FOREIGN KEY (category_id) REFERENCES major_categories(id);

-- 3. 专业行情数据表
CREATE TABLE IF NOT EXISTS major_market_data (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    major_name VARCHAR(200),
    category VARCHAR(100),
    source_url VARCHAR(1000) UNIQUE,
    source_website VARCHAR(100),
    employment_rate DECIMAL(5,2),
    avg_salary VARCHAR(100),
    admission_score DECIMAL(5,2),
    heat_index DECIMAL(5,2),
    trend_data JSONB,
    description TEXT,
    courses JSONB,
    career_prospects TEXT,
    crawled_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_major_market_crawled ON major_market_data(crawled_at DESC);
CREATE INDEX IF NOT EXISTS idx_major_market_major_name ON major_market_data(major_name);
CREATE INDEX IF NOT EXISTS idx_major_market_category ON major_market_data(category);
CREATE INDEX IF NOT EXISTS idx_major_market_heat ON major_market_data(heat_index DESC);
CREATE INDEX IF NOT EXISTS idx_major_market_employment ON major_market_data(employment_rate DESC);
CREATE INDEX IF NOT EXISTS idx_major_market_category_heat ON major_market_data(category, heat_index DESC);

-- 4. 大学信息表
CREATE TABLE IF NOT EXISTS universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    level VARCHAR(50),
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50),
    employment_rate DECIMAL(5,2),
    type VARCHAR(50),
    location TEXT,
    founded_year INT,
    website VARCHAR(500),
    major_strengths TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_universities_province ON universities(province);
CREATE INDEX IF NOT EXISTS idx_universities_level ON universities(level);
CREATE INDEX IF NOT EXISTS idx_universities_employment ON universities(employment_rate DESC);
CREATE INDEX IF NOT EXISTS idx_universities_name ON universities(name);
CREATE INDEX IF NOT EXISTS idx_universities_province_emp ON universities(province, employment_rate DESC);

-- 5. 录取分数线表
CREATE TABLE IF NOT EXISTS university_admission_scores (
    id SERIAL PRIMARY KEY,
    university_id INT NOT NULL,
    university_name VARCHAR(200),
    major_id INT,
    major_name VARCHAR(200),
    year INT NOT NULL,
    min_score DECIMAL(5,2) NOT NULL,
    max_score DECIMAL(5,2),
    avg_score DECIMAL(5,2),
    province VARCHAR(50) NOT NULL,
    batch VARCHAR(50),
    enrollment_count INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admission_university ON university_admission_scores(university_id);
CREATE INDEX IF NOT EXISTS idx_admission_major ON university_admission_scores(major_id);
CREATE INDEX IF NOT EXISTS idx_admission_year ON university_admission_scores(year);
CREATE INDEX IF NOT EXISTS idx_admission_province ON university_admission_scores(province);
CREATE INDEX IF NOT EXISTS idx_admission_score ON university_admission_scores(min_score);
CREATE INDEX IF NOT EXISTS idx_admission_uni_year_prov ON university_admission_scores(university_id, year, province);

ALTER TABLE university_admission_scores ADD CONSTRAINT IF NOT EXISTS fk_admission_university 
    FOREIGN KEY (university_id) REFERENCES universities(id);
ALTER TABLE university_admission_scores ADD CONSTRAINT IF NOT EXISTS fk_admission_major 
    FOREIGN KEY (major_id) REFERENCES majors(id);

-- 6. 行业趋势数据表
CREATE TABLE IF NOT EXISTS industry_trends (
    id SERIAL PRIMARY KEY,
    industry_name VARCHAR(200) NOT NULL,
    trend_data JSONB NOT NULL,
    policy_change TEXT,
    salary_change VARCHAR(100),
    source VARCHAR(200),
    source_url VARCHAR(1000),
    publish_time TIMESTAMP,
    heat_index DECIMAL(5,2),
    crawled_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_industry_trends_name ON industry_trends(industry_name);
CREATE INDEX IF NOT EXISTS idx_industry_trends_time ON industry_trends(publish_time DESC);
CREATE INDEX IF NOT EXISTS idx_industry_trends_heat ON industry_trends(heat_index DESC);
CREATE INDEX IF NOT EXISTS idx_industry_trends_gin ON industry_trends USING gin(to_tsvector('simple', industry_name || ' ' || COALESCE(policy_change, '')));

-- 7. 视频内容表
CREATE TABLE IF NOT EXISTS video_content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    url VARCHAR(1000) NOT NULL UNIQUE,
    cover_url VARCHAR(1000),
    duration INT,
    view_count INT DEFAULT 0,
    author VARCHAR(200),
    publish_time TIMESTAMP,
    platform VARCHAR(50) NOT NULL,
    related_major VARCHAR(200),
    keywords TEXT[],
    heat_index DECIMAL(5,2),
    crawled_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_video_platform ON video_content(platform);
CREATE INDEX IF NOT EXISTS idx_video_major ON video_content(related_major);
CREATE INDEX IF NOT EXISTS idx_video_view ON video_content(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_video_heat ON video_content(heat_index DESC);
CREATE INDEX IF NOT EXISTS idx_video_publish ON video_content(publish_time DESC);
CREATE INDEX IF NOT EXISTS idx_video_keywords ON video_content USING gin(keywords);

-- 8. 爬取历史表
CREATE TABLE IF NOT EXISTS crawl_history (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL UNIQUE,
    task_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    crawled_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crawl_history_type ON crawl_history(task_type);
CREATE INDEX IF NOT EXISTS idx_crawl_history_status ON crawl_history(status);
CREATE INDEX IF NOT EXISTS idx_crawl_history_time ON crawl_history(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_crawl_history_recent ON crawl_history(start_time DESC)
    WHERE start_time > NOW() - INTERVAL '30 days';

-- 9. 爬取配额表
CREATE TABLE IF NOT EXISTS crawl_quota (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL UNIQUE,
    quota INT NOT NULL,
    priority INT NOT NULL,
    used_count INT DEFAULT 0,
    last_reset_time TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crawl_quota_priority ON crawl_quota(priority DESC);

-- =====================================================
-- 10. 热点资讯表
-- =====================================================
CREATE TABLE IF NOT EXISTS hot_news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    source VARCHAR(100) NOT NULL,
    source_url VARCHAR(1000),
    publish_time TIMESTAMP,
    related_major VARCHAR(200),
    category VARCHAR(100),
    view_count INT DEFAULT 0,
    heat_index DECIMAL(5,2) DEFAULT 0,
    crawled_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hot_news_crawled ON hot_news(crawled_at DESC);
CREATE INDEX IF NOT EXISTS idx_hot_news_heat ON hot_news(heat_index DESC);
CREATE INDEX IF NOT EXISTS idx_hot_news_major ON hot_news(related_major);
CREATE INDEX IF NOT EXISTS idx_hot_news_category ON hot_news(category);
CREATE INDEX IF NOT EXISTS idx_hot_news_source ON hot_news(source);
CREATE INDEX IF NOT EXISTS idx_hot_news_publish ON hot_news(publish_time DESC);

-- =====================================================
-- 初始数据：学科分类（12个一级学科）
-- =====================================================
INSERT INTO major_categories (code, name, parent_id, sort_order) VALUES
('01', '哲学', NULL, 1),
('02', '经济学', NULL, 2),
('03', '法学', NULL, 3),
('04', '教育学', NULL, 4),
('05', '文学', NULL, 5),
('06', '历史学', NULL, 6),
('07', '理学', NULL, 7),
('08', '工学', NULL, 8),
('09', '农学', NULL, 9),
('10', '医学', NULL, 10),
('11', '军事学', NULL, 11),
('12', '艺术学', NULL, 12)
ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- 初始数据：爬取配额
-- =====================================================
INSERT INTO crawl_quota (category, quota, priority, used_count) VALUES
('工学', 100, 10, 0),
('理学', 80, 9, 0),
('经济学', 80, 9, 0),
('管理学', 70, 8, 0),
('医学', 60, 7, 0),
('法学', 60, 7, 0),
('文学', 50, 6, 0),
('教育学', 50, 6, 0),
('艺术学', 40, 5, 0),
('哲学', 30, 4, 0),
('历史学', 30, 4, 0),
('农学', 30, 4, 0),
('军事学', 20, 3, 0)
ON CONFLICT (category) DO NOTHING;

-- 完成标记
DO $$
BEGIN
    RAISE NOTICE '数据库迁移脚本执行完成';
    RAISE NOTICE '已创建9张数据表';
    RAISE NOTICE '已初始化12个学科分类';
    RAISE NOTICE '已初始化13个爬取配额';
END $$;
