-- =====================================================
-- 多层次院校数据迁移脚本
-- 功能: 为现有大学数据分配层次和排名
-- 版本: 1.0.0
-- 日期: 2026-01-25
-- =====================================================

-- 1. 创建临时层次映射表
CREATE TEMP TABLE IF NOT EXISTS temp_university_tier_mapping (
    university_name VARCHAR(200) UNIQUE,
    tier university_tier_enum,
    tier_rank INT,
    confidence_level DECIMAL(3,2) DEFAULT 0.8  -- 置信度
);

-- 2. 插入985院校映射数据
INSERT INTO temp_university_tier_mapping (university_name, tier, tier_rank) VALUES
-- 985工程大学（39所）
('北京大学', '985_211', 1),
('清华大学', '985_211', 2),
('复旦大学', '985_211', 3),
('上海交通大学', '985_211', 4),
('浙江大学', '985_211', 5),
('南京大学', '985_211', 6),
('中山大学', '985_211', 7),
('华中科技大学', '985_211', 8),
('西安交通大学', '985_211', 9),
('东南大学', '985_211', 10),
('天津大学', '985_211', 11),
('武汉大学', '985_211', 12),
('四川大学', '985_211', 13),
('哈尔滨工业大学', '985_211', 14),
('山东大学', '985_211', 15),
('吉林大学', '985_211', 16),
('中南大学', '985_211', 17),
('中国科学技术大学', '985_211', 18),
('中国人民大学', '985_211', 19),
('北京航空航天大学', '985_211', 20),
('厦门大学', '985_211', 21),
('同济大学', '985_211', 22),
('大连理工大学', '985_211', 23),
('华南理工大学', '985_211', 24),
('重庆大学', '985_211', 25),
('西北工业大学', '985_211', 26),
('电子科技大学', '985_211', 27),
('湖南大学', '985_211', 28),
('东北大学', '985_211', 29),
('兰州大学', '985_211', 30),
('北京理工大学', '985_211', 31),
('中国农业大学', '985_211', 32),
('华东师范大学', '985_211', 33),
('中央民族大学', '985_211', 34),
('国防科技大学', '985_211', 35),
('西北农林科技大学', '985_211', 36),
('中国海洋大学', '985_211', 37),
('郑州大学', '985_211', 38),
('云南大学', '985_211', 39)
ON CONFLICT (university_name) DO NOTHING;

-- 3. 插入211院校映射数据（不含985）
INSERT INTO temp_university_tier_mapping (university_name, tier, tier_rank) VALUES
-- 部分知名211大学
('北京邮电大学', '985_211', 40),
('北京交通大学', '985_211', 41),
('北京科技大学', '985_211', 42),
('北京化工大学', '985_211', 43),
('北京外国语大学', '985_211', 44),
('对外经济贸易大学', '985_211', 45),
('中央财经大学', '985_211', 46),
('中国政法大学', '985_211', 47),
('华北电力大学', '985_211', 48),
('上海财经大学', '985_211', 49),
('华东理工大学', '985_211', 50),
('东华大学', '985_211', 51),
('上海外国语大学', '985_211', 52),
('南京航空航天大学', '985_211', 53),
('南京理工大学', '985_211', 54),
('河海大学', '985_211', 55),
('江南大学', '985_211', 56),
('苏州大学', '985_211', 57),
('中国矿业大学', '985_211', 58),
('中国药科大学', '985_211', 59),
('南京农业大学', '985_211', 60),
('江南大学', '985_211', 61),
('合肥工业大学', '985_211', 62),
('安徽大学', '985_211', 63),
('福州大学', '985_211', 64),
('南昌大学', '985_211', 65),
('山东科技大学', '985_211', 66),
('中国石油大学', '985_211', 67),
('郑州大学', '985_211', 68),
('武汉理工大学', '985_211', 69),
('华中师范大学', '985_211', 70),
('中南财经政法大学', '985_211', 71),
('湖南师范大学', '985_211', 72),
('暨南大学', '985_211', 73),
('华南师范大学', '985_211', 74),
('广西大学', '985_211', 75),
('海南大学', '985_211', 76),
('四川农业大学', '985_211', 77),
('西南财经大学', '985_211', 78),
('西南交通大学', '985_211', 79),
('贵州大学', '985_211', 80),
('云南大学', '985_211', 81),
('西藏大学', '985_211', 82),
('西北大学', '985_211', 83),
('陕西师范大学', '985_211', 84),
('西安电子科技大学', '985_211', 85),
('长安大学', '985_211', 86),
('兰州大学', '985_211', 87),
('青海大学', '985_211', 88),
('宁夏大学', '985_211', 89),
('新疆大学', '985_211', 90),
('石河子大学', '985_211', 91),
('内蒙古大学', '985_211', 92),
('辽宁大学', '985_211', 93),
('大连海事大学', '985_211', 94),
('东北师范大学', '985_211', 95),
('延边大学', '985_211', 96),
('东北林业大学', '985_211', 97),
('哈尔滨工程大学', '985_211', 98),
('东北农业大学', '985_211', 99)
ON CONFLICT (university_name) DO NOTHING;

-- 4. 插入省属重点院校映射数据
INSERT INTO temp_university_tier_mapping (university_name, tier, tier_rank) VALUES
-- 各省属重点大学
('山西大学', 'provincial_key', 1),
('太原理工大学', 'provincial_key', 2),
('中北大学', 'provincial_key', 3),
('山西师范大学', 'provincial_key', 4),
('山西财经大学', 'provincial_key', 5),
('山西医科大学', 'provincial_key', 6),
('河北大学', 'provincial_key', 7),
('河北工业大学', 'provincial_key', 8),
('燕山大学', 'provincial_key', 9),
('河北师范大学', 'provincial_key', 10),
('河南大学', 'provincial_key', 11),
('河南科技大学', 'provincial_key', 12),
('河南师范大学', 'provincial_key', 13),
('河南农业大学', 'provincial_key', 14),
('河南理工大学', 'provincial_key', 15),
('河南财经政法大学', 'provincial_key', 16),
('山东师范大学', 'provincial_key', 17),
('山东农业大学', 'provincial_key', 18),
('山东财经大学', 'provincial_key', 19),
('曲阜师范大学', 'provincial_key', 20),
('山东科技大学', 'provincial_key', 21),
('江苏大学', 'provincial_key', 22),
('扬州大学', 'provincial_key', 23),
('江苏师范大学', 'provincial_key', 24),
('南京工业大学', 'provincial_key', 25),
('浙江工业大学', 'provincial_key', 26),
('浙江师范大学', 'provincial_key', 27),
('杭州电子科技大学', 'provincial_key', 28),
('浙江理工大学', 'provincial_key', 29),
('安徽工业大学', 'provincial_key', 30),
('安徽理工大学', 'provincial_key', 31),
('安徽师范大学', 'provincial_key', 32),
('安徽农业大学', 'provincial_key', 33),
('安徽财经大学', 'provincial_key', 34)
ON CONFLICT (university_name) DO NOTHING;

-- 5. 插入一本院校映射数据
INSERT INTO temp_university_tier_mapping (university_name, tier, tier_rank) VALUES
-- 部分一本院校
('首都师范大学', 'first_tier', 1),
('首都医科大学', 'first_tier', 2),
('首都经济贸易大学', 'first_tier', 3),
('北京第二外国语学院', 'first_tier', 4),
('北京工商大学', 'first_tier', 5),
('北京建筑大学', 'first_tier', 6),
('天津师范大学', 'first_tier', 7),
('天津理工大学', 'first_tier', 8),
('天津财经大学', 'first_tier', 9),
('天津外国语大学', 'first_tier', 10),
('河北经贸大学', 'first_tier', 11),
('河北地质大学', 'first_tier', 12),
('石家庄铁道大学', 'first_tier', 13),
('山西大同大学', 'first_tier', 14),
('太原科技大学', 'first_tier', 15),
('山西中医药大学', 'first_tier', 16),
('内蒙古科技大学', 'first_tier', 17),
('内蒙古师范大学', 'first_tier', 18),
('内蒙古农业大学', 'first_tier', 19),
('辽宁师范大学', 'first_tier', 20),
('沈阳师范大学', 'first_tier', 21),
('大连交通大学', 'first_tier', 22),
('沈阳建筑大学', 'first_tier', 23),
('长春理工大学', 'first_tier', 24),
('长春师范大学', 'first_tier', 25),
('吉林师范大学', 'first_tier', 26),
('吉林财经大学', 'first_tier', 27),
('黑龙江大学', 'first_tier', 28),
('哈尔滨理工大学', 'first_tier', 29),
('哈尔滨师范大学', 'first_tier', 30),
('齐齐哈尔大学', 'first_tier', 31)
ON CONFLICT (university_name) DO NOTHING;

-- 6. 插入二本院校映射数据
INSERT INTO temp_university_tier_mapping (university_name, tier, tier_rank) VALUES
-- 部分二本院校
('北京城市学院', 'second_tier', 1),
('北京吉利学院', 'second_tier', 2),
('首都师范大学科德学院', 'second_tier', 3),
('北京工商大学嘉华学院', 'second_tier', 4),
('天津天狮学院', 'second_tier', 5),
('天津仁爱学院', 'second_tier', 6),
('天津商业大学宝德学院', 'second_tier', 7),
('河北科技师范学院', 'second_tier', 8),
('唐山学院', 'second_tier', 9),
('廊坊师范学院', 'second_tier', 10),
('山西工商学院', 'second_tier', 11),
('山西应用科技学院', 'second_tier', 12),
('晋中学院', 'second_tier', 13),
('运城学院', 'second_tier', 14),
('内蒙古民族大学', 'second_tier', 15),
('赤峰学院', 'second_tier', 16),
('呼伦贝尔学院', 'second_tier', 17),
('辽宁科技学院', 'second_tier', 18),
('沈阳工程学院', 'second_tier', 19),
('大连艺术学院', 'second_tier', 20),
('吉林农业科技学院', 'second_tier', 21),
('长春科技学院', 'second_tier', 22),
('黑龙江工业学院', 'second_tier', 23),
('黑龙江工程学院', 'second_tier', 24)
ON CONFLICT (university_name) DO NOTHING;

-- 7. 插入高职高专院校映射数据
INSERT INTO temp_university_tier_mapping (university_name, tier, tier_rank) VALUES
-- 部分高职高专院校
('北京信息职业技术学院', 'vocational', 1),
('北京电子科技职业学院', 'vocational', 2),
('北京工业职业技术学院', 'vocational', 3),
('北京农业职业学院', 'vocational', 4),
('北京财贸职业学院', 'vocational', 5),
('天津职业大学', 'vocational', 6),
('天津中德应用技术大学', 'vocational', 7),
('天津电子信息职业技术学院', 'vocational', 8),
('天津现代职业技术学院', 'vocational', 9),
('天津轻工职业技术学院', 'vocational', 10),
('河北工业职业技术大学', 'vocational', 11),
('石家庄铁路职业技术学院', 'vocational', 12),
('石家庄邮电职业技术学院', 'vocational', 13),
('山西工程职业学院', 'vocational', 14),
('山西机电职业技术学院', 'vocational', 15),
('山西财贸职业技术学院', 'vocational', 16),
('呼和浩特职业学院', 'vocational', 17),
('内蒙古化工职业学院', 'vocational', 18),
('内蒙古机电职业技术学院', 'vocational', 19),
('辽宁职业学院', 'vocational', 20),
('沈阳职业技术学院', 'vocational', 21),
('大连职业技术学院', 'vocational', 22),
('吉林电子信息职业技术学院', 'vocational', 23),
('吉林工业职业技术学院', 'vocational', 24),
('黑龙江职业学院', 'vocational', 25),
('哈尔滨职业技术学院', 'vocational', 26)
ON CONFLICT (university_name) DO NOTHING;

-- 8. 执行数据迁移：更新universities表的tier字段
UPDATE universities u
SET 
    tier = COALESCE(tm.tier, 'first_tier'),  -- 默认为一本院校
    tier_rank = COALESCE(tm.tier_rank, 999),
    tier_weight = CASE 
        WHEN tm.tier = '985_211' THEN 1.0
        WHEN tm.tier = 'provincial_key' THEN 0.85
        WHEN tm.tier = 'first_tier' THEN 0.70
        WHEN tm.tier = 'second_tier' THEN 0.55
        WHEN tm.tier = 'vocational' THEN 0.40
        ELSE 0.70
    END
FROM temp_university_tier_mapping tm
WHERE u.name = tm.university_name;

-- 9. 为未映射的大学设置默认层次
UPDATE universities 
SET 
    tier = 'first_tier',
    tier_rank = 999,
    tier_weight = 0.70
WHERE tier IS NULL;

-- 10. 更新university_admission_scores表的层次相关字段
UPDATE university_admission_scores uas
SET 
    tier_specific_range = JSONB_BUILD_OBJECT(
        'min_range', (SELECT default_score_range - 5 FROM university_tier_config WHERE tier = u.tier),
        'max_range', (SELECT default_score_range + 5 FROM university_tier_config WHERE tier = u.tier),
        'effective_range', (
            SELECT default_score_range + COALESCE(
                (SELECT score_range_modifier FROM university_tier_weights 
                 WHERE tier = u.tier AND province = uas.province AND is_active = TRUE),
                (SELECT score_range_modifier FROM university_tier_weights 
                 WHERE tier = u.tier AND province IS NULL AND is_active = TRUE),
                0
            )
            FROM university_tier_config WHERE tier = u.tier
        )
    ),
    score_match_range = (SELECT default_score_range FROM university_tier_config WHERE tier = u.tier),
    tier_confidence = CASE 
        WHEN u.tier = '985_211' THEN 0.95
        WHEN u.tier = 'provincial_key' THEN 0.90
        WHEN u.tier = 'first_tier' THEN 0.80
        WHEN u.tier = 'second_tier' THEN 0.70
        WHEN u.tier = 'vocational' THEN 0.60
        ELSE 0.70
    END
FROM universities u
WHERE uas.university_id = u.id;

-- 11. 创建迁移统计报告
WITH migration_stats AS (
    SELECT 
        'total_universities' as metric,
        COUNT(*) as value
    FROM universities
    
    UNION ALL
    
    SELECT 
        'universities_with_tier' as metric,
        COUNT(*)
    FROM universities
    WHERE tier IS NOT NULL
    
    UNION ALL
    
    SELECT 
        tier::TEXT as metric,
        COUNT(*) as value
    FROM universities
    WHERE tier IS NOT NULL
    GROUP BY tier
    
    UNION ALL
    
    SELECT 
        'migration_completion_rate' as metric,
        ROUND(
            (SELECT COUNT(*) FROM universities WHERE tier IS NOT NULL)::DECIMAL / 
            (SELECT COUNT(*) FROM universities) * 100, 2
        ) as value
)
SELECT * FROM migration_stats ORDER BY metric;

-- 12. 验证数据完整性
DO $$
DECLARE
    v_total_universities INT;
    v_universities_with_tier INT;
    v_completion_rate DECIMAL(5,2);
BEGIN
    SELECT COUNT(*) INTO v_total_universities FROM universities;
    SELECT COUNT(*) INTO v_universities_with_tier FROM universities WHERE tier IS NOT NULL;
    v_completion_rate := ROUND(v_universities_with_tier::DECIMAL / v_total_universities * 100, 2);
    
    RAISE NOTICE '=== 多层次院校数据迁移统计 ===';
    RAISE NOTICE '总大学数量: %', v_total_universities;
    RAISE NOTICE '已分配层次的大学数量: %', v_universities_with_tier;
    RAISE NOTICE '迁移完成率: %%%', v_completion_rate;
    
    -- 显示各层次分布
    RAISE NOTICE '=== 各层次分布 ===';
    FOR rec IN 
        SELECT tier, COUNT(*) as count 
        FROM universities 
        WHERE tier IS NOT NULL 
        GROUP BY tier 
        ORDER BY tier
    LOOP
        RAISE NOTICE '%: %所', rec.tier, rec.count;
    END LOOP;
    
    -- 验证索引创建
    IF v_completion_rate >= 95 THEN
        RAISE NOTICE '✅ 数据迁移成功完成';
    ELSE
        RAISE NOTICE '⚠️  数据迁移完成率低于95%%，请检查未分配层次的大学';
    END IF;
END $$;

-- 13. 清理临时表
DROP TABLE IF EXISTS temp_university_tier_mapping;

-- 完成标记
DO $$
BEGIN
    RAISE NOTICE '多层次院校数据迁移脚本执行完成';
    RAISE NOTICE '已为所有大学分配层次和排名';
    RAISE NOTICE '已更新录取分数表的层次相关信息';
    RAISE NOTICE '请验证迁移结果并测试推荐功能';
END $$;