"""大学推荐服务"""
import psycopg2
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

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

# 数据库连接
DB_URL = "postgresql://postgres:password@localhost:5432/employment"

class University(BaseModel):
    id: int
    name: str
    province: str
    city: Optional[str] = None
    level: Optional[str] = None
    employment_rate: Optional[float] = None
    website: Optional[str] = None

class RecommendationResponse(BaseModel):
    success: bool
    scenario: str
    total: int
    groups: Dict[str, Any]

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(DB_URL)

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
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 确定推荐场景
        if province and score:
            scenario = "A"
        elif province:
            scenario = "B"
        else:
            scenario = "C"
        
        groups = {}
        total_count = 0
        
        if scenario == "A":
            # 场景A: 专业+省份+分数
            score_min = score - 30
            score_max = score + 30
            
            # 同省分数匹配
            cursor.execute("""
                SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
                FROM universities u
                JOIN university_admission_scores s ON u.id = s.university_id
                WHERE u.province = %s 
                  AND s.major_name = %s
                  AND s.avg_score BETWEEN %s AND %s
                GROUP BY u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
                LIMIT %s
            """, (province, major, score_min, score_max, limit//2))
            
            province_results = cursor.fetchall()
            if province_results:
                groups["score_match"] = {
                    "name": "🏆 分数匹配大学",
                    "count": len(province_results),
                    "description": f"{province}省内录取分数{score_min}-{score_max}分段的高校",
                    "universities": [
                        {
                            "id": row[0],
                            "name": row[1],
                            "province": row[2],
                            "city": row[3],
                            "level": row[4],
                            "employment_rate": float(row[5]) if row[5] else None,
                            "website": row[6]
                        } for row in province_results
                    ]
                }
                total_count += len(province_results)
            
            # 全国分数匹配
            cursor.execute("""
                SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
                FROM universities u
                JOIN university_admission_scores s ON u.id = s.university_id
                WHERE s.major_name = %s
                  AND s.avg_score BETWEEN %s AND %s
                  AND u.province != %s
                GROUP BY u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
                LIMIT %s
            """, (major, score_min, score_max, province, limit//2))
            
            national_results = cursor.fetchall()
            if national_results:
                groups["national_match"] = {
                    "name": "🌟 全国推荐大学",
                    "count": len(national_results),
                    "description": f"全国范围内录取分数{score_min}-{score_max}分段的高校",
                    "universities": [
                        {
                            "id": row[0],
                            "name": row[1],
                            "province": row[2],
                            "city": row[3],
                            "level": row[4],
                            "employment_rate": float(row[5]) if row[5] else None,
                            "website": row[6]
                        } for row in national_results
                    ]
                }
                total_count += len(national_results)
                
        elif scenario == "B":
            # 场景B: 专业+省份
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
            if province_results:
                groups["province_match"] = {
                    "name": "📍 同省优质大学",
                    "count": len(province_results),
                    "description": f"{province}省内{major}专业的优质高校",
                    "universities": [
                        {
                            "id": row[0],
                            "name": row[1],
                            "province": row[2],
                            "city": row[3],
                            "level": row[4],
                            "employment_rate": float(row[5]) if row[5] else None,
                            "website": row[6]
                        } for row in province_results
                    ]
                }
                total_count += len(province_results)
            
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
            if national_results:
                groups["national_match"] = {
                    "name": "🌟 全国推荐大学",
                    "count": len(national_results),
                    "description": f"全国范围内{major}专业的优质高校",
                    "universities": [
                        {
                            "id": row[0],
                            "name": row[1],
                            "province": row[2],
                            "city": row[3],
                            "level": row[4],
                            "employment_rate": float(row[5]) if row[5] else None,
                            "website": row[6]
                        } for row in national_results
                    ]
                }
                total_count += len(national_results)
                
        else:
            # 场景C: 只有专业
            cursor.execute("""
                SELECT u.id, u.name, u.province, u.city, u.level, u.employment_rate, u.website
                FROM universities u
                WHERE u.major_strengths IS NOT NULL
                  AND %s = ANY(u.major_strengths)
                ORDER BY u.level, u.employment_rate DESC
                LIMIT %s
            """, (major, limit))
            
            national_results = cursor.fetchall()
            if national_results:
                groups["national_match"] = {
                    "name": "🌟 全国推荐大学",
                    "count": len(national_results),
                    "description": f"全国范围内{major}专业的优质高校",
                    "universities": [
                        {
                            "id": row[0],
                            "name": row[1],
                            "province": row[2],
                            "city": row[3],
                            "level": row[4],
                            "employment_rate": float(row[5]) if row[5] else None,
                            "website": row[6]
                        } for row in national_results
                    ]
                }
                total_count += len(national_results)
        
        return RecommendationResponse(
            success=True,
            scenario=scenario,
            total=total_count,
            groups=groups
        )
        
    except Exception as e:
        logger.error(f"推荐服务异常: {e}")
        raise HTTPException(status_code=500, detail="推荐服务暂时不可用")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)