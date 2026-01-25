"""
专业信息API服务
提供专业分类、专业列表、专业详情等接口
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="专业信息API",
    description="专业选择指导应用 - 专业信息接口",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'employment',
    'user': 'postgres',
    'password': 'postgres'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

# 数据模型
class MajorCategory:
    """专业分类模型"""
    def __init__(self, id: int, name: str, code: str, level: int = 1, 
                 parent_id: Optional[int] = None, description: Optional[str] = None):
        self.id = id
        self.name = name
        self.code = code
        self.level = level
        self.parent_id = parent_id
        self.description = description

class Major:
    """专业模型"""
    def __init__(self, id: int, name: str, code: str, category_id: int,
                 description: Optional[str] = None, training_objective: Optional[str] = None,
                 main_courses: Optional[List[str]] = None, employment_direction: Optional[str] = None,
                 study_period: int = 4, degree_awarded: Optional[str] = None,
                 national_key_major: bool = False, source_url: Optional[str] = None):
        self.id = id
        self.name = name
        self.code = code
        self.category_id = category_id
        self.description = description
        self.training_objective = training_objective
        self.main_courses = main_courses
        self.employment_direction = employment_direction
        self.study_period = study_period
        self.degree_awarded = degree_awarded
        self.national_key_major = national_key_major
        self.source_url = source_url

@app.get("/")
async def root():
    """根路径，检查API状态"""
    return {
        "message": "专业信息API服务运行中",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/majors/categories")
async def get_major_categories():
    """
    获取专业分类列表
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT id, name, code, level, parent_id, description, sort_order
        FROM major_categories
        ORDER BY sort_order, id
        """
        
        cursor.execute(query)
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 转换为字典列表
        result = [dict(cat) for cat in categories]
        
        return result
        
    except Exception as e:
        logger.error(f"获取专业分类失败: {e}")
        raise HTTPException(status_code=500, detail="获取专业分类失败")

@app.get("/api/v1/majors")
async def get_majors(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category_id: Optional[int] = Query(None, description="专业分类ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取专业列表（支持分页、筛选、搜索）
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if category_id:
            where_conditions.append("m.category_id = %s")
            params.append(category_id)
        
        if keyword:
            where_conditions.append("(m.name ILIKE %s OR m.description ILIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 获取总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM majors m
        WHERE {where_clause}
        """
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # 获取分页数据
        offset = (page - 1) * page_size
        data_query = f"""
        SELECT 
            m.id, m.name, m.code, m.category_id, m.description,
            m.study_period, m.degree_awarded, m.national_key_major,
            m.source_url, m.crawled_at,
            c.name as category_name, c.code as category_code
        FROM majors m
        LEFT JOIN major_categories c ON m.category_id = c.id
        WHERE {where_clause}
        ORDER BY m.id
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(data_query, params + [page_size, offset])
        majors = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 转换为字典列表
        result = [dict(major) for major in majors]
        
        return {
            "success": True,
            "data": result,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error(f"获取专业列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取专业列表失败")

@app.get("/api/v1/majors/{major_id}")
async def get_major_detail(major_id: int):
    """
    获取专业详情
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 获取专业详情
        query = """
        SELECT 
            m.id, m.name, m.code, m.category_id, m.description,
            m.training_objective, m.main_courses, m.employment_direction,
            m.study_period, m.degree_awarded, m.national_key_major,
            m.discipline_level, m.source_url, m.source_website,
            m.crawled_at, m.updated_at,
            c.name as category_name, c.code as category_code
        FROM majors m
        LEFT JOIN major_categories c ON m.category_id = c.id
        WHERE m.id = %s
        """
        
        cursor.execute(query, (major_id,))
        major = cursor.fetchone()
        
        if not major:
            raise HTTPException(status_code=404, detail="专业不存在")
        
        cursor.close()
        conn.close()
        
        # 转换为字典
        result = dict(major)
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取专业详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取专业详情失败")

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)