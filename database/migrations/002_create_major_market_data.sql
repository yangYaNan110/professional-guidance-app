-- 专业行情数据表 - 用于热度指数计算
-- 数据来源：各大招聘网站、教育部统计、行业报告

CREATE TABLE major_market_data (
    id SERIAL PRIMARY KEY,
    major_id INTEGER REFERENCES majors(id) ON DELETE CASCADE, -- 关联专业ID
    major_name VARCHAR(200) NOT NULL, -- 专业名称（冗余字段，便于查询）
    category_name VARCHAR(100), -- 学科门类名称
    
    -- 就业市场指标
    employment_rate DECIMAL(5,2), -- 就业率 (0-100%)
    avg_salary DECIMAL(10,2), -- 平均月薪（元）
    salary_growth_rate DECIMAL(5,2), -- 薪资增长率（%）
    employment_prospects TEXT, -- 就业前景描述
    
    -- 招生与报考指标
    admission_difficulty DECIMAL(5,2), -- 录取难度评分（1-10分）
    application_volume DECIMAL(10,0), -- 报考人数（近年平均）
    enrollment_growth_rate DECIMAL(5,2), -- 招生增长率（%）
    
    -- 行业发展趋势
    industry_demand_score DECIMAL(5,2), -- 行业需求评分（1-10分）
    future_prospects_score DECIMAL(5,2), -- 未来前景评分（1-10分）
    talent_shortage BOOLEAN DEFAULT FALSE, -- 是否人才短缺
    
    -- 热度指数与排名
    heat_index DECIMAL(5,2), -- 综合热度指数（1-100分）
    popularity_rank INTEGER, -- 人气排名
    employment_rank INTEGER, -- 就业排名
    salary_rank INTEGER, -- 薪资排名
    future_rank INTEGER, -- 前景排名
    
    -- 数据来源与时效性
    data_period VARCHAR(50), -- 数据统计周期（如：2023年度）
    data_source VARCHAR(100), -- 主要数据来源
    source_urls TEXT[], -- 相关数据来源URLs
    confidence_level DECIMAL(3,2), -- 数据置信度（0-1）
    
    -- 时间戳字段
    crawled_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 唯一约束：每个专业每个统计周期只能有一条记录
    UNIQUE(major_id, data_period)
);

-- 创建索引 - 优化查询性能
CREATE INDEX idx_major_market_data_major_id ON major_market_data(major_id);
CREATE INDEX idx_major_market_data_major_name ON major_market_data(major_name);
CREATE INDEX idx_major_market_data_category ON major_market_data(category_name);
CREATE INDEX idx_major_market_data_heat_index ON major_market_data(heat_index DESC);
CREATE INDEX idx_major_market_data_employment_rate ON major_market_data(employment_rate DESC);
CREATE INDEX idx_major_market_data_avg_salary ON major_market_data(avg_salary DESC);
CREATE INDEX idx_major_market_data_popularity_rank ON major_market_data(popularity_rank);
CREATE INDEX idx_major_market_data_crawled_at ON major_market_data(crawled_at DESC);

-- 添加约束条件
ALTER TABLE major_market_data ADD CONSTRAINT chk_employment_rate CHECK (employment_rate >= 0 AND employment_rate <= 100);
ALTER TABLE major_market_data ADD CONSTRAINT chk_avg_salary CHECK (avg_salary >= 0);
ALTER TABLE major_market_data ADD CONSTRAINT chk_score_ranges CHECK (
    admission_difficulty >= 1 AND admission_difficulty <= 10 AND
    industry_demand_score >= 1 AND industry_demand_score <= 10 AND
    future_prospects_score >= 1 AND future_prospects_score <= 10 AND
    heat_index >= 1 AND heat_index <= 100 AND
    confidence_level >= 0 AND confidence_level <= 1
);

-- 创建热度指数计算函数
CREATE OR REPLACE FUNCTION calculate_heat_index(
    p_employment_rate DECIMAL,
    p_avg_salary DECIMAL,
    p_salary_growth_rate DECIMAL,
    p_industry_demand_score DECIMAL,
    p_future_prospects_score DECIMAL,
    p_talent_shortage BOOLEAN
) RETURNS DECIMAL AS $$
DECLARE
    heat_score DECIMAL;
    salary_score DECIMAL;
    trend_score DECIMAL;
    demand_score DECIMAL;
BEGIN
    -- 热度指数计算公式
    -- 基础分：就业率 * 0.3 + 薪资水平评分 * 0.25 + 发展趋势 * 0.25 + 需求热度 * 0.2
    
    -- 薪资水平评分（1-100分）：月薪1万=20分，每增加1万+10分，最高60分
    salary_score := CASE 
        WHEN p_avg_salary <= 10000 THEN 20
        WHEN p_avg_salary <= 20000 THEN 20 + (p_avg_salary - 10000) / 1000
        WHEN p_avg_salary <= 50000 THEN 30 + (p_avg_salary - 20000) / 2000
        ELSE 60
    END;
    
    -- 发展趋势评分（1-100分）：结合前景评分和增长率
    trend_score := (p_future_prospects_score * 8 + 
                   COALESCE(p_salary_growth_rate, 0) * 2);
    
    -- 需求热度评分（1-100分）：行业需求 + 人才短缺加分
    demand_score := p_industry_demand_score * 8 + 
                   CASE WHEN p_talent_shortage THEN 20 ELSE 0 END;
    
    -- 综合热度指数
    heat_score := p_employment_rate * 0.3 + 
                  salary_score * 0.25 + 
                  trend_score * 0.25 + 
                  demand_score * 0.20;
    
    -- 确保结果在1-100范围内
    RETURN GREATEST(1, LEAST(100, heat_score));
END;
$$ LANGUAGE plpgsql;

-- 创建触发器：自动计算热度指数
CREATE OR REPLACE FUNCTION auto_calculate_heat_index()
RETURNS TRIGGER AS $$
BEGIN
    NEW.heat_index := calculate_heat_index(
        NEW.employment_rate,
        NEW.avg_salary,
        NEW.salary_growth_rate,
        NEW.industry_demand_score,
        NEW.future_prospects_score,
        NEW.talent_shortage
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_heat_index
    BEFORE INSERT OR UPDATE ON major_market_data
    FOR EACH ROW EXECUTE FUNCTION auto_calculate_heat_index();

-- 更新已存在记录的热度指数
UPDATE major_market_data SET 
    heat_index = calculate_heat_index(
        employment_rate,
        avg_salary,
        salary_growth_rate,
        industry_demand_score,
        future_prospects_score,
        talent_shortage
    )
WHERE heat_index IS NULL;

-- 添加触发器 - 自动更新 updated_at
CREATE TRIGGER update_major_market_data_updated_at 
    BEFORE UPDATE ON major_market_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加注释
COMMENT ON TABLE major_market_data IS '专业行情数据表 - 存储就业、薪资、发展前景等市场数据，用于热度指数计算';
COMMENT ON COLUMN major_market_data.heat_index IS '综合热度指数：基于就业率、薪资、发展趋势、需求热度的综合评分';
COMMENT ON COLUMN major_market_data.employment_rate IS '就业率：该专业毕业生的就业比例';
COMMENT ON COLUMN major_market_data.avg_salary IS '平均月薪：该专业毕业生的平均月薪（元）';
COMMENT ON COLUMN major_market_data.industry_demand_score IS '行业需求评分：1-10分，行业对该专业人才的需求程度';
COMMENT ON COLUMN major_market_data.future_prospects_score IS '未来前景评分：1-10分，该专业未来的发展前景';

-- 创建市场数据统计函数
CREATE OR REPLACE FUNCTION get_market_data_statistics()
RETURNS TABLE(
    total_majors BIGINT,
    avg_employment_rate DECIMAL,
    avg_salary DECIMAL,
    avg_heat_index DECIMAL,
    high_employment_count BIGINT,
    high_salary_count BIGINT,
    talent_shortage_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT,
        ROUND(AVG(employment_rate), 2),
        ROUND(AVG(avg_salary), 2),
        ROUND(AVG(heat_index), 2),
        COUNT(*) FILTER (WHERE employment_rate >= 90)::BIGINT,
        COUNT(*) FILTER (WHERE avg_salary >= 15000)::BIGINT,
        COUNT(*) FILTER (WHERE talent_shortage = TRUE)::BIGINT
    FROM major_market_data
    WHERE crawled_at >= NOW() - INTERVAL '1 year';
END;
$$ LANGUAGE plpgsql;