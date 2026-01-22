"""爬虫服务 - 专业行情数据爬取"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

# 添加shared模块到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.data_manager import MajorDataManager
from services.crawler import MajorDataCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

data_manager = MajorDataManager()
crawler = MajorDataCrawler()

# 爬取任务状态存储
crawl_tasks = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("爬虫服务启动")
    yield
    logger.info("爬虫服务关闭")

app = FastAPI(
    title="爬虫服务",
    description="专业选择指导应用 - 专业行情数据爬取服务",
    version="1.0.0",
    lifespan=lifespan
)

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
            "行情数据": "GET /api/v1/major/market-data"
        }
    }

@app.post("/api/v1/crawler/crawl")
async def trigger_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """触发爬虫任务"""
    task_id = str(uuid.uuid4())
    
    crawl_tasks[task_id] = {
        "status": "running",
        "started_at": datetime.utcnow(),
        "records_crawled": 0,
        "records_saved": 0,
        "error_message": None
    }
    
    background_tasks.add_task(run_crawl_task, task_id, request.force)
    
    return CrawlResponse(
        task_id=task_id,
        status="started",
        message="爬虫任务已启动，请使用task_id查询进度"
    )

async def run_crawl_task(task_id: str, force: bool = False):
    """执行爬虫任务"""
    try:
        logger.info(f"开始执行爬虫任务: {task_id}")
        
        # 执行爬取
        new_data = await crawler.crawl_all_sources()
        
        if not new_data:
            crawl_tasks[task_id]["status"] = "completed"
            crawl_tasks[task_id]["message"] = "未获取到新数据"
            return
        
        crawl_tasks[task_id]["records_crawled"] = len(new_data)
        
        # 保存数据（自动去重和数量限制）
        saved_count = data_manager.save_crawled_data(new_data)
        
        crawl_tasks[task_id]["records_saved"] = saved_count
        crawl_tasks[task_id]["status"] = "completed"
        crawl_tasks[task_id]["completed_at"] = datetime.utcnow()
        
        logger.info(f"爬虫任务完成: 获取{len(new_data)}条，保存{saved_count}条")
        
    except Exception as e:
        logger.error(f"爬虫任务失败: {e}")
        crawl_tasks[task_id]["status"] = "failed"
        crawl_tasks[task_id]["error_message"] = str(e)

@app.get("/api/v1/crawler/status/{task_id}")
async def get_crawl_status(task_id: str):
    """获取爬虫任务状态"""
    if task_id not in crawl_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return crawl_tasks[task_id]

@app.get("/api/v1/crawler/quota")
async def get_quota_status():
    """获取爬虫配额状态"""
    from services.quota_manager import quota_manager
    return quota_manager.get_quota_status()

@app.get("/api/v1/crawler/statistics")
async def get_crawler_statistics():
    """获取爬虫统计数据"""
    from services.quota_manager import quota_manager
    return quota_manager.get_statistics()

@app.get("/api/v1/major/market-data")
async def get_market_data(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    sort_by: str = "crawled_at",
    order: str = "desc"
):
    """获取专业行情数据"""
    try:
        data, total = data_manager.get_market_data(
            page=page,
            page_size=page_size,
            category=category,
            sort_by=sort_by,
            order=order
        )
        
        return MarketDataListResponse(
            data=data,
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"获取行情数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/major/market-data/stats")
async def get_market_stats():
    """获取行情数据统计"""
    try:
        stats = data_manager.get_stats()
        return stats
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("CRAWLER_PORT", "8004"))
    uvicorn.run(app, host="0.0.0.0", port=port)
