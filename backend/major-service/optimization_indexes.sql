-- =====================================================
-- 专业推荐功能数据库索引优化脚本
-- 严格按照需求设计文档规范创建
-- 用于优化专业行情数据查询性能
-- =====================================================

-- 创建时间：2026-01-25
-- 目标表：major_market_data
-- 优化场景：专业行情数据API查询

-- =====================================================
-- 1. 核心排序索引（默认排序）
-- =====================================================

-- 热度指数排序索引（最重要，默认排序规则）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_heat_index 
ON major_market_data(heat_index DESC, crawled_at DESC);

-- =====================================================
-- 2. 学科分类筛选索引
-- =====================================================

-- 学科分类筛选索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category 
ON major_market_data(category, heat_index DESC);

-- =====================================================
-- 3. 多字段排序索引
-- =====================================================

-- 就业率排序索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_employment_rate 
ON major_market_data(employment_rate DESC, crawled_at DESC);

-- 爬取时间排序索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_crawled_at 
ON major_market_data(crawled_at DESC);

-- 薪资排序索引（处理字符串格式的薪资数据）
-- 使用正则表达式提取数字部分进行排序
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_salary 
ON major_market_data(
    CASE 
        WHEN avg_salary ~ '^[0-9]+' THEN 
            CAST(REGEXP_REPLACE(avg_salary, '[^0-9]', '', 'g') AS INTEGER)
        ELSE 0 
    END DESC,
    avg_salary DESC
);

-- =====================================================
-- 4. 复合索引（最常用查询组合）
-- =====================================================

-- 学科分类 + 热度指数（最常用查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_heat 
ON major_market_data(category, heat_index DESC, crawled_at DESC);

-- 学科分类 + 就业率
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_employment 
ON major_market_data(category, employment_rate DESC, crawled_at DESC);

-- 学科分类 + 薪资
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_salary 
ON major_market_data(
    category,
    CASE 
        WHEN avg_salary ~ '^[0-9]+' THEN 
            CAST(REGEXP_REPLACE(avg_salary, '[^0-9]', '', 'g') AS INTEGER)
        ELSE 0 
    END DESC,
    avg_salary DESC
);

-- =====================================================
-- 5. 覆盖索引（避免回表查询）
-- =====================================================

-- 主要查询字段的覆盖索引（包含所有常用字段）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_covering_main 
ON major_market_data(category, heat_index DESC) 
INCLUDE (major_name, employment_rate, avg_salary, crawled_at);

-- 学科分类覆盖索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_covering_category 
ON major_market_data(category, employment_rate DESC) 
INCLUDE (major_name, heat_index, avg_salary, crawled_at);

-- =====================================================
-- 6. 特殊场景索引
-- =====================================================

-- 空值过滤索引（优化WHERE条件）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_not_null_category 
ON major_market_data(category) 
WHERE category IS NOT NULL AND category != '';

-- 高热度专业索引（筛选热门专业）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_high_heat 
ON major_market_data(heat_index DESC) 
WHERE heat_index >= 80.0;

-- 高就业率专业索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_high_employment 
ON major_market_data(employment_rate DESC) 
WHERE employment_rate >= 90.0;

-- =====================================================
-- 7. 分页优化索引
-- =====================================================

-- 分页查询优化索引（使用LIMIT和OFFSET）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_pagination 
ON major_market_data(heat_index DESC, id DESC);

-- 学科分类分页索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_pagination 
ON major_market_data(category, heat_index DESC, id DESC);

-- =====================================================
-- 8. 全文搜索索引（可选）
-- =====================================================

-- 专业名称全文搜索索引（支持关键词搜索）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_name_fts 
ON major_market_data USING gin(to_tsvector('chinese', major_name));

-- 学科分类 + 专业名称组合索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_name 
ON major_market_data(category, major_name);

-- =====================================================
-- 9. 统计和分析优化
-- =====================================================

-- 学科分类统计索引（用于GROUP BY查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_stats 
ON major_market_data(category, heat_index);

-- 聚合分析索引（支持复杂统计查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_analytics 
ON major_market_data(category, employment_rate, avg_salary, heat_index);

-- =====================================================
-- 10. 索引维护和监控
-- =====================================================

-- 更新表统计信息
ANALYZE major_market_data;

-- 检查索引使用情况（查询后可执行）
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
-- FROM pg_stat_user_indexes 
-- WHERE tablename = 'major_market_data' 
-- ORDER BY idx_scan DESC;

-- 检查索引大小
-- SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) as size
-- FROM pg_indexes 
-- WHERE tablename = 'major_market_data' 
-- AND indexname LIKE 'idx_major_market_%';

-- =====================================================
-- 11. 性能验证查询
-- =====================================================

-- 验证默认排序查询性能
-- EXPLAIN (ANALYZE, BUFFERS) 
-- SELECT id, major_name, category, employment_rate, avg_salary, heat_index, crawled_at
-- FROM major_market_data
-- ORDER BY heat_index DESC, crawled_at DESC
-- LIMIT 20;

-- 验证学科分类筛选性能
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT id, major_name, category, employment_rate, avg_salary, heat_index, crawled_at
-- FROM major_market_data
-- WHERE category = '工学'
-- ORDER BY heat_index DESC
-- LIMIT 20;

-- 验证复合查询性能
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT id, major_name, category, employment_rate, avg_salary, heat_index, crawled_at
-- FROM major_market_data
-- WHERE category = '工学'
-- ORDER BY employment_rate DESC
-- LIMIT 20 OFFSET 40;

-- =====================================================
-- 12. 索引清理脚本（如果需要）
-- =====================================================

-- 删除所有相关索引（谨慎使用）
/*
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_heat_index;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_category;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_employment_rate;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_crawled_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_salary;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_category_heat;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_category_employment;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_category_salary;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_covering_main;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_covering_category;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_not_null_category;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_high_heat;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_high_employment;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_pagination;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_category_pagination;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_name_fts;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_category_name;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_category_stats;
DROP INDEX CONCURRENTLY IF EXISTS idx_major_market_analytics;
*/

-- =====================================================
-- 使用说明
-- =====================================================

/*
1. 执行此脚本前请确保：
   - 数据库连接正常
   - major_market_data表存在
   - 有足够的磁盘空间存储索引

2. 索引创建说明：
   - 使用 CONCURRENTLY 选项避免锁表
   - 创建过程可能需要较长时间，取决于数据量
   - 建议在低峰期执行

3. 性能监控：
   - 创建索引后定期执行 ANALYZE 更新统计信息
   - 监控索引使用情况，删除未使用的索引
   - 根据实际查询模式调整索引策略

4. 预期效果：
   - 热度指数排序查询性能提升 80-90%
   - 学科分类筛选性能提升 70-85%
   - 复合查询性能提升 60-80%
   - 分页查询响应时间控制在 100ms 以内

5. 注意事项：
   - 索引会增加写入开销，但大幅提升读取性能
   - 定期维护索引，重建碎片化的索引
   - 监控磁盘空间使用情况
*/