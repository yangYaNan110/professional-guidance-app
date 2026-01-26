"""推荐服务主应用"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import uvicorn
import psycopg2
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="推荐服务",
    description="就业指导应用 - 岗位推荐服务",
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

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    industry: Optional[str] = None

class RecommendationRequest(BaseModel):
    user_id: str
    limit: int = 10

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        # 在开发环境中，如果连接失败，可能需要适当处理或抛出异常
        raise e

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "recommendation-service"}

@app.get("/api/v1/recommendations")
async def get_recommendations(
    user_id: Optional[str] = Query(None, description="用户ID"),
    limit: int = Query(10, description="推荐数量")
):
    print(f"获取推荐职位列表: user_id={user_id}, limit={limit}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 优先查询 recommendations 表 (如果实现了推荐算法)
        # 这里暂时直接从 jobs 表查询作为 fallback
        query = """
            SELECT id, title, company, location, salary_min, salary_max, skills, industry 
            FROM jobs 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        recommendations = []
        for row in rows:
            # 处理 skills 字段，可能是 None 或 list
            skills = row[6]
            if skills is None:
                skills = []
            elif not isinstance(skills, list):
                # 如果是字符串或其他格式，尝试转换（视具体存储而定，psycopg2通常会自动处理json）
                skills = [] 

            recommendations.append({
                "job": {
                    "id": str(row[0]),
                    "title": row[1],
                    "company": row[2],
                    "location": row[3],
                    "salary_min": row[4],
                    "salary_max": row[5],
                    "skills": skills,
                    "industry": row[7]
                },
                "score": 0.85,  # 模拟分数，后续可接入真实算法
                "reason": "基于您的兴趣推荐"  # 模拟理由
            })
            
        return {
            "recommendations": recommendations,
            "total": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"获取推荐失败: {e}")
        # 如果数据库查询失败，返回空列表而不是报错，或者根据需求报错
        return {"recommendations": [], "total": 0, "error": str(e)}
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
