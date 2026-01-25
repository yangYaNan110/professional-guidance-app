#!/usr/bin/env python3
"""
专业推荐模块API服务
提供专业推荐、分类筛选、详情查询等RESTful API
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from enum import Enum

# 导入推荐引擎
from recommendation_engine import MajorRecommendationEngine, SortBy, SortOrder

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="专业推荐模块API",
    description="提供专业推荐、分类筛选、详情查询等RESTful接口",
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

# 推荐引擎实例
recommendation_engine = MajorRecommendationEngine()

# API响应模型
class APIResponse:
    """标准API响应格式"""
    @staticmethod
    def success(data: Any, message: str = "操作成功") -> Dict[str, Any]:
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, code: int = 400) -> Dict[str, Any]:
        return {
            "success": False,
            "error": message,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }

# 依赖注入：确保数据库连接
async def get_db_engine():
    """获取推荐引擎实例"""
    if not recommendation_engine.connect_database():
        raise HTTPException(status_code=503, detail="数据库连接失败")
    try:
        yield recommendation_engine
    finally:
        pass  # 保持连接打开，避免频繁开关

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 专业推荐API服务启动")
    if not recommendation_engine.connect_database():
        logger.error("❌ 数据库连接失败，服务可能无法正常工作")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    recommendation_engine.close()
    logger.info("🔚 专业推荐API服务关闭")

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return APIResponse.success({
        "service": "专业推荐模块API",
        "version": "1.0.0",
        "description": "提供专业推荐、分类筛选、详情查询等服务",
        "endpoints": {
            "recommendations": "/api/v1/recommendations",
            "categories": "/api/v1/categories", 
            "major_detail": "/api/v1/majors/{major_id}",
            "statistics": "/api/v1/statistics"
        }
    })

# 获取专业推荐列表
@app.get("/api/v1/recommendations")
async def get_recommendations(
    category_id: Optional[int] = Query(None, description="专业分类ID，不填表示所有分类"),
    sort_by: str = Query("heat_index", description="排序字段：heat_index, employment_rate, avg_salary, future_prospects, industry_demand, crawled_at"),
    sort_order: str = Query("desc", description="排序顺序：desc, asc"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量，最大100"),
    engine: MajorRecommendationEngine = Depends(get_db_engine)
):
    """
    获取专业推荐列表
    
    支持的排序字段：
    - heat_index: 热度指数（默认）
    - employment_rate: 就业率
    - avg_salary: 平均薪资
    - future_prospects: 发展前景
    - industry_demand: 行业需求
    - crawled_at: 更新时间
    """
    try:
        # 验证排序字段
        valid_sort_fields = [e.value for e in SortBy]
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的排序字段: {sort_by}，支持的字段: {', '.join(valid_sort_fields)}"
            )
        
        # 验证排序顺序
        if sort_order not in ["desc", "asc"]:
            raise HTTPException(
                status_code=400,
                detail=f"无效的排序顺序: {sort_order}，支持的顺序: desc, asc"
            )
        
        # 转换枚举类型
        sort_by_enum = SortBy(sort_by)
        sort_order_enum = SortOrder(sort_order)
        
        # 获取推荐结果
        result = engine.get_major_recommendations(
            category_id=category_id,
            sort_by=sort_by_enum,
            sort_order=sort_order_enum,
            page=page,
            page_size=page_size
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        response = APIResponse.success(result, f"成功获取 {len(result['data'])} 个专业推荐")
        
        # 开发期间禁用缓存标识
        return JSONResponse(
            content=response,
            headers={"X-Cache": "DISABLED"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")

# 获取专业分类列表
@app.get("/api/v1/categories")
async def get_categories(engine: MajorRecommendationEngine = Depends(get_db_engine)):
    """获取所有专业分类"""
    try:
        categories = engine.get_categories()
        
        response = APIResponse.success(categories, f"成功获取 {len(categories)} 个专业分类")
        
        # 开发期间禁用缓存标识
        return JSONResponse(
            content=response,
            headers={"X-Cache": "DISABLED"}
        )
        
    except Exception as e:
        logger.error(f"❌ 获取分类失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")

# 获取专业详情
@app.get("/api/v1/majors/{major_id}")
async def get_major_detail(
    major_id: int,
    engine: MajorRecommendationEngine = Depends(get_db_engine)
):
    """获取专业详情"""
    try:
        if major_id <= 0:
            raise HTTPException(status_code=400, detail="无效的专业ID")
        
        result = engine.get_major_detail(major_id)
        
        if not result["success"]:
            if "不存在" in result["message"]:
                raise HTTPException(status_code=404, detail=result["message"])
            else:
                raise HTTPException(status_code=500, detail=result["message"])
        
        response = APIResponse.success(result["data"], "成功获取专业详情")
        
        # 开发期间禁用缓存标识
        return JSONResponse(
            content=response,
            headers={"X-Cache": "DISABLED"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取专业详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取专业详情失败: {str(e)}")

# 获取统计信息
@app.get("/api/v1/statistics")
async def get_statistics(engine: MajorRecommendationEngine = Depends(get_db_engine)):
    """获取推荐统计信息"""
    try:
        result = engine.get_statistics()
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        response = APIResponse.success(result["data"], "成功获取统计信息")
        
        # 开发期间禁用缓存标识
        return JSONResponse(
            content=response,
            headers={"X-Cache": "DISABLED"}
        )
        
    except Exception as e:
        logger.error(f"❌ 获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

# 健康检查
@app.get("/api/v1/health")
async def health_check():
    """健康检查接口"""
    try:
        # 尝试连接数据库
        if recommendation_engine.conn:
            db_status = "healthy"
        else:
            if recommendation_engine.connect_database():
                db_status = "healthy"
                recommendation_engine.close()
            else:
                db_status = "unhealthy"
        
        health_info = {
            "status": "healthy" if db_status == "healthy" else "unhealthy",
            "service": "专业推荐API",
            "version": "1.0.0",
            "database": db_status,
            "timestamp": datetime.now().isoformat()
        }
        
        status_code = 200 if db_status == "healthy" else 503
        return JSONResponse(content=APIResponse.success(health_info), status_code=status_code)
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return JSONResponse(
            content=APIResponse.error(f"健康检查失败: {str(e)}", 503),
            status_code=503
        )

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return JSONResponse(
        content=APIResponse.error("接口不存在", 404),
        status_code=404
    )

@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    """参数验证错误处理"""
    return JSONResponse(
        content=APIResponse.error("请求参数格式错误", 422),
        status_code=422
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500错误处理"""
    logger.error(f"❌ 服务器内部错误: {exc}")
    return JSONResponse(
        content=APIResponse.error("服务器内部错误", 500),
        status_code=500
    )

if __name__ == "__main__":
    # 开发环境启动
    uvicorn.run(
        "recommendation_api_new:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )