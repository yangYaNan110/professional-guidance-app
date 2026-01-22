"""爬虫服务 - 专业行情数据爬取"""
import os
import sys
import logging
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_manager import MajorDataManager
from services.crawler import MajorDataCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

data_manager = MajorDataManager()
crawler = MajorDataCrawler()
crawl_tasks = {}

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("爬虫服务启动")
    yield
    logger.info("爬虫服务关闭")

app = FastAPI(
    title="爬虫服务",
    description="专业选择指导应用 - 专业行情数据爬取服务",
    version="1.0.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    for key, value in CORS_HEADERS.items():
        response.headers[key] = value
    return response

class CrawlRequest(BaseModel):
    force: bool = False

class CrawlResponse(BaseModel):
    task_id: str
    status: str
    message: str

class MarketDataItem(BaseModel):
    id: int
    major_name: Optional[str]
    category: Optional[str]
    source_website: Optional[str]
    employment_rate: Optional[float]
    avg_salary: Optional[str]
    heat_index: Optional[float]
    crawled_at: datetime
    title: str

class MarketDataListResponse(BaseModel):
    data: List[MarketDataItem]
    pagination: dict

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crawler-service"}

@app.get("/")
async def root():
    return {
        "message": "爬虫服务",
        "version": "1.0.0",
        "endpoints": {
            "触发爬取": "POST /api/v1/crawler/crawl",
            "爬取状态": "GET /api/v1/crawler/status/{task_id}",
            "行情数据": "GET /api/v1/major/market-data",
            "学科分类": "GET /api/v1/major/categories"
        }
    }

@app.post("/api/v1/crawler/crawl")
async def trigger_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    crawl_tasks[task_id] = {
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "records_crawled": 0,
        "records_saved": 0,
        "error_message": None
    }
    background_tasks.add_task(run_crawl_task, task_id, request.force)
    return CrawlResponse(
        task_id=task_id,
        status="started",
        message="爬虫任务已启动"
    )

async def run_crawl_task(task_id: str, force: bool = False):
    try:
        logger.info(f"开始执行爬虫任务: {task_id}")
        new_data = await crawler.crawl_all_sources()
        if not new_data:
            crawl_tasks[task_id]["status"] = "completed"
            crawl_tasks[task_id]["message"] = "未获取到新数据"
            return
        crawl_tasks[task_id]["records_crawled"] = len(new_data)
        saved_count = data_manager.save_crawled_data(new_data)
        crawl_tasks[task_id]["records_saved"] = saved_count
        crawl_tasks[task_id]["status"] = "completed"
        crawl_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"爬虫任务完成: 获取{len(new_data)}条，保存{saved_count}条")
    except Exception as e:
        logger.error(f"爬虫任务失败: {e}")
        crawl_tasks[task_id]["status"] = "failed"
        crawl_tasks[task_id]["error_message"] = str(e)

@app.get("/api/v1/crawler/status/{task_id}")
async def get_crawl_status(task_id: str):
    if task_id not in crawl_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    return crawl_tasks[task_id]

@app.get("/api/v1/crawler/quota")
async def get_quota_status():
    from services.quota_manager import quota_manager
    return quota_manager.get_quota_status()

@app.get("/api/v1/crawler/statistics")
async def get_crawler_statistics():
    from services.quota_manager import quota_manager
    return quota_manager.get_statistics()

@app.get("/api/v1/major/categories")
async def get_categories(limit: int = 10):
    from services.quota_manager import quota_manager
    categories = quota_manager.get_hot_categories(limit)
    return {"categories": categories, "total": len(categories)}

@app.get("/api/v1/major/market-data")
async def get_market_data(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    sort_by: str = "heat_index",
    order: str = "desc"
):
    try:
        data, total = data_manager.get_market_data(
            page=page, page_size=page_size, category=category, sort_by=sort_by, order=order
        )
        return MarketDataListResponse(
            data=data,
            pagination={
                "page": page, "page_size": page_size, "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"获取行情数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/major/market-data/stats")
async def get_market_stats():
    try:
        from services.quota_manager import quota_manager
        
        conn = data_manager._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as total FROM major_market_data")
        stats["total"] = cursor.fetchone()["total"]
        
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM major_market_data
            GROUP BY category
            ORDER BY count DESC
        ''')
        stats["by_category"] = [
            {"category": row["category"], "count": row["count"]}
            for row in cursor.fetchall()
        ]
        
        cursor.execute("SELECT MAX(crawled_at) as last_crawl FROM major_market_data")
        stats["last_crawl"] = cursor.fetchone()["last_crawl"]
        
        conn.close()
        
        stats["quota_status"] = quota_manager.get_quota_status()
        
        return stats
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/crawler/reset-and-seed")
async def reset_and_seed():
    """重置配额并补充所有学科数据（确保每学科至少10条）"""
    try:
        from services.quota_manager import quota_manager
        from services.data_manager import MajorDataManager
        from services.crawler import generate_mock_data
        
        # 创建新的 data_manager 实例
        data_manager = MajorDataManager()
        
        # 1. 重置配额计数
        quota_manager.reset_counts()
        logger.info("已重置配额计数")
        
        # 2. 获取所有需要补充数据的学科
        all_subjects = list(quota_manager.SUBJECT_QUOTAS.keys())
        
        # 3. 生成所有学科的模拟数据
        new_data = generate_mock_data(categories=all_subjects)
        logger.info(f"生成了 {len(new_data)} 条模拟数据")
        
        # 4. 保存数据
        saved_count = data_manager.save_crawled_data(new_data)
        
        return {
            "status": "success",
            "message": f"已补充数据，确保每学科至少10条",
            "data_generated": len(new_data),
            "data_saved": saved_count,
            "subjects_covered": all_subjects
        }
        
    except Exception as e:
        logger.error(f"补充数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("CRAWLER_PORT", "8004"))
    uvicorn.run(app, host="0.0.0.0", port=port)
