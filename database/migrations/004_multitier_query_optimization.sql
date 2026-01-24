-- =====================================================
-- 多层次院校推荐查询优化脚本
-- 功能: 针对多层次院校推荐的性能优化SQL
-- 目标: 查询性能<200ms，索引命中率>90%
-- 版本: 1.0.0
-- 日期: 2026-01-25
-- =====================================================

-- 1. 创建高性能复合索引
-- 针对多层次推荐查询的核心复合索引

-- universities表核心复合索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_universities_multitier_recommendation 
ON universities(province, tier, employment_rate DESC, tier_rank) 
WHERE tier IS NOT NULL;

-- 针对特定省份+层次的查询优化
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_universities_province_tier_score 
ON universities(province, tier, tier_rank) 
WHERE tier IS NOT NULL AND employment_rate > 70;

-- 针对全国推荐的查询优化
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_universities_tier_national 
ON universities(tier, employment_rate DESC, tier_rank) 
WHERE tier IS NOT NULL;

-- 2. university_admission_scores表复合索引
-- 针对分数+层次+省份的复合查询
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_admission_multitier_composite 
ON university_admission_scores(university_id, year DESC, province, avg_score) 
WHERE avg_score IS NOT NULL;

-- 针对层次特定范围查询的GIN索引优化
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_admission_tier_specific_gin 
ON university_admission_scores USING gin(tier_specific_range) 
WHERE tier_specific_range IS NOT NULL;

-- 针对分数匹配的优化索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_admission_score_match 
ON university_admission_scores(avg_score, province, year DESC) 
WHERE avg_score IS NOT NULL;

-- 3. university_tier_config和权重表的优化索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tier_config_priority_active 
ON university_tier_config(tier_priority) 
WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tier_weights_province_active 
ON university_tier_weights(tier, province) 
WHERE is_active = TRUE;

-- 4. 创建物化视图：预计算热门推荐结果
-- 这个视图可以显著提高常见查询的性能
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_popular_university_recommendations AS
WITH tier_priorities AS (
    SELECT 
        tier,
        tier_name,
        tier_priority,
        recommendation_limit
    FROM university_tier_config 
    WHERE is_active = TRUE
),
university_scores AS (
    SELECT 
        u.id as university_id,
        u.name as university_name,
        u.province,
        u.tier,
        u.employment_rate,
        u.tier_rank,
        m.name as major_name,
        m.category_name,
        s.avg_score,
        s.year,
        tc.tier_priority,
        -- 预计算推荐分数
        (
            tc.tier_priority * 0.4 + 
            u.employment_rate * 0.3 + 
            COALESCE(m.heat_index, 0) * 0.2 + 
            CASE 
                WHEN u.major_strengths @> ARRAY[m.name] THEN 1.0
                WHEN u.major_strengths && ARRAY[m.name] THEN 0.6
                ELSE 0.3
            END * 0.1
        ) as precomputed_score,
        -- 预计算专业匹配度
        CASE 
            WHEN u.major_strengths @> ARRAY[m.name] THEN 100
            WHEN u.major_strengths && ARRAY[m.name] THEN 60
            ELSE 30
        END as major_match_score
    FROM universities u
    INNER JOIN tier_priorities tc ON u.tier = tc.tier
    INNER JOIN majors m ON m.name IS NOT NULL
    LEFT JOIN LATERAL (
        SELECT * FROM university_admission_scores 
        WHERE university_id = u.id 
        AND year >= EXTRACT(YEAR FROM NOW()) - 2
        ORDER BY year DESC, avg_score DESC
        LIMIT 1
    ) s ON true
    WHERE u.tier IS NOT NULL
),
ranked_recommendations AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY tier, major_name 
            ORDER BY 
                precomputed_score DESC,
                major_match_score DESC,
                employment_rate DESC
        ) as tier_rank
    FROM university_scores
)
SELECT 
    university_id,
    university_name,
    province,
    tier,
    tier_priority,
    major_name,
    category_name,
    avg_score,
    major_match_score,
    precomputed_score,
    tier_rank
FROM ranked_recommendations
WHERE tier_rank <= 5  -- 每个层次取前5名
ORDER BY tier_priority, major_name, precomputed_score DESC;

-- 为物化视图创建索引
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_mv_popular_university_unique 
ON mv_popular_university_recommendations(university_id, major_name, tier);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mv_popular_university_search 
ON mv_popular_university_recommendations(major_name, tier_priority, precomputed_score DESC);

-- 5. 创建分区函数（用于大数据量场景）
-- 按年份动态创建分区的函数
CREATE OR REPLACE FUNCTION create_admission_score_partition(p_year INT)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    next_year INT;
BEGIN
    partition_name := 'university_admission_scores_' || p_year;
    next_year := p_year + 1;
    
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I 
        PARTITION OF university_admission_scores_partitioned 
        FOR VALUES FROM (%L) TO (%L)',
        partition_name, p_year, next_year
    );
    
    -- 为分区表创建必要的索引
    EXECUTE format('
        CREATE INDEX IF NOT EXISTS %I 
        ON %I (university_id, avg_score)',
        'idx_' || partition_name || '_composite', partition_name
    );
    
    RAISE NOTICE '已创建分区表: %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- 6. 创建智能查询缓存表
-- 缓存热门查询结果，避免重复计算
CREATE TABLE IF NOT EXISTS query_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    query_params JSONB NOT NULL,
    result_data JSONB NOT NULL,
    hit_count INT DEFAULT 0,
    last_hit_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_cache_key 
ON query_cache(cache_key) 
WHERE is_active = TRUE AND expires_at > NOW();

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_cache_hit_count 
ON query_cache(hit_count DESC) 
WHERE is_active = TRUE;

-- 7. 创建查询缓存管理函数
CREATE OR REPLACE FUNCTION get_cached_recommendation(
    p_cache_key VARCHAR(255),
    p_query_params JSONB,
    p_ttl_minutes INT DEFAULT 60
)
RETURNS JSONB AS $$
DECLARE
    cached_result JSONB;
    expired_time TIMESTAMP;
BEGIN
    expired_time := NOW() - (p_ttl_minutes || ' minutes')::INTERVAL;
    
    -- 尝试从缓存获取
    SELECT result_data INTO cached_result
    FROM query_cache 
    WHERE cache_key = p_cache_key 
    AND is_active = TRUE 
    AND created_at > expired_time;
    
    IF cached_result IS NOT NULL THEN
        -- 更新命中统计
        UPDATE query_cache 
        SET hit_count = hit_count + 1, last_hit_at = NOW()
        WHERE cache_key = p_cache_key;
        
        RETURN cached_result;
    END IF;
    
    RETURN NULL;  -- 缓存未命中
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cache_recommendation(
    p_cache_key VARCHAR(255),
    p_query_params JSONB,
    p_result_data JSONB,
    p_ttl_minutes INT DEFAULT 60
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO query_cache (
        cache_key, query_params, result_data, expires_at
    ) VALUES (
        p_cache_key, p_query_params, p_result_data, NOW() + (p_ttl_minutes || ' minutes')::INTERVAL
    )
    ON CONFLICT (cache_key) 
    DO UPDATE SET 
        result_data = EXCLUDED.result_data,
        expires_at = EXCLUDED.expires_at,
        created_at = NOW(),
        hit_count = 0;
END;
$$ LANGUAGE plpgsql;

-- 8. 优化后的多层次推荐查询函数
CREATE OR REPLACE FUNCTION get_optimized_multitier_recommendations(
    p_target_major VARCHAR(200),
    p_target_province VARCHAR(50) DEFAULT NULL,
    p_target_score DECIMAL(5,2) DEFAULT NULL,
    p_limit_per_tier INT DEFAULT 3,
    p_use_cache BOOLEAN DEFAULT TRUE
)
RETURNS JSONB AS $$
DECLARE
    cache_key VARCHAR(255);
    query_params JSONB;
    cached_result JSONB;
    result JSONB;
BEGIN
    -- 构建缓存键
    cache_key := md5(
        p_target_major || '|' || 
        COALESCE(p_target_province, 'NULL') || '|' ||
        COALESCE(p_target_score::TEXT, 'NULL') || '|' ||
        p_limit_per_tier::TEXT
    );
    
    -- 构建查询参数JSON
    query_params := JSONB_BUILD_OBJECT(
        'target_major', p_target_major,
        'target_province', p_target_province,
        'target_score', p_target_score,
        'limit_per_tier', p_limit_per_tier
    );
    
    -- 如果启用缓存，先尝试从缓存获取
    IF p_use_cache THEN
        cached_result := get_cached_recommendation(cache_key, query_params, 30);  -- 30分钟缓存
        IF cached_result IS NOT NULL THEN
            RETURN cached_result;
        END IF;
    END IF;
    
    -- 执行优化查询
    WITH tiered_universities AS (
        -- 首先从物化视图获取热门推荐
        SELECT * FROM mv_popular_university_recommendations
        WHERE major_name = p_target_major
        AND (p_target_province IS NULL OR province = p_target_province)
        AND (p_target_score IS NULL OR ABS(avg_score - p_target_score) <= 30)
        
        UNION ALL
        
        -- 补充从主表获取的实时数据
        SELECT 
            u.id as university_id,
            u.name as university_name,
            u.province,
            u.tier,
            tc.tier_priority,
            m.name as major_name,
            m.category_name,
            s.avg_score,
            CASE 
                WHEN u.major_strengths @> ARRAY[m.name] THEN 100
                WHEN u.major_strengths && ARRAY[m.name] THEN 60
                ELSE 30
            END as major_match_score,
            (
                tc.tier_priority * 0.4 + 
                u.employment_rate * 0.3 + 
                COALESCE(m.heat_index, 0) * 0.2 + 
                CASE 
                    WHEN u.major_strengths @> ARRAY[m.name] THEN 1.0
                    WHEN u.major_strengths && ARRAY[m.name] THEN 0.6
                    ELSE 0.3
                END * 0.1
            ) as precomputed_score,
            u.tier_rank
        FROM v_university_multitier_recommendation u
        INNER JOIN university_tier_config tc ON u.tier = tc.tier
        WHERE u.major_name = p_target_major
        AND (p_target_province IS NULL OR u.university_province = p_target_province)
        AND (p_target_score IS NULL OR ABS(u.avg_score - p_target_score) <= u.effective_score_range)
    ),
    ranked_results AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY tier 
                ORDER BY 
                    tier_priority ASC,
                    major_match_score DESC,
                    precomputed_score DESC,
                    employment_rate DESC
            ) as tier_rank
        FROM tiered_universities
    )
    SELECT JSONB_OBJECT_AGG(
        tier_name || '(' || tier::TEXT || ')',
        (
            SELECT JSONB_AGG(
                JSONB_BUILD_OBJECT(
                    'university_id', university_id,
                    'university_name', university_name,
                    'province', province,
                    'tier_rank', tier_rank,
                    'employment_rate', employment_rate,
                    'avg_score', avg_score,
                    'major_match_score', major_match_score,
                    'precomputed_score', precomputed_score
                )
                ORDER BY major_match_score DESC, precomputed_score DESC
            )
            FROM ranked_results r2
            WHERE r2.tier = r1.tier 
            AND tier_rank <= p_limit_per_tier
        )
    ) INTO result
    FROM (SELECT DISTINCT tier, tier_name FROM ranked_results) r1;
    
    -- 缓存结果
    IF p_use_cache AND result IS NOT NULL THEN
        PERFORM cache_recommendation(cache_key, query_params, result, 30);
    END IF;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- 9. 创建性能监控视图
CREATE OR REPLACE VIEW v_recommendation_performance_stats AS
WITH recent_queries AS (
    SELECT 
        cache_key,
        hit_count,
        created_at,
        last_hit_at,
        EXTRACT(EPOCH FROM (last_hit_at - created_at)) as age_seconds
    FROM query_cache 
    WHERE is_active = TRUE 
    AND created_at > NOW() - INTERVAL '24 hours'
)
SELECT 
    'cache_stats' as metric_type,
    COUNT(*) as total_cached_queries,
    COUNT(CASE WHEN hit_count > 0 THEN 1 END) as cache_hit_queries,
    ROUND(
        COUNT(CASE WHEN hit_count > 0 THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as cache_hit_rate_percent,
    AVG(hit_count) as avg_hit_count,
    MAX(hit_count) as max_hit_count,
    AVG(age_seconds) as avg_cache_age_seconds
FROM recent_queries

UNION ALL

SELECT 
    'index_usage' as metric_type,
    (SELECT COUNT(*) FROM pg_stat_user_indexes WHERE tablename = 'universities') as total_cached_queries,
    (SELECT COUNT(*) FROM pg_stat_user_indexes WHERE tablename = 'universities' AND idx_scan > 100) as cache_hit_queries,
    0 as cache_hit_rate_percent,
    0 as avg_hit_count,
    0 as max_hit_count,
    0 as avg_cache_age_seconds;

-- 10. 创建自动优化建议函数
CREATE OR REPLACE FUNCTION generate_optimization_recommendations()
RETURNS TABLE(
    recommendation_type TEXT,
    description TEXT,
    sql_command TEXT,
    priority TEXT,
    estimated_improvement TEXT
) AS $$
BEGIN
    RETURN QUERY
    -- 检查缓存命中率
    WITH cache_stats AS (
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN hit_count > 0 THEN 1 END) as hits
        FROM query_cache 
        WHERE is_active = TRUE 
        AND created_at > NOW() - INTERVAL '24 hours'
    )
    SELECT 
        'cache_optimization'::TEXT,
        '当前缓存命中率为 ' || ROUND((hits::DECIMAL / NULLIF(total, 0) * 100), 2) || '%'::TEXT,
        '建议增加缓存TTL或预热热门查询'::TEXT,
        CASE 
            WHEN (hits::DECIMAL / NULLIF(total, 0) * 100) < 70 THEN 'HIGH'
            WHEN (hits::DECIMAL / NULLIF(total, 0) * 100) < 85 THEN 'MEDIUM'
            ELSE 'LOW'
        END::TEXT,
        '提升查询响应速度30-50%'::TEXT
    FROM cache_stats
    
    UNION ALL
    
    -- 检查索引使用情况
    SELECT 
        'index_optimization'::TEXT,
        '检查并优化未使用的索引'::TEXT,
        'CREATE INDEX CONCURRENTLY idx_missing_index ON table_name(columns)'::TEXT,
        'MEDIUM'::TEXT,
        '提升查询速度20-40%'::TEXT
    
    UNION ALL
    
    -- 检查物化视图刷新需求
    SELECT 
        'materialized_view_refresh'::TEXT,
        '物化视图可能需要刷新以获取最新数据'::TEXT,
        'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_popular_university_recommendations'::TEXT,
        'MEDIUM'::TEXT,
        '确保数据新鲜度和查询准确性'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- 11. 创建定时任务清理缓存
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INT AS $$
DECLARE
    deleted_count INT;
BEGIN
    DELETE FROM query_cache 
    WHERE expires_at < NOW() 
    OR (created_at < NOW() - INTERVAL '7 days' AND hit_count < 5);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 12. 性能测试查询示例
-- 这些查询可以用于验证优化效果
/*
-- 测试查询性能
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT * FROM get_optimized_multitier_recommendations(
    '计算机科学与技术', 
    '山西省', 
    620.0, 
    3, 
    TRUE
);

-- 测试缓存效果
SELECT * FROM v_recommendation_performance_stats;

-- 获取优化建议
SELECT * FROM generate_optimization_recommendations();

-- 清理过期缓存
SELECT cleanup_expired_cache();
*/

-- 完成标记
DO $$
BEGIN
    RAISE NOTICE '多层次院校推荐查询优化脚本执行完成';
    RAISE NOTICE '已创建高性能复合索引';
    RAISE NOTICE '已创建物化视图预计算热门推荐';
    RAISE NOTICE '已创建智能查询缓存机制';
    RAISE NOTICE '已创建性能监控和优化建议工具';
    RAISE NOTICE '预期查询性能可提升至<200ms，索引命中率>90%';
    
    -- 验证索引创建
    RAISE NOTICE '=== 索引创建验证 ===';
    FOR rec IN 
        SELECT indexname, tablename 
        FROM pg_indexes 
        WHERE tablename IN ('universities', 'university_admission_scores', 'query_cache')
        AND indexname LIKE '%multitier%' OR indexname LIKE '%tier%'
        ORDER BY tablename, indexname
    LOOP
        RAISE NOTICE '已创建索引: % (表: %)', rec.indexname, rec.tablename;
    END LOOP;
END $$;