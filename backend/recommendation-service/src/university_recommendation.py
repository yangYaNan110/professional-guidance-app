"""大学推荐服务主应用"""
import psycopg2
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="大学推荐服务",
    description="专业选择指导应用 - 大学推荐服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接配置
DB_URL = "postgresql://postgres:postgres@localhost:5432/employment"

# Pydantic模型
class UniversityRecommendationRequest(BaseModel):
    major: str
    province: Optional[str] = None
    score: Optional[int] = None
    limit: Optional[int] = 10

class University(BaseModel):
    id: int
    name: str
    province: str
    city: Optional[str] = None
    level: Optional[str] = None
    employment_rate: Optional[float] = None
    website: Optional[str] = None
    match_score: Optional[float] = None
    match_reason: Optional[str] = None

class UniversityGroup(BaseModel):
    type: str  # province_score_match, national_score_match, province_match, national_match
    name: str
    count: int
    description: str
    universities: List[University]

class RecommendationResponse(BaseModel):
    success: bool
    scenario: str  # A, B, C
    total: int
    groups: Dict[str, Any]  # 动态分组

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

def determine_scenario(province: Optional[str], score: Optional[int], major: str) -> str:
    """确定推荐场景"""
    if province and score:
        return "A"  # 专业+省份+分数
    elif province:
        return "B"  # 专业+省份
    else:
        return "C"  # 只有专业

def calculate_major_match_score(target_major: str, university_majors: List[str]) -> float:
    """计算专业匹配度"""
    if not university_majors:
        return 0.3
    
    # 直接匹配
    if target_major in university_majors:
        return 1.0
    
    # 相关专业匹配
    related_majors = get_related_majors(target_major)
    for major in university_majors:
        if major in related_majors:
            return 0.8
    
    # 跨学科匹配
    cross_disciplinary = get_cross_disciplinary_majors(target_major)
    for major in university_majors:
        if major in cross_disciplinary:
            return 0.6
    
    # 兜底匹配
    return 0.3

def get_related_majors(major: str) -> List[str]:
    """获取相关专业列表"""
    engineering = ["人工智能", "计算机科学与技术", "软件工程", "数据科学", "电子信息工程", "自动化"]
    science = ["数学", "物理学", "化学", "生物学"]
    business = ["经济学", "金融学", "会计学", "工商管理", "市场营销"]
    medicine = ["临床医学", "口腔医学", "中医学", "药学", "护理学"]
    law = ["法学", "政治学与行政学", "国际政治", "社会学"]
    economics = ["经济学", "金融学", "会计学", "工商管理", "市场营销"]
    
    if major in engineering:
        return engineering + science
    elif major in business:
        return business + economics
    elif major in medicine:
        return medicine + science
    else:
        return engineering + business  # 默认返回工科+商科

def get_level_priority(level: str) -> int:
    """获取大学层次优先级"""
    mapping = {
        "985": 1,
        "211": 2, 
        "双一流": 3,
        "省属重点": 4,
        "普通本科": 5
    }
    return mapping.get(level, 6)

def recommend_scenario_a(major: str, province: str, score: int, limit: int) -> Dict[str, Any]:
    """场景A: 专业+省份+分数"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    score_range_min = score - 30
    score_range_max = score + 30
    
    try:
        # 同省分数段匹配
        cursor.execute("""
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
        """, (province, major, score_range_min, score_range_max, limit//2))
        
        province_results = cursor.fetchall()
        
        # 全国分数段匹配
        cursor.execute("""
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
        """, (major, score_range_min, score_range_max, province, limit//2))
        
        national_results = cursor.fetchall()
        
        # 格式化结果
        groups = {}
        
        if province_results:
            groups["province_score_match"] = {
                "name": "🏆 同省分数匹配大学",
                "count": len(province_results),
                "description": f"{province}省内录取分数{score_range_min}-{score_range_max}分段的高校",
                "universities": [format_university(row, major) for row in province_results]
            }
        
        if national_results:
            groups["national_score_match"] = {
                "name": "🌟 全国分数匹配大学", 
                "count": len(national_results),
                "description": f"全国范围内录取分数{score_range_min}-{score_range_max}分段的高校",
                "universities": [format_university(row, major) for row in national_results]
            }
        
        return {
            "success": True,
            "scenario": "A",
            "total": len(province_results) + len(national_results),
            "groups": groups
        }
        
    except Exception as e:
        logger.error(f"场景A推荐失败: {e}")
        raise HTTPException(status_code=500, detail="推荐服务暂时不可用")
    finally:
        cursor.close()
        conn.close()

def recommend_scenario_b(major: str, province: str, limit: int) -> Dict[str, Any]:
    """场景B: 专业+省份"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 同省优质大学
        cursor.execute("""
            SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
            FROM universities u
            WHERE u.province = %s
              AND u.major_strengths IS NOT NULL
              AND %s = ANY(u.major_strengths)
            ORDER BY u.level, u.employment_rate DESC
            LIMIT %s
        """, (province, major, limit//2))
        
        province_results = cursor.fetchall()
        
        # 全国推荐大学
        cursor.execute("""
            SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
            FROM universities u
            WHERE u.major_strengths IS NOT NULL
              AND %s = ANY(u.major_strengths)
              AND u.province != %s
            ORDER BY u.level, u.employment_rate DESC
            LIMIT %s
        """, (major, province, limit//2))
        
        national_results = cursor.fetchall()
        
        # 格式化结果
        groups = {}
        
        if province_results:
            groups["province_match"] = {
                "name": "📍 同省优质大学",
                "count": len(province_results),
                "description": f"{province}省内{major}专业的优质高校",
                "universities": [format_university(row, major) for row in province_results]
            }
        
        if national_results:
            groups["national_match"] = {
                "name": "🌟 全国推荐大学",
                "count": len(national_results), 
                "description": f"全国范围内{major}专业的优质高校",
                "universities": [format_university(row, major) for row in national_results]
            }
        
        return {
            "success": True,
            "scenario": "B",
            "total": len(province_results) + len(national_results),
            "groups": groups
        }
        
    except Exception as e:
        logger.error(f"场景B推荐失败: {e}")
        raise HTTPException(status_code=500, detail="推荐服务暂时不可用")
    finally:
        cursor.close()
        conn.close()

def recommend_scenario_c(major: str, limit: int) -> Dict[str, Any]:
    """场景C: 只有专业"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 全国推荐大学
        cursor.execute("""
            SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
            FROM universities u
            WHERE u.major_strengths IS NOT NULL
              AND %s = ANY(u.major_strengths)
            ORDER BY u.level, u.employment_rate DESC
            LIMIT %s
        """, (major, limit))
        
        national_results = cursor.fetchall()
        
        # 格式化结果
        groups = {}
        
        if national_results:
            groups["national_match"] = {
                "name": "🌟 全国推荐大学",
                "count": len(national_results),
                "description": f"全国范围内{major}专业的优质高校",
                "universities": [format_university(row, major) for row in national_results]
            }
        
        return {
            "success": True,
            "scenario": "C",
            "total": len(national_results),
            "groups": groups
        }
        
    except Exception as e:
        logger.error(f"场景C推荐失败: {e}")
        raise HTTPException(status_code=500, detail="推荐服务暂时不可用")
    finally:
        cursor.close()
        conn.close()

def format_university(row, major: str) -> Dict[str, Any]:
    """格式化大学信息"""
    university_majors = []
    if len(row) > 7:  # 如果有专业信息
        university_majors = [major]  # 简化处理，实际应从数据库获取
    
    match_score = calculate_major_match_score(major, university_majors)
    
    return {
        "id": row[0],
        "name": row[1],
        "province": row[2],
        "city": row[3],
        "level": row[4],
        "employment_rate": float(row[5]) if row[5] else None,
        "website": row[6],
        "match_score": match_score,
        "match_reason": f"专业匹配度: {match_score:.2f}"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "university-recommendation-service"}

@app.get("/api/v1/universities/recommend")
async def recommend_universities(
    major: str = Query(..., description="专业名称"),
    province: Optional[str] = Query(None, description="目标省份"),
    score: Optional[int] = Query(None, description="预估分数"),
    limit: Optional[int] = Query(10, description="推荐数量限制")
) -> RecommendationResponse:
    """获取推荐大学列表"""
    
    # 参数验证
    if not major or not major.strip():
        raise HTTPException(status_code=400, detail="专业名称不能为空")
    
    if score and (score < 400 or score > 750):
        raise HTTPException(status_code=400, detail="分数应在400-750之间")
    
    try:
        # 确定推荐场景
        scenario = determine_scenario(province, score, major)
        
        # 根据场景执行推荐
        if scenario == "A":
            return recommend_scenario_a(major, province, score, limit)
        elif scenario == "B":
            return recommend_scenario_b(major, province, limit)
        else:
            return recommend_scenario_c(major, limit)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推荐服务异常: {e}")
        raise HTTPException(status_code=500, detail="推荐服务暂时不可用")

@app.get("/api/v1/universities/{university_id}")
async def get_university_detail(university_id: int):
    """获取大学详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, province, city, level, employment_rate, website, 
                   major_strengths, description
            FROM universities
            WHERE id = %s
        """, (university_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="大学信息未找到")
        
        return {
            "success": True,
            "data": {
                "id": result[0],
                "name": result[1],
                "province": result[2],
                "city": result[3],
                "level": result[4],
                "employment_rate": float(result[5]) if result[5] else None,
                "website": result[6],
                "major_strengths": result[7] if len(result) > 7 else [],
                "description": result[8] if len(result) > 8 else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取大学详情失败: {e}")
        raise HTTPException(status_code=500, detail="服务暂时不可用")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)