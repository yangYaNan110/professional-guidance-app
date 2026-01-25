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
            "/api/v1/majors/{id}",
            "/api/v1/majors/recommendations",
            "/api/v1/majors/heat-ranking",
            "/api/v1/majors/search"
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

@app.get("/api/v1/majors/recommendations")
async def get_major_recommendations(
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=10, description="每页数量"),
    category: Optional[str] = Query(default=None, description="学科门类筛选"),
    sort_by: Optional[str] = Query(default="heat_index", description="排序字段: heat_index, employment_rate, avg_salary, future_rank"),
    order: Optional[str] = Query(default="desc", description="排序方向: desc, asc")
):
    """获取专业推荐列表（基于热度指数排序）"""
    try:
        # 筛选数据
        filtered_data = MAJOR_MARKET_DATA
        
        if category:
            filtered_data = [d for d in filtered_data if d["category_name"] == category]
        
        # 排序
        valid_sort_fields = ["heat_index", "employment_rate", "avg_salary", "popularity_rank", "employment_rank", "salary_rank", "future_rank"]
        if sort_by not in valid_sort_fields:
            sort_by = "heat_index"
        
        reverse_order = (order or "").lower() == "desc"
        filtered_data.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse_order)
        
        # 分页计算
        total = len(filtered_data)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = filtered_data[start:end]
        
        # 组装完整的专业信息
        recommendations = []
        for market_data in page_data:
            # 获取专业基本信息
            major_info = next((m for m in MAJORS if m["id"] == market_data["major_id"]), {})
            if not major_info:
                continue
                
            # 组合基本信息和市场数据
            recommendation = {
                "id": market_data["major_id"],
                "name": market_data["major_name"],
                "category": market_data["category_name"],
                "code": major_info.get("code", ""),
                "description": major_info.get("description", ""),
                "study_period": major_info.get("study_period", 4),
                "degree_awarded": major_info.get("degree_awarded", ""),
                
                # 市场数据
                "market_data": {
                    "employment_rate": market_data["employment_rate"],
                    "avg_salary": market_data["avg_salary"],
                    "salary_growth_rate": market_data["salary_growth_rate"],
                    "industry_demand_score": market_data["industry_demand_score"],
                    "future_prospects_score": market_data["future_prospects_score"],
                    "talent_shortage": market_data["talent_shortage"],
                    "heat_index": market_data["heat_index"],
                    
                    # 排名信息
                    "rankings": {
                        "popularity": market_data["popularity_rank"],
                        "employment": market_data["employment_rank"],
                        "salary": market_data["salary_rank"],
                        "future": market_data["future_rank"]
                    }
                },
                
                # 推荐标签
                "tags": generate_recommendation_tags(market_data)
            }
            recommendations.append(recommendation)
        
        return success_response({
            "recommendations": recommendations,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": end < total,
                "has_more": end < total
            },
            "filters": {
                "category": category,
                "sort_by": sort_by,
                "order": order,
                "available_categories": list(set(d["category_name"] for d in MAJOR_MARKET_DATA))
            }
        })
    except Exception as e:
        logger.error(f"获取专业推荐失败: {str(e)}")
        return error_response("获取专业推荐失败")

@app.get("/api/v1/majors/heat-ranking")
async def get_heat_ranking(
    limit: int = Query(default=20, description="返回数量限制"),
    category: Optional[str] = Query(default=None, description="学科门类筛选")
):
    """获取专业热度排行榜"""
    try:
        filtered_data = MAJOR_MARKET_DATA
        
        if category:
            filtered_data = [d for d in filtered_data if d["category_name"] == category]
        
        # 按热度指数排序
        sorted_data = sorted(filtered_data, key=lambda x: x["heat_index"], reverse=True)[:limit]
        
        ranking_list = []
        for i, market_data in enumerate(sorted_data, 1):
            major_info = next((m for m in MAJORS if m["id"] == market_data["major_id"]), {})
            
            ranking_item = {
                "rank": i,
                "id": market_data["major_id"],
                "name": market_data["major_name"],
                "category": market_data["category_name"],
                "heat_index": market_data["heat_index"],
                "employment_rate": market_data["employment_rate"],
                "avg_salary": market_data["avg_salary"],
                "talent_shortage": market_data["talent_shortage"],
                "trend": get_trend_description(market_data),
                "tags": generate_recommendation_tags(market_data)
            }
            ranking_list.append(ranking_item)
        
        return success_response({
            "ranking": ranking_list,
            "total": len(ranking_list),
            "category": category,
            "updated_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取热度排行榜失败: {str(e)}")
        return error_response("获取热度排行榜失败")

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

# 模拟市场数据（实际应从major_market_data表读取）
MAJOR_MARKET_DATA = [
    {
        "major_id": 1,
        "major_name": "计算机科学与技术",
        "category_name": "工学",
        "employment_rate": 95.5,
        "avg_salary": 18500.00,
        "salary_growth_rate": 12.5,
        "admission_difficulty": 8.5,
        "industry_demand_score": 9.2,
        "future_prospects_score": 9.5,
        "talent_shortage": True,
        "heat_index": 88.5,
        "popularity_rank": 1,
        "employment_rank": 2,
        "salary_rank": 3,
        "future_rank": 1,
        "data_source": "综合招聘平台数据"
    },
    {
        "major_id": 2,
        "major_name": "软件工程",
        "category_name": "工学",
        "employment_rate": 96.2,
        "avg_salary": 17800.00,
        "salary_growth_rate": 11.8,
        "admission_difficulty": 8.2,
        "industry_demand_score": 9.0,
        "future_prospects_score": 9.2,
        "talent_shortage": True,
        "heat_index": 86.8,
        "popularity_rank": 2,
        "employment_rank": 1,
        "salary_rank": 4,
        "future_rank": 2,
        "data_source": "综合招聘平台数据"
    },
    {
        "major_id": 3,
        "major_name": "数据科学与大数据技术",
        "category_name": "工学",
        "employment_rate": 92.8,
        "avg_salary": 19500.00,
        "salary_growth_rate": 15.2,
        "admission_difficulty": 8.8,
        "industry_demand_score": 9.5,
        "future_prospects_score": 9.3,
        "talent_shortage": True,
        "heat_index": 89.2,
        "popularity_rank": 3,
        "employment_rank": 4,
        "salary_rank": 2,
        "future_rank": 3,
        "data_source": "综合招聘平台数据"
    },
    {
        "major_id": 4,
        "major_name": "人工智能",
        "category_name": "工学",
        "employment_rate": 90.5,
        "avg_salary": 22000.00,
        "salary_growth_rate": 18.5,
        "admission_difficulty": 9.5,
        "industry_demand_score": 9.8,
        "future_prospects_score": 9.8,
        "talent_shortage": True,
        "heat_index": 92.5,
        "popularity_rank": 4,
        "employment_rank": 6,
        "salary_rank": 1,
        "future_rank": 1,
        "data_source": "综合招聘平台数据"
    },
    {
        "major_id": 5,
        "major_name": "数学与应用数学",
        "category_name": "理学",
        "employment_rate": 85.2,
        "avg_salary": 12500.00,
        "salary_growth_rate": 8.5,
        "admission_difficulty": 7.5,
        "industry_demand_score": 7.8,
        "future_prospects_score": 8.2,
        "talent_shortage": False,
        "heat_index": 75.8,
        "popularity_rank": 5,
        "employment_rank": 8,
        "salary_rank": 8,
        "future_rank": 5,
        "data_source": "综合招聘平台数据"
    }
]

@app.get("/api/v1/majors/recommendations")
async def get_major_recommendations(
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=10, description="每页数量"),
    category: Optional[str] = Query(default=None, description="学科门类筛选"),
    sort_by: Optional[str] = Query(default="heat_index", description="排序字段: heat_index, employment_rate, avg_salary, future_rank"),
    order: Optional[str] = Query(default="desc", description="排序方向: desc, asc")
):
    """获取专业推荐列表（基于热度指数排序）"""
    try:
        # 筛选数据
        filtered_data = MAJOR_MARKET_DATA
        
        if category:
            filtered_data = [d for d in filtered_data if d["category_name"] == category]
        
        # 排序
        valid_sort_fields = ["heat_index", "employment_rate", "avg_salary", "popularity_rank", "employment_rank", "salary_rank", "future_rank"]
        if sort_by not in valid_sort_fields:
            sort_by = "heat_index"
        
        reverse_order = (order or "").lower() == "desc"
        filtered_data.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse_order)
        
        # 分页计算
        total = len(filtered_data)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = filtered_data[start:end]
        
        # 组装完整的专业信息
        recommendations = []
        for market_data in page_data:
            # 获取专业基本信息
            major_info = next((m for m in MAJORS if m["id"] == market_data["major_id"]), {})
            if not major_info:
                continue
                
            # 组合基本信息和市场数据
            recommendation = {
                "id": market_data["major_id"],
                "name": market_data["major_name"],
                "category": market_data["category_name"],
                "code": major_info.get("code", ""),
                "description": major_info.get("description", ""),
                "study_period": major_info.get("study_period", 4),
                "degree_awarded": major_info.get("degree_awarded", ""),
                
                # 市场数据
                "market_data": {
                    "employment_rate": market_data["employment_rate"],
                    "avg_salary": market_data["avg_salary"],
                    "salary_growth_rate": market_data["salary_growth_rate"],
                    "industry_demand_score": market_data["industry_demand_score"],
                    "future_prospects_score": market_data["future_prospects_score"],
                    "talent_shortage": market_data["talent_shortage"],
                    "heat_index": market_data["heat_index"],
                    
                    # 排名信息
                    "rankings": {
                        "popularity": market_data["popularity_rank"],
                        "employment": market_data["employment_rank"],
                        "salary": market_data["salary_rank"],
                        "future": market_data["future_rank"]
                    }
                },
                
                # 推荐标签
                "tags": generate_recommendation_tags(market_data)
            }
            recommendations.append(recommendation)
        
        return success_response({
            "recommendations": recommendations,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": end < total,
                "has_more": end < total
            },
            "filters": {
                "category": category,
                "sort_by": sort_by,
                "order": order,
                "available_categories": list(set(d["category_name"] for d in MAJOR_MARKET_DATA))
            }
        })
    except Exception as e:
        logger.error(f"获取专业推荐失败: {str(e)}")
        return error_response("获取专业推荐失败")

@app.get("/api/v1/majors/heat-ranking")
async def get_heat_ranking(
    limit: int = Query(default=20, description="返回数量限制"),
    category: Optional[str] = Query(default=None, description="学科门类筛选")
):
    """获取专业热度排行榜"""
    try:
        filtered_data = MAJOR_MARKET_DATA
        
        if category:
            filtered_data = [d for d in filtered_data if d["category_name"] == category]
        
        # 按热度指数排序
        sorted_data = sorted(filtered_data, key=lambda x: x["heat_index"], reverse=True)[:limit]
        
        ranking_list = []
        for i, market_data in enumerate(sorted_data, 1):
            major_info = next((m for m in MAJORS if m["id"] == market_data["major_id"]), {})
            
            ranking_item = {
                "rank": i,
                "id": market_data["major_id"],
                "name": market_data["major_name"],
                "category": market_data["category_name"],
                "heat_index": market_data["heat_index"],
                "employment_rate": market_data["employment_rate"],
                "avg_salary": market_data["avg_salary"],
                "talent_shortage": market_data["talent_shortage"],
                "trend": get_trend_description(market_data),
                "tags": generate_recommendation_tags(market_data)
            }
            ranking_list.append(ranking_item)
        
        return success_response({
            "ranking": ranking_list,
            "total": len(ranking_list),
            "category": category,
            "updated_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取热度排行榜失败: {str(e)}")
        return error_response("获取热度排行榜失败")

def generate_recommendation_tags(market_data: Dict[str, Any]) -> List[str]:
    """根据市场数据生成推荐标签"""
    tags = []
    
    # 高就业率标签
    if market_data["employment_rate"] >= 95:
        tags.append("高就业率")
    elif market_data["employment_rate"] >= 90:
        tags.append("好就业")
    
    # 高薪资标签
    if market_data["avg_salary"] >= 20000:
        tags.append("高薪资")
    elif market_data["avg_salary"] >= 15000:
        tags.append("薪资不错")
    
    # 发展前景标签
    if market_data["future_prospects_score"] >= 9.0:
        tags.append("前景广阔")
    elif market_data["future_prospects_score"] >= 8.0:
        tags.append("前景良好")
    
    # 人才短缺标签
    if market_data["talent_shortage"]:
        tags.append("人才紧缺")
    
    # 热度标签
    if market_data["heat_index"] >= 90:
        tags.append("热门")
    elif market_data["heat_index"] >= 80:
        tags.append("推荐")
    
    return tags[:4]  # 最多显示4个标签

def get_trend_description(market_data: Dict[str, Any]) -> str:
    """获取趋势描述"""
    heat_index = market_data["heat_index"]
    salary_growth = market_data["salary_growth_rate"]
    
    if heat_index >= 90 and salary_growth >= 15:
        return "📈 快速上升"
    elif heat_index >= 80 and salary_growth >= 10:
        return "📊 稳步上升"
    elif heat_index >= 70:
        return "➡️ 持平"
    else:
        return "📉 趋冷"

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
        reload=False,
        log_level="info"
    )