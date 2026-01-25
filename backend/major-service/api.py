#!/usr/bin/env python3
"""
专业信息模块 - API服务
提供专业分类、专业列表、专业详情等RESTful API
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="专业信息模块API",
    description="提供专业分类、专业列表、专业详情等RESTful接口",
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

# 模拟数据库数据（实际应从PostgreSQL读取）
MAJOR_CATEGORIES = [
    {"id": 1, "name": "工学", "code": "08", "level": 1, "parent_id": None},
    {"id": 2, "name": "理学", "code": "07", "level": 1, "parent_id": None},
    {"id": 3, "name": "文学", "code": "05", "level": 1, "parent_id": None},
    {"id": 4, "name": "历史学", "code": "06", "level": 1, "parent_id": None},
    {"id": 5, "name": "经济学", "code": "02", "level": 1, "parent_id": None},
]

MAJORS = [
    {
        "id": 1,
        "name": "计算机科学与技术",
        "code": "080901",
        "category_id": 1,
        "description": "培养具备计算机软硬件基础知识和应用能力的专业人才",
        "training_objective": "培养德、智、体、美全面发展，具有创新精神和实践能力的高级专门人才",
        "main_courses": ["数据结构", "算法设计", "操作系统", "计算机网络", "数据库原理"],
        "employment_direction": "软件开发、网络管理、信息安全、人工智能等",
        "study_period": 4,
        "degree_awarded": "工学学士",
        "national_key_major": True,
        "source_url": "https://gaokao.chsi.com.cn/zyk/2024/zyk/080901",
        "source_website": "阳光高考"
    },
    {
        "id": 2,
        "name": "软件工程",
        "code": "080902",
        "category_id": 1,
        "description": "培养具备软件设计、开发、测试和维护能力的专业人才",
        "training_objective": "培养具有软件工程理论基础和实践能力的高级工程技术人才",
        "main_courses": ["软件工程导论", "程序设计", "软件测试", "项目管理", "系统架构"],
        "employment_direction": "软件开发、软件测试、项目管理、系统架构等",
        "study_period": 4,
        "degree_awarded": "工学学士",
        "national_key_major": True,
        "source_url": "https://gaokao.chsi.com.cn/zyk/2024/zyk/080902",
        "source_website": "阳光高考"
    },
    {
        "id": 3,
        "name": "数据科学与大数据技术",
        "code": "080910T",
        "category_id": 1,
        "description": "培养具备数据收集、处理、分析和可视化能力的专业人才",
        "training_objective": "培养具有大数据理论基础和实践能力的数据分析人才",
        "main_courses": ["大数据导论", "数据挖掘", "机器学习", "云计算", "分布式系统"],
        "employment_direction": "数据分析、大数据开发、人工智能、云计算等",
        "study_period": 4,
        "degree_awarded": "工学学士",
        "national_key_major": True,
        "source_url": "https://gaokao.chsi.com.cn/zyk/2024/zyk/080910T",
        "source_website": "阳光高考"
    },
    {
        "id": 4,
        "name": "人工智能",
        "code": "080717T",
        "category_id": 1,
        "description": "培养具备人工智能理论基础和应用能力的专业人才",
        "training_objective": "培养具有AI理论基础和实践能力的复合型人才",
        "main_courses": ["人工智能导论", "机器学习", "深度学习", "计算机视觉", "自然语言处理"],
        "employment_direction": "AI算法工程师、机器学习工程师、数据科学家等",
        "study_period": 4,
        "degree_awarded": "工学学士",
        "national_key_major": True,
        "source_url": "https://gaokao.chsi.com.cn/zyk/2024/zyk/080717T",
        "source_website": "阳光高考"
    },
    {
        "id": 5,
        "name": "数学与应用数学",
        "code": "070101",
        "category_id": 2,
        "description": "培养具备数学理论基础和应用能力的专业人才",
        "training_objective": "培养具有扎实数学基础和应用能力的数学专门人才",
        "main_courses": ["数学分析", "高等代数", "解析几何", "概率论", "数理统计"],
        "employment_direction": "科研、教育、金融、IT等",
        "study_period": 4,
        "degree_awarded": "理学学士",
        "national_key_major": True,
        "source_url": "https://gaokao.chsi.com.cn/zyk/2024/zyk/070101",
        "source_website": "阳光高考"
    }
]

# API响应格式
def success_response(data: Any) -> Dict[str, Any]:
    """统一成功响应格式"""
    return {
        "success": True,
        "data": data,
        "message": "操作成功",
        "timestamp": datetime.now().isoformat()
    }

def error_response(message: str, code: int = 400) -> Dict[str, Any]:
    """统一错误响应格式"""
    return {
        "success": False,
        "error": message,
        "code": code,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

# API路由
@app.get("/")
async def root():
    """根路径"""
    return success_response({
        "message": "专业信息模块API服务",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/majors/categories",
            "/api/v1/majors",
            "/api/v1/majors/{id}"
        ]
    })

@app.get("/api/v1/majors/categories")
async def get_categories():
    """获取专业分类列表"""
    try:
        # 构建树形结构
        categories = []
        for cat in MAJOR_CATEGORIES:
            if cat["parent_id"] is None:  # 只返回一级分类
                category_item = {
                    "id": cat["id"],
                    "name": cat["name"],
                    "code": cat["code"],
                    "level": cat["level"]
                }
                categories.append(category_item)
        
        return success_response(categories)
    except Exception as e:
        logger.error(f"获取专业分类失败: {str(e)}")
        return error_response("获取专业分类失败")

@app.get("/api/v1/majors")
async def get_majors(
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=10, description="每页数量"),
    category_id: Optional[int] = Query(default=None, description="分类ID"),
    keyword: Optional[str] = Query(default=None, description="关键词搜索")
):
    """获取专业列表（支持分页、筛选、搜索）"""
    try:
        # 筛选专业
        filtered_majors = MAJORS
        
        if category_id:
            filtered_majors = [m for m in filtered_majors if m["category_id"] == category_id]
        
        if keyword:
            keyword = keyword.lower()
            filtered_majors = [m for m in filtered_majors 
                           if keyword in m["name"].lower() 
                           or keyword in str(m["description"]).lower()]
        
        # 分页计算
        total = len(filtered_majors)
        start = (page - 1) * page_size
        end = start + page_size
        majors_page = filtered_majors[start:end]
        
        return success_response({
            "majors": majors_page,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        })
    except Exception as e:
        logger.error(f"获取专业列表失败: {str(e)}")
        return error_response("获取专业列表失败")

@app.get("/api/v1/majors/{major_id}")
async def get_major_detail(major_id: int):
    """获取专业详情"""
    try:
        major = next((m for m in MAJORS if m["id"] == major_id), None)
        
        if not major:
            return error_response("专业不存在", 404)
        
        # 获取分类信息
        category = next((c for c in MAJOR_CATEGORIES if c["id"] == major["category_id"]), None)
        
        major_with_category = major.copy()
        major_with_category["category"] = category
        
        return success_response(major_with_category)
    except Exception as e:
        logger.error(f"获取专业详情失败: {str(e)}")
        return error_response("获取专业详情失败")

@app.get("/api/v1/majors/search")
async def search_majors(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(default=10, description="返回结果数量限制")
):
    """专业搜索接口"""
    try:
        if len(q.strip()) < 2:
            return error_response("搜索关键词至少2个字符")
        
        keyword = q.lower()
        search_results = []
        
        for major in MAJORS:
            if (keyword in major["name"].lower() or 
                keyword in major["description"].lower() or
                keyword in major["code"]):
                search_results.append({
                    "id": major["id"],
                    "name": major["name"],
                    "code": major["code"],
                    "category_id": major["category_id"],
                    "highlight": {
                        "name": major["name"],
                        "description": major["description"][:100] + "..." if len(major["description"]) > 100 else major["description"]
                    }
                })
        
        # 限制结果数量
        search_results = search_results[:limit]
        
        return success_response({
            "results": search_results,
            "total": len(search_results),
            "keyword": q
        })
    except Exception as e:
        logger.error(f"专业搜索失败: {str(e)}")
        return error_response("专业搜索失败")

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return success_response({
        "status": "healthy",
        "service": "major-service",
        "version": "1.0.0",
        "database": "simulated",  # 实际应检查PostgreSQL连接
        "timestamp": datetime.now().isoformat()
    })

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(exc)}")
    return error_response("服务器内部错误", 500)

if __name__ == "__main__":
    # 启动服务
    logger.info("启动专业信息模块API服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )