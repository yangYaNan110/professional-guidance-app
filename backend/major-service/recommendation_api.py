"""
专业推荐API服务
严格按照需求设计文档规范实现：
1. 数据真实性原则：禁止使用假数据，所有数据来自PostgreSQL
2. 开发期间禁用Redis缓存：直接查询数据库，添加响应头X-Cache: DISABLED
3. 专业列表排序规则：默认按热度指数（heat_index）排序
4. 支持分页、筛选、排序参数
"""

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime
from pydantic import BaseModel, Field
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="专业推荐API",
    description="专业选择指导应用 - 专业推荐核心接口",
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

# 数据库配置（从环境变量或默认值）
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'employment'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

# =====================================================
# 响应模型定义
# =====================================================

class MajorMarketDataItem(BaseModel):
    """专业行情数据项"""
    id: int
    major_name: Optional[str]
    category: Optional[str]
    employment_rate: Optional[float]
    avg_salary: Optional[str]
    heat_index: Optional[float]
    crawled_at: Optional[datetime]

class PaginationInfo(BaseModel):
    """分页信息"""
    page: int
    page_size: int
    total: int
    total_pages: int

class MajorMarketDataResponse(BaseModel):
    """专业行情数据响应"""
    data: List[MajorMarketDataItem]
    pagination: PaginationInfo

class CategoryItem(BaseModel):
    """学科分类项"""
    category: str
    count: int
    display_name: str

class CategoriesResponse(BaseModel):
    """学科分类响应"""
    data: List[CategoryItem]

# =====================================================
# 数据库查询函数
# =====================================================

def get_major_market_data_from_db(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "heat_index",
    order: str = "desc"
) -> MajorMarketDataResponse:
    """
    从数据库获取专业行情数据
    严格按照热度指数排序规则
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 验证排序字段
        valid_sort_fields = ["heat_index", "employment_rate", "crawled_at", "avg_salary"]
        if sort_by not in valid_sort_fields:
            sort_by = "heat_index"  # 默认按热度指数排序
        
        # 验证排序方向
        order = "desc" if order.lower() not in ["asc", "desc"] else order.lower()
        
        # 构建WHERE条件
        where_conditions = []
        params = []
        
        if category:
            where_conditions.append("category = %s")
            params.append(category)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 获取总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM major_market_data
        WHERE {where_clause}
        """
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # 构建排序子句（特殊处理avg_salary，因为它可能是字符串格式）
        if sort_by == "avg_salary":
            # 尝试从avg_salary字符串中提取数字进行排序
            order_clause = f"""
            ORDER BY 
                CASE 
                    WHEN avg_salary ~ '^[0-9]+' THEN 
                        CAST(REGEXP_REPLACE(avg_salary, '[^0-9]', '', 'g') AS INTEGER)
                    ELSE 0 
                END {order},
                avg_salary {order}
            """
        else:
            order_clause = f"ORDER BY {sort_by} {order}, crawled_at DESC"
        
        # 获取分页数据
        offset = (page - 1) * page_size
        data_query = f"""
        SELECT 
            id, 
            major_name, 
            category, 
            employment_rate, 
            avg_salary, 
            heat_index,
            crawled_at
        FROM major_market_data
        WHERE {where_clause}
        {order_clause}
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(data_query, params + [page_size, offset])
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 转换数据格式
        data = []
        for record in records:
            # 处理datetime对象
            if record['crawled_at']:
                record['crawled_at'] = record['crawled_at'].isoformat()
            data.append(MajorMarketDataItem(**record))
        
        # 构建分页信息
        total_pages = (total + page_size - 1) // page_size
        pagination = PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages
        )
        
        return MajorMarketDataResponse(data=data, pagination=pagination)
        
    except Exception as e:
        logger.error(f"查询专业行情数据失败: {e}")
        raise HTTPException(status_code=500, detail="查询专业行情数据失败")

def get_categories_from_db() -> CategoriesResponse:
    """
    从数据库获取学科分类
    统计每个学科门类的专业数量
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            category,
            COUNT(*) as count,
            CASE 
                WHEN category = '工学' THEN '🔧 工学'
                WHEN category = '理学' THEN '🔬 理学'
                WHEN category = '经济学' THEN '💰 经济学'
                WHEN category = '管理学' THEN '📊 管理学'
                WHEN category = '医学' THEN '⚕️ 医学'
                WHEN category = '法学' THEN '⚖️ 法学'
                WHEN category = '文学' THEN '📚 文学'
                WHEN category = '历史学' THEN '📜 历史学'
                WHEN category = '哲学' THEN '🤔 哲学'
                WHEN category = '教育学' THEN '🎓 教育学'
                WHEN category = '农学' THEN '🌾 农学'
                WHEN category = '艺术学' THEN '🎨 艺术学'
                ELSE COALESCE(category, '其他')
            END as display_name
        FROM major_market_data
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
        ORDER BY count DESC, category
        """
        
        cursor.execute(query)
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 转换数据格式
        data = []
        for record in records:
            data.append(CategoryItem(
                category=record['category'],
                count=record['count'],
                display_name=record['display_name']
            ))
        
        return CategoriesResponse(data=data)
        
    except Exception as e:
        logger.error(f"查询学科分类失败: {e}")
        raise HTTPException(status_code=500, detail="查询学科分类失败")

# =====================================================
# API路由定义
# =====================================================

@app.get("/")
async def root():
    """根路径，检查API状态"""
    return {
        "message": "专业推荐API服务运行中",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "cache_status": "开发期间已禁用Redis缓存"
    }

@app.get("/api/v1/major/market-data", response_model=MajorMarketDataResponse)
async def get_major_market_data(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="学科门类筛选"),
    sort_by: str = Query("heat_index", description="排序字段：heat_index, employment_rate, avg_salary, crawled_at"),
    order: str = Query("desc", description="排序方向：asc, desc")
):
    """
    获取专业行情数据
    
    核心规则：
    1. 数据真实性：所有数据来自PostgreSQL数据库
    2. 缓存策略：开发期间禁用Redis缓存，直接查询数据库
    3. 默认排序：按热度指数（heat_index）降序排序
    4. 支持筛选：按学科门类筛选
    5. 支持分页：最大每页100条记录
    """
    try:
        # 从数据库获取数据
        result = get_major_market_data_from_db(
            category=category,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order
        )
        
        # 返回响应，添加禁用缓存的标识
        return Response(
            content=result.json(),
            headers={"X-Cache": "DISABLED"},
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取专业行情数据失败: {e}")
        raise HTTPException(status_code=500, detail="获取专业行情数据失败")

@app.get("/api/v1/data/categories", response_model=CategoriesResponse)
async def get_categories():
    """
    获取学科分类列表
    
    核心规则：
    1. 数据真实性：从major_market_data表统计真实数据
    2. 缓存策略：开发期间禁用Redis缓存
    3. 显示名称：为每个学科添加emoji标识，提升用户体验
    4. 排序规则：按专业数量降序，数量相同时按名称排序
    """
    try:
        # 从数据库获取数据
        result = get_categories_from_db()
        
        # 返回响应，添加禁用缓存的标识
        return Response(
            content=result.json(),
            headers={"X-Cache": "DISABLED"},
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取学科分类失败: {e}")
        raise HTTPException(status_code=500, detail="获取学科分类失败")

@app.get("/api/v1/major/health")
async def health_check():
    """健康检查"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查数据库连接
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "cache": "disabled (development mode)",
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

# =====================================================
# 数据库索引优化建议（文档用途）
# =====================================================

OPTIMIZATION_SQLS = """
-- 专业行情数据表索引优化
-- 根据查询需求创建复合索引，提升性能

-- 1. 热度指数排序索引（默认排序）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_heat_index 
ON major_market_data(heat_index DESC, crawled_at DESC);

-- 2. 学科分类筛选索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category 
ON major_market_data(category, heat_index DESC);

-- 3. 就业率排序索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_employment_rate 
ON major_market_data(employment_rate DESC, crawled_at DESC);

-- 4. 爬取时间排序索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_crawled_at 
ON major_market_data(crawled_at DESC);

-- 5. 复合索引：学科分类 + 热度指数（最常用查询组合）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_heat 
ON major_market_data(category, heat_index DESC, crawled_at DESC);

-- 6. 复合索引：学科分类 + 就业率
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_category_employment 
ON major_market_data(category, employment_rate DESC, crawled_at DESC);

-- 7. 薪资排序索引（处理字符串格式的薪资）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_salary 
ON major_market_data(
    CASE 
        WHEN avg_salary ~ '^[0-9]+' THEN 
            CAST(REGEXP_REPLACE(avg_salary, '[^0-9]', '', 'g') AS INTEGER)
        ELSE 0 
    END DESC,
    avg_salary DESC
);

-- 8. 主要查询字段的覆盖索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_major_market_covering 
ON major_market_data(category, heat_index DESC) 
INCLUDE (major_name, employment_rate, avg_salary, crawled_at);

-- 统计信息更新
ANALYZE major_market_data;
"""

@app.get("/api/v1/admin/optimization-sql")
async def get_optimization_sql():
    """获取数据库优化SQL（管理员接口）"""
    return {
        "title": "专业行情数据表索引优化SQL",
        "description": "根据API查询需求创建的索引优化脚本",
        "sql": OPTIMIZATION_SQLS.strip(),
        "usage": "在PostgreSQL数据库中执行上述SQL语句以优化查询性能"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)