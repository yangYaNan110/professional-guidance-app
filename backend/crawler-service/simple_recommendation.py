"""
简化版大学推荐服务
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional

class SimpleRecommendationService:
    def __init__(self):
        self.conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='employment',
            user='postgres',
            password='postgres'
        )
    
    def get_recommended_universities(
        self,
        province: Optional[str] = None,
        score: Optional[int] = None,
        major_name: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """
        简化版大学推荐逻辑
        """
        result = {
            "universities": [],
            "groups": {
                "score_match": None,
                "province_match": None,
                "national_match": None
            },
            "scenario": "unknown",
            "total": 0
        }
        
        if not major_name:
            return result
        
        # 确定场景
        if province and score:
            scenario = "A"
        elif province:
            scenario = "B"
        else:
            scenario = "C"
        
        result["scenario"] = scenario
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if scenario == "A":
                # 场景A：省份+分数+专业
                score_min = score - 30
                score_max = score + 30
                
                # 同省分数匹配
                cursor.execute("""
                    SELECT 
                        u.id as university_id,
                        u.name as university_name,
                        u.province as university_province,
                        u.city,
                        u.level,
                        u.employment_rate,
                        u.major_strengths,
                        s.min_score,
                        s.avg_score,
                        'score' as match_type,
                        '🏆 分数匹配大学' as match_reason
                    FROM universities u
                    CROSS JOIN majors m
                    LEFT JOIN university_admission_scores s ON u.id = s.university_id AND m.id = s.major_id
                    WHERE u.province = %s
                    AND m.name = %s
                    AND (s.min_score IS NULL OR (s.min_score >= %s AND s.min_score <= %s))
                    ORDER BY s.min_score DESC NULLS LAST
                    LIMIT %s
                """, (province, major_name, score_min, score_max, limit))
                
                score_match = cursor.fetchall()
                
                # 全国优质大学
                cursor.execute("""
                    SELECT 
                        u.id as university_id,
                        u.name as university_name,
                        u.province as university_province,
                        u.city,
                        u.level,
                        u.employment_rate,
                        u.major_strengths,
                        s.min_score,
                        s.avg_score,
                        'national' as match_type,
                        '🌟 全国推荐大学' as match_reason
                    FROM universities u
                    CROSS JOIN majors m
                    LEFT JOIN university_admission_scores s ON u.id = s.university_id AND m.id = s.major_id
                    WHERE m.name = %s
                    AND u.province != %s
                    AND (s.min_score IS NULL OR (s.min_score >= %s AND s.min_score <= %s))
                    ORDER BY u.level DESC, u.employment_rate DESC
                    LIMIT %s
                """, (major_name, province, score_min, score_max, limit))
                
                national_match = cursor.fetchall()
                
                result["universities"] = score_match + national_match
                result["groups"]["score_match"] = {
                    "name": "🏆 分数匹配大学",
                    "count": len(score_match),
                    "description": "录取分数在您预估分数±30分范围内的高校"
                } if score_match else None
                result["groups"]["national_match"] = {
                    "name": "🌟 全国推荐大学",
                    "count": len(national_match),
                    "description": "全国范围内该专业的优质高校"
                } if national_match else None
                
            elif scenario == "B":
                # 场景B：只有省份+专业
                cursor.execute("""
                    SELECT 
                        u.id as university_id,
                        u.name as university_name,
                        u.province as university_province,
                        u.city,
                        u.level,
                        u.employment_rate,
                        u.major_strengths,
                        'province' as match_type,
                        '📍 同省优质大学' as match_reason
                    FROM universities u
                    CROSS JOIN majors m
                    WHERE u.province = %s
                    AND m.name = %s
                    ORDER BY u.level DESC, u.employment_rate DESC
                    LIMIT %s
                """, (province, major_name, limit))
                
                province_match = cursor.fetchall()
                
                cursor.execute("""
                    SELECT 
                        u.id as university_id,
                        u.name as university_name,
                        u.province as university_province,
                        u.city,
                        u.level,
                        u.employment_rate,
                        u.major_strengths,
                        'national' as match_type,
                        '🌟 全国推荐大学' as match_reason
                    FROM universities u
                    CROSS JOIN majors m
                    WHERE m.name = %s
                    AND u.province != %s
                    ORDER BY u.level DESC, u.employment_rate DESC
                    LIMIT %s
                """, (major_name, province, limit))
                
                national_match = cursor.fetchall()
                
                result["universities"] = province_match + national_match
                result["groups"]["province_match"] = {
                    "name": "📍 同省优质大学",
                    "count": len(province_match),
                    "description": "您所在省份内该专业的优质高校"
                } if province_match else None
                result["groups"]["national_match"] = {
                    "name": "🌟 全国推荐大学",
                    "count": len(national_match),
                    "description": "全国范围内该专业的优质高校"
                } if national_match else None
                
            else:
                # 场景C：只有专业
                cursor.execute("""
                    SELECT 
                        u.id as university_id,
                        u.name as university_name,
                        u.province as university_province,
                        u.city,
                        u.level,
                        u.employment_rate,
                        u.major_strengths,
                        'national' as match_type,
                        '🌟 全国推荐大学' as match_reason
                    FROM universities u
                    CROSS JOIN majors m
                    WHERE m.name = %s
                    ORDER BY u.level DESC, u.employment_rate DESC
                    LIMIT %s
                """, (major_name, limit * 2))
                
                national_match = cursor.fetchall()
                
                result["universities"] = national_match
                result["groups"]["national_match"] = {
                    "name": "🌟 全国推荐大学",
                    "count": len(national_match),
                    "description": "全国范围内该专业的优质高校"
                } if national_match else None
        
        result["total"] = len(result["universities"])
        return result