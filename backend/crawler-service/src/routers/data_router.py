"""
爬虫数据模块API路由
日期: 2026-01-23

数据流规则：
1. 爬虫Agent负责数据采集，写入PostgreSQL数据库
2. 后端API只从数据库或Redis缓存读取数据
3. 前端通过API获取数据，后端不直接爬取数据
4. Redis缓存层减少数据库压力
"""

from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional
import sys
import os
import uuid
import httpx
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.crawler_data_service import CrawlerDataService, DatabaseConfig
from services.redis_cache_service import RedisCacheService, CacheKeyBuilder
from models.database import (
    MajorListResponse, UniversityListResponse, MajorMarketDataListResponse,
    AdmissionScoreListResponse, IndustryTrendListResponse,
    VideoContentListResponse, CrawlHistoryListResponse, CrawlQuotaListResponse,
    HotNewsListResponse
)

router = APIRouter(prefix="/api/v1/data", tags=["爬虫数据"])

# 初始化数据服务
data_service = CrawlerDataService(DatabaseConfig())

# 初始化缓存服务
cache_service = RedisCacheService()


# =====================================================
# 缓存辅助函数
# =====================================================

def get_cache_headers(key: str) -> dict:
    """生成缓存响应头"""
    ttl = cache_service._get_ttl(key)
    return {
        "X-Cache-TTL": str(ttl),
        "X-Cache-Key": key
    }


# =====================================================
# 学科分类API（带缓存）
# =====================================================

@router.get("/categories")
async def get_categories(parent_id: Optional[int] = None):
    """获取学科分类列表（从数据库读取，支持Redis缓存）"""
    try:
        # 构建缓存键
        cache_key = CacheKeyBuilder.categories()
        
        # 尝试从缓存读取
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return Response(
                content=str(cached_data),
                headers={**get_cache_headers(cache_key), "X-Cache": "HIT"},
                media_type="application/json"
            )
        
        # 从数据库读取
        categories = data_service.get_categories(parent_id)
        result = {"data": categories, "total": len(categories)}
        
        # 写入缓存
        cache_service.set(cache_key, result)
        
        return Response(
            content=str(result),
            headers={**get_cache_headers(cache_key), "X-Cache": "MISS"},
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/{category_id}")
async def get_category(category_id: int):
    """获取学科分类详情（从数据库读取）"""
    try:
        category = data_service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="学科分类不存在")
        return category
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 专业API（带缓存）
# =====================================================

@router.get("/majors", response_model=MajorListResponse)
async def get_majors(
    category_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取专业列表（从数据库读取，支持Redis缓存）"""
    try:
        # 构建缓存键
        cache_key = CacheKeyBuilder.majors_list(page, str(category_id) if category_id else None)
        
        # 尝试从缓存读取
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库读取
        result = data_service.get_majors(category_id, page, page_size)
        
        # 写入缓存
        cache_service.set(cache_key, result.dict())
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/majors/{major_id}")
async def get_major(major_id: int):
    """获取专业详情（从数据库读取）"""
    try:
        major = data_service.get_major_by_id(major_id)
        if not major:
            raise HTTPException(status_code=404, detail="专业不存在")
        return major
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 专业行情数据API（带缓存）
# =====================================================

@router.get("/market-data", response_model=MajorMarketDataListResponse)
async def get_market_data(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取专业行情数据列表（从数据库读取，支持Redis缓存）"""
    try:
        # 构建缓存键
        cache_key = f"market-data:{category or 'all'}:{page}:{page_size}"
        
        # 尝试从缓存读取
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库读取
        result = data_service.get_major_market_data(category, page, page_size)
        
        # 写入缓存
        cache_service.set(cache_key, result.dict())
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 大学API（带缓存）
# =====================================================

@router.get("/universities", response_model=UniversityListResponse)
async def get_universities(
    province: Optional[str] = None,
    level: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取大学列表（从数据库读取，支持Redis缓存）"""
    try:
        # 构建缓存键
        cache_key = f"universities:{province or 'all'}:{level or 'all'}:{page}:{page_size}"
        
        # 尝试从缓存读取
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库读取
        result = data_service.get_universities(province, level, page, page_size)
        
        # 写入缓存
        cache_service.set(cache_key, result.dict())
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/universities/{university_id}")
async def get_university(university_id: int):
    """获取大学详情（从数据库读取）"""
    try:
        university = data_service.get_university_by_id(university_id)
        if not university:
            raise HTTPException(status_code=404, detail="大学不存在")
        return university
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 录取分数API（带缓存）
# =====================================================

@router.get("/admission-scores", response_model=AdmissionScoreListResponse)
async def get_admission_scores(
    university_id: Optional[int] = None,
    major_id: Optional[int] = None,
    province: Optional[str] = None,
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取录取分数列表（从数据库读取，支持Redis缓存）"""
    try:
        result = data_service.get_admission_scores(university_id, major_id, province, year, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 行业趋势API（带缓存）
# =====================================================

@router.get("/industry-trends", response_model=IndustryTrendListResponse)
async def get_industry_trends(
    industry_name: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取行业趋势列表（从数据库读取，支持Redis缓存）"""
    try:
        result = data_service.get_industry_trends(industry_name, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 视频内容API（带缓存）
# =====================================================

@router.get("/videos", response_model=VideoContentListResponse)
async def get_videos(
    platform: Optional[str] = None,
    related_major: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取视频内容列表（从数据库读取，支持Redis缓存）"""
    try:
        result = data_service.get_videos(platform, related_major, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 爬取历史API
# =====================================================

@router.get("/crawl-history", response_model=CrawlHistoryListResponse)
async def get_crawl_history(
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取爬取历史列表（从数据库读取）"""
    try:
        result = data_service.get_crawl_history(task_type, status, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 爬取配额API
# =====================================================

@router.get("/crawl-quotas", response_model=CrawlQuotaListResponse)
async def get_crawl_quotas():
    """获取爬取配额列表（从数据库读取，支持Redis缓存）"""
    try:
        cache_key = CacheKeyBuilder.quota_status()
        
        # 尝试从缓存读取
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库读取
        result = data_service.get_crawl_quotas()
        
        # 写入缓存
        cache_service.set(cache_key, result.dict())
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 缓存管理API（管理员接口）
# =====================================================

@router.delete("/cache/{cache_key}")
async def delete_cache(cache_key: str):
    """删除指定缓存（管理员接口）"""
    try:
        success = cache_service.delete(cache_key)
        if success:
            return {"status": "success", "message": f"缓存已清除: {cache_key}"}
        else:
            return {"status": "failed", "message": f"缓存不存在或清除失败: {cache_key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/bulk")
async def delete_cache_bulk(pattern: str = Query(..., description="缓存键模式，如 majors:*")):
    """批量清除缓存（管理员接口）"""
    try:
        count = cache_service.delete_pattern(pattern)
        return {"status": "success", "message": f"已清除 {count} 个缓存键", "pattern": pattern}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/all")
async def delete_all_cache():
    """清除所有数据缓存（爬取完成后调用）（管理员接口）"""
    try:
        count = cache_service.invalidate_all_data()
        return {"status": "success", "message": f"已清除 {count} 个数据缓存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息（管理员接口）"""
    try:
        return cache_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 全量爬取API（管理员接口）
# =====================================================

@router.post("/admin/crawler/full-crawl")
async def trigger_full_crawl(task_type: str = "all"):
    """
    触发全量爬取（管理员接口）
    
    全量爬取规则：
    1. 忽略增量逻辑，强制重新爬取所有数据
    2. 根据source_url覆盖已有记录
    3. 重置所有学科配额使用计数
    4. 记录操作日志，标记为全量爬取
    """
    try:
        task_id = str(uuid.uuid4())
        
        # 记录全量爬取任务
        from models.database import CrawlHistory, CrawlStatus, CrawlTaskType
        
        # 重置配额
        data_service.reset_quota_used()
        
        # 调用爬虫服务触发全量爬取
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                "http://localhost:8004/api/v1/admin/crawler/crawl",
                json={"force": True}
            )
            
            if response.status_code == 200:
                crawl_result = response.json()
                
                # 记录爬取历史
                history = CrawlHistory(
                    task_id=task_id,
                    task_type=task_type,
                    start_time=datetime.utcnow(),
                    status=CrawlStatus.RUNNING.value,
                    crawled_count=0,
                    success_count=0,
                    failed_count=0
                )
                data_service.log_crawl_history(history)
                
                return {
                    "task_id": task_id,
                    "status": "started",
                    "message": "全量爬取任务已启动",
                    "crawl_mode": "full",
                    "task_type": task_type,
                    "crawler_response": crawl_result
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "message": f"触发全量爬取失败: {response.status_code}",
                    "crawl_mode": "full",
                    "task_type": task_type
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 热点资讯API（带缓存）
# =====================================================

@router.get("/hot-news", response_model=HotNewsListResponse)
async def get_hot_news(
    category: Optional[str] = None,
    related_major: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query("heat_index", regex="^(heat_index|publish_time)$")
):
    """获取热点资讯列表（从数据库读取，支持Redis缓存）"""
    try:
        result = data_service.get_hot_news(
            category=category,
            related_major=related_major,
            source=source,
            page=page,
            page_size=page_size,
            order_by=order_by
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-news/trending", response_model=HotNewsListResponse)
async def get_hot_news_trending(limit: int = Query(20, ge=1, le=100)):
    """获取热门趋势资讯（按热度排序）"""
    try:
        return data_service.get_hot_news_trending(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-news/recent", response_model=HotNewsListResponse)
async def get_hot_news_recent(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(20, ge=1, le=100)
):
    """获取最近发布的热点资讯"""
    try:
        return data_service.get_hot_news_recent(hours=hours, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-news/by-major/{major}", response_model=HotNewsListResponse)
async def get_hot_news_by_major(major: str, limit: int = Query(10, ge=1, le=50)):
    """获取指定专业的热点资讯"""
    try:
        return data_service.get_hot_news_by_major(major=major, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-news/by-category/{category}", response_model=HotNewsListResponse)
async def get_hot_news_by_category(category: str, limit: int = Query(10, ge=1, le=50)):
    """获取指定分类的热点资讯"""
    try:
        return data_service.get_hot_news_by_category(category=category, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
