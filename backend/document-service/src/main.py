#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业介绍服务
根据专业名称动态生成专业介绍内容
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_processor import DocumentProcessor

app = FastAPI(
    title="专业介绍服务", 
    description="生成专业介绍内容",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_processor = DocumentProcessor()


class MajorIntroRequest(BaseModel):
    """专业介绍请求"""
    major_name: str
    category: Optional[str] = None
    related_majors: Optional[List[str]] = None


class MajorIntroResponse(BaseModel):
    """专业介绍响应"""
    success: bool
    major_name: str
    category: str
    introduction: str
    core_courses: List[str]
    career_prospects: str
    related_majors: List[str]
    generated_at: str
    cached: bool = False
    is_hot_major: bool = False
    cache_ttl_hours: int = 72
    cache_hit: bool = False


@app.get("/api/v1/major/intro/{major_name}")
async def get_major_introduction(major_name: str):
    """
    获取专业介绍
    
    Args:
        major_name: 专业名称
        
    Returns:
        MajorIntroResponse: 专业介绍内容
    """
    try:
        result = document_processor.generate_major_introduction(major_name)
        
        return MajorIntroResponse(
            success=True,
            major_name=result["name"],
            category=result["category"],
            introduction=result.get("introduction", ""),
            core_courses=result.get("core_courses", []),
            career_prospects=result.get("career_prospects", ""),
            related_majors=result.get("related_majors", []),
            generated_at=result["generated_at"],
            cached=result.get("cached", False),
            is_hot_major=result.get("is_hot_major", False),
            cache_ttl_hours=result.get("cache_ttl_hours", 72),
            cache_hit=result.get("cache_hit", False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/major/intro")
async def get_major_introduction_post(request: MajorIntroRequest):
    """
    获取专业介绍（POST方法）
    
    Args:
        request: 请求参数
        
    Returns:
        MajorIntroResponse: 专业介绍内容
    """
    try:
        result = document_processor.generate_major_introduction(
            request.major_name,
            request.category,
            request.related_majors
        )
        
        return MajorIntroResponse(
            success=True,
            major_name=result["name"],
            category=result["category"],
            introduction=result.get("introduction", ""),
            core_courses=result.get("core_courses", []),
            career_prospects=result.get("career_prospects", ""),
            related_majors=result.get("related_majors", []),
            generated_at=result["generated_at"],
            cached=result.get("cached", False),
            is_hot_major=result.get("is_hot_major", False),
            cache_ttl_hours=result.get("cache_ttl_hours", 72),
            cache_hit=result.get("cache_hit", False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/major/intro/cache/{major_name}")
async def clear_cache(major_name: str):
    """清除缓存"""
    document_processor.clear_cache(major_name)
    return {"success": True, "message": f"已清除 {major_name} 的缓存"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
