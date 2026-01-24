-- =====================================================
-- 多层次院校数据库模型迁移脚本
-- 版本: 2.0.0
-- 日期: 2026-01-25
-- 功能: 为大学推荐模块设计多层次院校数据库模型
-- =====================================================

-- 1. 创建院校层次枚举类型
DO $$ BEGIN
    CREATE TYPE university_tier_enum AS ENUM (
        '985_211',        -- 985/211院校
        'provincial_key',  -- 省属重点院校
        'first_tier',     -- 一本院校
        'second_tier',    -- 二本院校
        'vocational'      -- 高职高专院校
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. 修改universities表，增加tier相关字段
ALTER TABLE universities 
ADD COLUMN IF NOT EXISTS tier university_tier_enum,
ADD COLUMN IF NOT EXISTS tier_rank INT DEFAULT 999,  -- 层次内排名
ADD COLUMN IF NOT EXISTS tier_weight DECIMAL(3,2) DEFAULT 1.0;  -- 层次权重

-- 3. 添加tier字段的数据约束
ALTER TABLE universities 
ADD CONSTRAINT IF NOT EXISTS chk_tier_rank 
    CHECK (tier_rank >= 1 AND tier_rank <= 999);

ALTER TABLE universities 
ADD CONSTRAINT IF NOT EXISTS chk_tier_weight 
    CHECK (tier_weight >= 0.1 AND tier_weight <= 10.0);

-- 4. 为universities表创建tier相关索引
CREATE INDEX IF NOT EXISTS idx_universities_tier ON universities(tier);
CREATE INDEX IF NOT EXISTS idx_universities_tier_rank ON universities(tier_rank);
CREATE INDEX IF NOT EXISTS idx_universities_tier_composite ON universities(tier, tier_rank);
CREATE INDEX IF NOT EXISTS idx_universities_province_tier ON universities(province, tier);
CREATE INDEX IF NOT EXISTS idx_universities_tier_emp ON universities(tier, employment_rate DESC);

-- 5. 修改university_admission_scores表，增加层次相关字段
ALTER TABLE university_admission_scores
ADD COLUMN IF NOT EXISTS tier_specific_range JSONB,
ADD COLUMN IF NOT EXISTS score_match_range INT DEFAULT 30,  -- 默认匹配范围±30分
ADD COLUMN IF NOT EXISTS tier_confidence DECIMAL(3,2) DEFAULT 1.0;  -- 层次置信度

-- 6. 为university_admission_scores表创建层次相关索引
CREATE INDEX IF NOT EXISTS idx_admission_tier_specific ON university_admission_scores USING gin(tier_specific_range);
CREATE INDEX IF NOT EXISTS idx_admission_score_range ON university_admission_scores(score_match_range);
CREATE INDEX IF NOT EXISTS idx_admission_composite_tier ON university_admission_scores(province, year, tier_specific_range);

-- 7. 创建院校层次配置表
CREATE TABLE IF NOT EXISTS university_tier_config (
    id SERIAL PRIMARY KEY,
    tier university_tier_enum NOT NULL UNIQUE,
    tier_name VARCHAR(50) NOT NULL,
    description TEXT,
    default_score_range INT NOT NULL,  -- 默认分数匹配范围
    min_score INT,  -- 该层次最低分数线
    max_score INT,  -- 该层次最高分数线
    tier_priority INT NOT NULL,  -- 层次优先级（数字越小优先级越高）
    recommendation_limit INT DEFAULT 5,  -- 推荐数量限制
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 8. 插入院校层次配置数据
INSERT INTO university_tier_config (tier, tier_name, description, default_score_range, tier_priority, recommendation_limit) VALUES
('985_211', '985/211院校', '国家重点建设的高水平大学，包含985工程和211工程院校', 20, 1, 3),
('provincial_key', '省属重点院校', '各省重点建设的大学，在区域内有较强影响力', 25, 2, 4),
('first_tier', '一本院校', '本科第一批次录取院校，教学质量较好', 30, 3, 5),
('second_tier', '二本院校', '本科第二批次录取院校，应用型人才培养为主', 35, 4, 6),
('vocational', '高职高专院校', '高等职业教育院校，注重技能培养', 40, 5, 8)
ON CONFLICT (tier) DO NOTHING;

-- 9. 创建院校层次权重表（动态配置）
CREATE TABLE IF NOT EXISTS university_tier_weights (
    id SERIAL PRIMARY KEY,
    tier university_tier_enum NOT NULL,
    province VARCHAR(50),  -- 省份特定的权重
    weight_factor DECIMAL(4,3) NOT NULL,  -- 权重因子
    score_range_modifier INT DEFAULT 0,  -- 分数范围修正值
    recommendation_boost DECIMAL(3,2) DEFAULT 1.0,  -- 推荐增强因子
    effective_date TIMESTAMP DEFAULT NOW(),
    expiry_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tier, province)
);

-- 10. 插入默认层次权重配置
INSERT INTO university_tier_weights (tier, province, weight_factor, score_range_modifier, recommendation_boost) VALUES
-- 全国通用权重
('985_211', NULL, 1.000, 0, 1.2),
('provincial_key', NULL, 0.850, 5, 1.1),
('first_tier', NULL, 0.700, 10, 1.0),
('second_tier', NULL, 0.550, 15, 0.9),
('vocational', NULL, 0.400, 20, 0.8)
ON CONFLICT (tier, province) DO NOTHING;

-- 11. 创建多层次推荐查询优化视图
CREATE OR REPLACE VIEW v_university_multitier_recommendation AS
WITH tier_config AS (
    SELECT 
        tier,
        tier_name,
        default_score_range,
        tier_priority,
        recommendation_limit
    FROM university_tier_config 
    WHERE is_active = TRUE
),
tier_weights AS (
    SELECT 
        tier,
        COALESCE(
            (SELECT weight_factor FROM university_tier_weights 
             WHERE uw.tier = tw.tier AND uw.province = tw.province AND is_active = TRUE),
            (SELECT weight_factor FROM university_tier_weights 
             WHERE uw.tier = tw.tier AND province IS NULL AND is_active = TRUE),
            1.0
        ) as weight_factor,
        COALESCE(
            (SELECT score_range_modifier FROM university_tier_weights 
             WHERE uw.tier = tw.tier AND uw.province = tw.province AND is_active = TRUE),
            (SELECT score_range_modifier FROM university_tier_weights 
             WHERE uw.tier = tw.tier AND province IS NULL AND is_active = TRUE),
            0
        ) as score_range_modifier
    FROM university_tier_weights uw
    CROSS JOIN (SELECT DISTINCT tier FROM university_tier_weights WHERE is_active = TRUE) tw
    GROUP BY tier
)
SELECT 
    u.id as university_id,
    u.name as university_name,
    u.province as university_province,
    u.city,
    u.employment_rate,
    u.tier,
    u.tier_rank,
    u.major_strengths,
    tc.tier_name,
    tc.tier_priority,
    tc.recommendation_limit,
    tw.weight_factor,
    tw.score_range_modifier,
    m.id as major_id,
    m.name as major_name,
    m.category_name,
    s.avg_score,
    s.year,
    s.province as admission_province,
    -- 动态计算分数匹配范围
    (tc.default_score_range + COALESCE(tw.score_range_modifier, 0)) as effective_score_range,
    -- 计算综合推荐分数
    (
        tc.tier_priority * 0.4 +  -- 层次优先级权重40%
        u.employment_rate * 0.3 +  -- 就业率权重30%
        COALESCE(m.heat_index, 0) * 0.2 +  -- 专业热度权重20%
        COALESCE(tw.weight_factor, 1.0) * 0.1  -- 动态权重因子10%
    ) as recommendation_score,
    -- 计算专业匹配度
    CASE 
        WHEN u.major_strengths @> ARRAY[m.name] THEN 100
        WHEN u.major_strengths && ARRAY[m.name] THEN 60
        ELSE 30
    END as major_match_score
FROM universities u
INNER JOIN tier_config tc ON u.tier = tc.tier
INNER JOIN tier_weights tw ON u.tier = tw.tier
LEFT JOIN majors m ON m.name IS NOT NULL
LEFT JOIN LATERAL (
    SELECT * FROM university_admission_scores 
    WHERE university_id = u.id 
    AND year >= EXTRACT(YEAR FROM NOW()) - 2
    ORDER BY year DESC, avg_score DESC
    LIMIT 1
) s ON true
WHERE u.tier IS NOT NULL;

-- 12. 创建多层次推荐函数
CREATE OR REPLACE FUNCTION get_multitier_university_recommendations(
    target_major VARCHAR(200),
    target_province VARCHAR(50) DEFAULT NULL,
    target_score DECIMAL(5,2) DEFAULT NULL,
    limit_per_tier INT DEFAULT 3
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    WITH ranked_universities AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY tier 
                ORDER BY 
                    tier_priority ASC,
                    major_match_score DESC,
                    recommendation_score DESC,
                    employment_rate DESC
            ) as tier_rank
        FROM v_university_multitier_recommendation
        WHERE 
            major_name = target_major
            AND (target_province IS NULL OR university_province = target_province)
            AND (
                target_score IS NULL 
                OR ABS(avg_score - target_score) <= effective_score_range
            )
    ),
    tiered_recommendations AS (
        SELECT 
            tier,
            tier_name,
            JSONB_AGG(
                JSONB_BUILD_OBJECT(
                    'university_id', university_id,
                    'university_name', university_name,
                    'province', university_province,
                    'city', city,
                    'tier_rank', tier_rank,
                    'employment_rate', employment_rate,
                    'avg_score', avg_score,
                    'major_match_score', major_match_score,
                    'recommendation_score', recommendation_score
                )
                ORDER BY major_match_score DESC, recommendation_score DESC
            ) FILTER (WHERE tier_rank <= limit_per_tier) as universities
        FROM ranked_universities
        WHERE tier_rank <= limit_per_tier
        GROUP BY tier, tier_name
        ORDER BY tier_priority
    )
    SELECT JSONB_OBJECT_AGG(tier_name, universities) INTO result
    FROM tiered_recommendations;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- 13. 创建触发器：自动更新university_admission_scores的tier_specific_range
CREATE OR REPLACE FUNCTION update_tier_specific_range()
RETURNS TRIGGER AS $$
BEGIN
    -- 自动计算并更新层次特定的分数范围
    UPDATE university_admission_scores 
    SET tier_specific_range = JSONB_BUILD_OBJECT(
        'min_range', 
        (SELECT default_score_range - 5 FROM university_tier_config WHERE tier = NEW.tier),
        'max_range', 
        (SELECT default_score_range + 5 FROM university_tier_config WHERE tier = NEW.tier),
        'effective_range', 
        (SELECT default_score_range + COALESCE(
            (SELECT score_range_modifier FROM university_tier_weights 
             WHERE tier = NEW.tier AND province = NEW.province AND is_active = TRUE),
            (SELECT score_range_modifier FROM university_tier_weights 
             WHERE tier = NEW.tier AND province IS NULL AND is_active = TRUE),
            0
        ) FROM university_tier_config WHERE tier = NEW.tier)
    )
    WHERE university_id = NEW.university_id AND major_id = NEW.major_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 14. 创建触发器
CREATE TRIGGER trigger_update_tier_specific_range
    AFTER INSERT OR UPDATE ON university_admission_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_tier_specific_range();

-- 15. 创建性能优化：分区表建议（用于大数据量场景）
-- 注意：这需要根据实际数据量和PostgreSQL版本启用
/*
-- 按年份分区university_admission_scores表
CREATE TABLE university_admission_scores_partitioned (
    LIKE university_admission_scores INCLUDING ALL
) PARTITION BY RANGE (year);

-- 创建分区表
CREATE TABLE university_admission_scores_2023 
    PARTITION OF university_admission_scores_partitioned 
    FOR VALUES FROM (2023) TO (2024);

CREATE TABLE university_admission_scores_2024 
    PARTITION OF university_admission_scores_partitioned 
    FOR VALUES FROM (2024) TO (2025);
*/

-- 16. 数据验证函数
CREATE OR REPLACE FUNCTION validate_university_tier_data()
RETURNS TABLE(validation_result JSONB) AS $$
BEGIN
    RETURN QUERY
    SELECT JSONB_BUILD_OBJECT(
        'validation_type', 'tier_data_completeness',
        'total_universities', COUNT(*),
        'universities_with_tier', COUNT(CASE WHEN tier IS NOT NULL THEN 1 END),
        'completion_rate', ROUND(
            COUNT(CASE WHEN tier IS NOT NULL THEN 1 END)::DECIMAL / COUNT(*) * 100, 2
        ),
        'tier_distribution', (
            SELECT JSONB_AGG(
                JSONB_BUILD_OBJECT(
                    tier::TEXT, COUNT(*)
                )
            )
            FROM universities
            WHERE tier IS NOT NULL
            GROUP BY tier
        )
    )
    FROM universities;
END;
$$ LANGUAGE plpgsql;

-- 17. 创建统计信息收集函数
CREATE OR REPLACE FUNCTION analyze_tier_recommendation_performance()
RETURNS TABLE(
    tier VARCHAR(20),
    total_recommendations BIGINT,
    avg_response_time DECIMAL(8,2),
    index_hit_rate DECIMAL(5,2)
) AS $$
BEGIN
    -- 这里需要结合实际的查询日志来统计
    -- 提供框架，实际使用时需要配合日志分析工具
    RETURN QUERY
    SELECT 
        tc.tier::VARCHAR,
        0::BIGINT,  -- 需要从查询日志获取
        0.0::DECIMAL,  -- 需要从查询日志获取
        0.0::DECIMAL   -- 需要从系统视图获取
    FROM university_tier_config tc
    WHERE tc.is_active = TRUE
    ORDER BY tc.tier_priority;
END;
$$ LANGUAGE plpgsql;

-- 18. 创建索引使用统计查询（用于性能监控）
CREATE OR REPLACE VIEW v_index_usage_stats AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    CASE 
        WHEN idx_scan = 0 THEN 0
        ELSE ROUND((idx_tup_fetch::DECIMAL / NULLIF(idx_scan, 0))::DECIMAL, 2)
    END as avg_tuples_per_scan
FROM pg_stat_user_indexes 
WHERE tablename IN ('universities', 'university_admission_scores', 'university_tier_config')
ORDER BY idx_scan DESC;

-- 19. 创建性能优化建议查询
CREATE OR REPLACE VIEW v_performance_optimization_suggestions AS
SELECT 
    'tier_specific_range索引' as optimization_item,
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_admission_tier_specific_gin 
     ON university_admission_scores USING gin(tier_specific_range);' as sql_suggestion,
    '提高层次特定范围查询性能' as description,
    'HIGH' as priority

UNION ALL

SELECT 
    '复合索引优化' as optimization_item,
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_universities_composite_recommendation 
     ON universities(province, tier, employment_rate DESC, tier_rank);' as sql_suggestion,
    '优化推荐查询的复合条件' as description,
    'HIGH' as priority

UNION ALL

SELECT 
    '分区表建议' as optimization_item,
    '考虑按年份分区university_admission_scores表' as sql_suggestion,
    '提高历史数据查询性能' as description,
    'MEDIUM' as priority;

-- 完成标记
DO $$
BEGIN
    RAISE NOTICE '多层次院校数据库模型迁移脚本执行完成';
    RAISE NOTICE '已创建多层次院校表结构';
    RAISE NOTICE '已创建院校层次配置和权重管理';
    RAISE NOTICE '已创建多层次推荐查询优化视图和函数';
    RAISE NOTICE '已创建性能监控和验证工具';
    
    -- 验证数据
    PERFORM validate_university_tier_data();
    
    RAISE NOTICE '数据验证完成，请检查输出结果';
END $$;