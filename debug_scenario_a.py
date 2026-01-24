#!/usr/bin/env python3
"""调试场景A推荐逻辑"""
import sys
import os

# 添加项目根目录到路径
sys.path.append('/Users/yangyanan/yyn/opencode/08_demo/backend/recommendation-service/src')

import psycopg2

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="employment",
        user="postgres",
        password="postgres"
    )

def debug_scenario_a():
    """调试场景A推荐逻辑"""
    
    major = "计算机科学与技术"
    province = "江苏省" 
    score = 620
    limit = 5
    
    score_range_min = score - 100  # 扩大分数范围以获取更多结果
    score_range_max = score + 100
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print(f"=== 调试场景A推荐 ===")
        print(f"参数: major={major}, province={province}, score={score}, limit={limit}")
        print(f"分数范围: {score_range_min} - {score_range_max}")
        print()
        
        # 测试同省查询
        province_sql = """
            SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website,
                   AVG(avg_score) as avg_admission_score
            FROM universities u
            JOIN university_admission_scores s ON u.id = s.university_id
            WHERE u.province = %s 
              AND s.major_name = %s
              AND s.avg_score BETWEEN %s AND %s
              AND s.year = 2023
            GROUP BY u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
            ORDER BY u.level, avg_admission_score DESC
            LIMIT %s
        """
        
        print("执行同省查询SQL:")
        print(province_sql % (province, major, score_range_min, score_range_max, limit))
        print()
        
        cursor.execute(province_sql, (province, major, score_range_min, score_range_max, limit))
        province_results = cursor.fetchall()
        
        print(f"同省查询结果数量: {len(province_results)}")
        for i, row in enumerate(province_results):
            print(f"  {i+1}. {row[1]} - {row[2]} - 分数:{row[8]} - 层次:{row[4]}")
        print()
        
        # 测试全国查询
        national_sql = """
            SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website,
                   AVG(avg_score) as avg_admission_score
            FROM universities u
            JOIN university_admission_scores s ON u.id = s.university_id
            WHERE s.major_name = %s
              AND s.avg_score BETWEEN %s AND %s
              AND s.year = 2023
              AND u.province != %s
            GROUP BY u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
            ORDER BY u.level, avg_admission_score DESC
            LIMIT %s
        """
        
        print("执行全国查询SQL:")
        print(national_sql % (major, score_range_min, score_range_max, province, limit))
        print()
        
        cursor.execute(national_sql, (major, score_range_min, score_range_max, province, limit))
        national_results = cursor.fetchall()
        
        print(f"全国查询结果数量: {len(national_results)}")
        for i, row in enumerate(national_results):
            print(f"  {i+1}. {row[1]} - {row[2]} - 分数:{row[8]} - 层次:{row[4]}")
        print()
        
        # 构建结果
        groups = {}
        
        if province_results:
            groups["province_score_match"] = {
                "name": "🏆 同省分数匹配大学",
                "count": len(province_results),
                "description": f"{province}省内录取分数{score_range_min}-{score_range_max}分段的高校",
                "universities": [{"name": row[1], "level": row[4], "score": row[8]} for row in province_results]
            }
            print(f"✅ 同省分组构建成功: {len(province_results)}所大学")
        
        if national_results:
            groups["national_score_match"] = {
                "name": "🌟 全国分数匹配大学", 
                "count": len(national_results),
                "description": f"全国范围内录取分数{score_range_min}-{score_range_max}分段的高校",
                "universities": [{"name": row[1], "level": row[4], "score": row[8]} for row in national_results]
            }
            print(f"✅ 全国分组构建成功: {len(national_results)}所大学")
        
        final_result = {
            "success": True,
            "scenario": "A",
            "total": len(province_results) + len(national_results),
            "groups": groups
        }
        
        print("=== 最终结果 ===")
        print(f"总大学数: {final_result['total']}")
        print(f"分组数: {len(final_result['groups'])}")
        for key, group in final_result['groups'].items():
            print(f"  {key}: {group['name']} ({group['count']}所)")
        
        return final_result
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_scenario_a()