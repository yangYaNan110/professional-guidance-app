-- 专业信息模块数据库表结构
-- 确保数据真实性：所有数据必须来自权威网站，支持URL追溯

-- 1. 专业分类表
-- 数据来源：阳光高考专业分类体系
CREATE TABLE major_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- 分类名称（如：工学、理学、文学）
    code VARCHAR(20) UNIQUE, -- 分类代码（教育部标准代码）
    parent_id INTEGER REFERENCES major_categories(id), -- 父分类ID，支持层级结构
    level INTEGER DEFAULT 1, -- 分类层级：1-学科门类，2-学科大类，3-专业类
    sort_order INTEGER DEFAULT 0, -- 排序顺序
    description TEXT, -- 分类描述
    source_url VARCHAR(500), -- 数据来源URL，确保可追溯
    source_website VARCHAR(100), -- 来源网站（如：阳光高考）
    crawled_at TIMESTAMP DEFAULT NOW(), -- 爬取时间
    updated_at TIMESTAMP DEFAULT NOW() -- 更新时间
);

-- 2. 专业信息表
-- 数据来源：阳光高考专业库、各高校官网
CREATE TABLE majors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL, -- 专业名称
    code VARCHAR(20) UNIQUE, -- 专业代码（教育部标准代码）
    category_id INTEGER REFERENCES major_categories(id), -- 所属专业分类ID
    description TEXT, -- 专业介绍
    training_objective TEXT, -- 培养目标
    main_courses TEXT[], -- 主干课程数组
    employment_direction TEXT, -- 就业方向
    study_period INTEGER DEFAULT 4, -- 学制年限
    degree_awarded VARCHAR(50), -- 授予学位
    national_key_major BOOLEAN DEFAULT FALSE, -- 是否国家重点专业
    discipline_level VARCHAR(50), -- 学科等级（如：一级学科、二级学科）
    
    -- 数据真实性追溯字段
    source_url VARCHAR(500) UNIQUE, -- 数据来源URL，确保可追溯
    source_website VARCHAR(100), -- 来源网站
    crawl_batch_id VARCHAR(50), -- 爬取批次ID
    
    -- 状态字段
    status INTEGER DEFAULT 1, -- 状态：1-有效，0-无效
    quality_score DECIMAL(3,2), -- 数据质量评分（0-1）
    
    crawled_at TIMESTAMP DEFAULT NOW(), -- 爬取时间
    updated_at TIMESTAMP DEFAULT NOW() -- 更新时间
);

-- 创建索引 - 优化查询性能
-- major_categories表索引
CREATE INDEX idx_major_categories_parent_id ON major_categories(parent_id);
CREATE INDEX idx_major_categories_code ON major_categories(code);
CREATE INDEX idx_major_categories_level ON major_categories(level);

-- majors表索引
CREATE INDEX idx_majors_category_id ON majors(category_id);
CREATE INDEX idx_majors_code ON majors(code);
CREATE INDEX idx_majors_name ON majors USING gin(to_tsvector('english', name));
CREATE INDEX idx_majors_status ON majors(status);
CREATE INDEX idx_majors_source_website ON majors(source_website);
CREATE INDEX idx_majors_crawled_at ON majors(crawled_at DESC);

-- 创建全文搜索索引 - 支持英文搜索
CREATE INDEX idx_majors_fulltext ON majors USING gin(
    to_tsvector('english', 
        COALESCE(name, '') || ' ' || 
        COALESCE(description, '') || ' ' || 
        COALESCE(employment_direction, '')
    )
);

-- 添加约束条件
ALTER TABLE major_categories ADD CONSTRAINT chk_categories_level CHECK (level >= 1 AND level <= 3);
ALTER TABLE majors ADD CONSTRAINT chk_majors_study_period CHECK (study_period >= 1 AND study_period <= 8);
ALTER TABLE majors ADD CONSTRAINT chk_majors_quality_score CHECK (quality_score >= 0 AND quality_score <= 1);
ALTER TABLE majors ADD CONSTRAINT chk_majors_status CHECK (status IN (0, 1));

-- 添加触发器 - 自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_major_categories_updated_at 
    BEFORE UPDATE ON major_categories 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_majors_updated_at 
    BEFORE UPDATE ON majors 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加注释
COMMENT ON TABLE major_categories IS '专业分类表 - 存储学科门类、学科大类、专业类信息';
COMMENT ON TABLE majors IS '专业信息表 - 存储专业详细信息，数据来源必须可追溯';

-- 数据质量检查函数
CREATE OR REPLACE FUNCTION check_data_quality()
RETURNS TABLE(
    table_name TEXT,
    issue_type TEXT,
    issue_count BIGINT,
    description TEXT
) AS $$
BEGIN
    -- 检查分类表数据质量
    RETURN QUERY
    SELECT 
        'major_categories'::TEXT as table_name,
        'missing_source_url'::TEXT as issue_type,
        COUNT(*)::BIGINT as issue_count,
        '分类缺少数据来源URL'::TEXT as description
    FROM major_categories 
    WHERE source_url IS NULL OR source_url = '';
    
    -- 检查专业表数据质量
    RETURN QUERY
    SELECT 
        'majors'::TEXT as table_name,
        'missing_source_url'::TEXT as issue_type,
        COUNT(*)::BIGINT as issue_count,
        '专业缺少数据来源URL'::TEXT as description
    FROM majors 
    WHERE source_url IS NULL OR source_url = '';
    
    RETURN QUERY
    SELECT 
        'majors'::TEXT as table_name,
        'invalid_category_reference'::TEXT as issue_type,
        COUNT(*)::BIGINT as issue_count,
        '专业引用了不存在的分类'::TEXT as description
    FROM majors m 
    LEFT JOIN major_categories c ON m.category_id = c.id 
    WHERE m.category_id IS NOT NULL AND c.id IS NULL;
END;
$$ LANGUAGE plpgsql;