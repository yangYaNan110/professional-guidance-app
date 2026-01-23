-- =====================================================
-- 大学专业录取分数线数据库表设计
-- =====================================================

-- 1. 大学基本信息表
DROP TABLE IF EXISTS universities;
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,           -- 大学名称
    level VARCHAR(100),                   -- 985/211/双一流/普通
    province VARCHAR(50) NOT NULL,        -- 所在省份
    city VARCHAR(100),                    -- 所在城市
    type VARCHAR(50),                     -- 综合/理工/医学/师范/财经等
    employment_rate DECIMAL(5,2),         -- 就业率
    founded_year INT,                     -- 建校年份
    website VARCHAR(500),                 -- 官网
    major_strengths TEXT[],               -- 王牌专业列表（数组）
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_universities_province ON universities(province);
CREATE INDEX idx_universities_level ON universities(level);
CREATE INDEX idx_universities_name ON universities(name);

-- 2. 学科门类表
DROP TABLE IF EXISTS major_categories;
CREATE TABLE major_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,    -- 学科门类名称（工学、理学、医学等）
    description TEXT,                      -- 学科描述
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入学科门类数据
INSERT INTO major_categories (name, description) VALUES
('工学', '工程学科，包括计算机、电子、机械等'),
('理学', '基础科学，包括数学、物理、化学等'),
('医学', '医学类专业，包括临床医学、口腔医学等'),
('法学', '法律类专业，包括法学、知识产权等'),
('经济学', '经济管理类，包括金融学、会计学等'),
('文学', '语言文学类，包括汉语言文学、英语等'),
('教育学', '教育类专业，包括教育学、学前教育等'),
('农学', '农业类专业，包括农学、动物医学等'),
('历史学', '历史类专业，包括历史学、考古学等'),
('哲学', '哲学类专业，包括哲学、逻辑学等'),
('艺术学', '艺术类专业，包括音乐学、美术学等'),
('管理学', '管理类专业，包括工商管理、行政管理等');

-- 3. 专业信息表
DROP TABLE IF EXISTS majors;
CREATE TABLE majors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,           -- 专业名称
    category_id INT REFERENCES major_categories(id),  -- 学科门类
    category_name VARCHAR(100),           -- 冗余存储学科门类名称
    description TEXT,                     -- 专业介绍
    core_courses TEXT[],                  -- 核心课程
    employment_rate DECIMAL(5,2),         -- 就业率
    avg_salary VARCHAR(100),              -- 平均薪资
    heat_index DECIMAL(5,2),              -- 热度指数
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_majors_category ON majors(category_id);
CREATE INDEX idx_majors_name ON majors(name);
CREATE INDEX idx_majors_heat ON majors(heat_index DESC);

-- 4. 大学专业录取分数线表（核心表）
DROP TABLE IF EXISTS university_admission_scores;
CREATE TABLE university_admission_scores (
    id SERIAL PRIMARY KEY,
    university_id INT REFERENCES universities(id),  -- 大学ID
    university_name VARCHAR(200),          -- 冗余存储大学名称
    major_id INT REFERENCES majors(id),    -- 专业ID
    major_name VARCHAR(200),               -- 冗余存储专业名称
    province VARCHAR(50) NOT NULL,         -- 招生省份
    admission_type VARCHAR(50) NOT NULL,   -- 录取类型：本科一批、本科二批、专科批
    year INT NOT NULL,                     -- 年份
    min_score INT,                         -- 最低录取分
    max_score INT,                         -- 最高录取分
    avg_score DECIMAL(5,2),                -- 平均录取分
    enrollment_count INT,                  -- 招生人数
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_admission_university ON university_admission_scores(university_id);
CREATE INDEX idx_admission_major ON university_admission_scores(major_id);
CREATE INDEX idx_admission_province ON university_admission_scores(province);
CREATE INDEX idx_admission_type ON university_admission_scores(admission_type);
CREATE INDEX idx_admission_year ON university_admission_scores(year DESC);
CREATE INDEX idx_admission_composite ON university_admission_scores(province, admission_type, year DESC);

-- 5. 数据爬取记录表
DROP TABLE IF EXISTS crawl_history;
CREATE TABLE crawl_history (
    id SERIAL PRIMARY KEY,
    crawl_type VARCHAR(100) NOT NULL,     -- 爬取类型：university/major/admission_score
    source_website VARCHAR(200),           -- 数据来源网站
    status VARCHAR(50) DEFAULT 'pending',  -- 状态：pending/running/completed/failed
    records_fetched INT DEFAULT 0,         -- 获取记录数
    records_saved INT DEFAULT 0,           -- 保存记录数
    started_at TIMESTAMP,                  -- 开始时间
    completed_at TIMESTAMP,                -- 完成时间
    error_message TEXT,                    -- 错误信息
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. 数据更新调度表
DROP TABLE IF EXISTS update_scheduler;
CREATE TABLE update_scheduler (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,     -- 表名
    update_frequency VARCHAR(50) NOT NULL,-- 更新频率：daily/weekly/monthly
    last_update_time TIMESTAMP,            -- 上次更新时间
    next_update_time TIMESTAMP,            -- 下次更新时间
    is_active BOOLEAN DEFAULT TRUE,        -- 是否激活
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 插入调度任务
INSERT INTO update_scheduler (table_name, update_frequency, next_update_time) VALUES
('universities', 'weekly', NOW() + INTERVAL '7 days'),
('majors', 'monthly', NOW() + INTERVAL '30 days'),
('university_admission_scores', 'weekly', NOW() + INTERVAL '7 days');

-- 7. 创建视图：按省份和专业查询录取分数线
DROP VIEW IF EXISTS v_province_major_scores;
CREATE VIEW v_province_major_scores AS
SELECT 
    u.name as university_name,
    u.province as university_province,
    u.city,
    u.level,
    u.employment_rate,
    m.name as major_name,
    m.category_name,
    s.province as admission_province,
    s.admission_type,
    s.year,
    s.min_score,
    s.max_score,
    s.avg_score,
    s.enrollment_count
FROM university_admission_scores s
LEFT JOIN universities u ON s.university_id = u.id
LEFT JOIN majors m ON s.major_id = m.id
WHERE s.year >= EXTRACT(YEAR FROM NOW()) - 3;  -- 最近3年数据

-- 8. 创建视图：大学专业推荐视图（带专业匹配度）
DROP VIEW IF EXISTS v_university_recommendation;
CREATE VIEW v_university_recommendation AS
SELECT 
    u.id as university_id,
    u.name as university_name,
    u.province as university_province,
    u.city,
    u.level,
    u.employment_rate,
    u.major_strengths,
    m.id as major_id,
    m.name as major_name,
    m.category_name,
    m.heat_index as major_heat_index,
    s.min_score as latest_min_score,
    s.max_score as latest_max_score,
    s.province as score_province,
    s.year as score_year,
    -- 计算专业匹配度
    CASE 
        WHEN u.major_strengths @> ARRAY[m.name] THEN 100
        WHEN u.major_strengths && ARRAY[m.name] THEN 60
        ELSE 0
    END as major_match_score
FROM universities u
CROSS JOIN majors m
LEFT JOIN LATERAL (
    SELECT * FROM university_admission_scores 
    WHERE university_id = u.id AND year >= EXTRACT(YEAR FROM NOW()) - 1
    ORDER BY year DESC
    LIMIT 1
) s ON true
WHERE m.name IS NOT NULL;

-- 9. 触发器：自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_universities_updated_at
    BEFORE UPDATE ON universities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_majors_updated_at
    BEFORE UPDATE ON majors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admission_scores_updated_at
    BEFORE UPDATE ON university_admission_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
