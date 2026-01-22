#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频服务
提供专业相关视频搜索、总结、剪辑功能
"""

import os
import json
import httpx
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio

app = FastAPI(title="Video Service", description="专业视频搜索和总结服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BILIBILI_API = "https://api.bilibili.com"


class VideoInfo(BaseModel):
    """视频信息"""
    bvid: str
    title: str
    description: str
    cover: str
    duration: int  # 秒
    author: str
    view_count: int
    pubdate: int
    url: str


class VideoSummaryResult(BaseModel):
    """视频总结结果"""
    video: VideoInfo
    summary: str
    key_points: List[str]
    timestamps: List[Dict[str, Any]]
    generated_at: str


class VideoSearchResponse(BaseModel):
    """视频搜索响应"""
    query: str
    total_results: int
    results: List[VideoInfo]


@app.get("/")
async def root():
    return {"service": "video-service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/v1/video/search", response_model=VideoSearchResponse)
async def search_videos(
    keyword: str = Query(..., description="搜索关键词"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量", le=20)
):
    """
    搜索专业相关视频
    
    使用B站搜索API，返回与专业相关的视频列表
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # B站搜索API
            search_url = f"{BILIBILI_API}/x/web-interface/search/type"
            params = {
                "search_type": "video",
                "keyword": keyword,
                "page": page,
                "page_size": page_size,
                "order": "pubdate"  # 按发布时间排序
            }
            
            response = await client.get(search_url, params=params)
            data = response.json()
            
            if data.get("code") != 0:
                raise HTTPException(status_code=400, detail=data.get("message", "搜索失败"))
            
            results = []
            for item in data.get("data", {}).get("result", []):
                video = VideoInfo(
                    bvid=item.get("bvid", ""),
                    title=item.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", ""),
                    description=item.get("description", ""),
                    cover=item.get("cover", ""),
                    duration=item.get("duration", 0),
                    author=item.get("author", ""),
                    view_count=item.get("view", 0),
                    pubdate=item.get("pubdate", 0),
                    url=f"https://www.bilibili.com/video/{item.get('bvid', '')}"
                )
                results.append(video)
            
            return VideoSearchResponse(
                query=keyword,
                total_results=data.get("data", {}).get("numResults", 0),
                results=results
            )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@app.get("/api/v1/video/summary/{bvid}", response_model=VideoSummaryResult)
async def get_video_summary(
    bvid: str,
    output_duration: int = Query(300, description="摘要时长(秒)", le=600)
):
    """
    获取视频摘要
    
    分析视频内容，生成摘要、关键点和时间戳
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 获取视频信息
            info_url = f"{BILIBILI_API}/x/web-interface/view"
            info_response = await client.get(info_url, params={"bvid": bvid})
            info_data = info_response.json()
            
            if info_data.get("code") != 0:
                raise HTTPException(status_code=404, detail="视频不存在")
            
            video_info = info_data.get("data", {})
            pages = video_info.get("pages", [])
            
            # 获取视频字幕/弹幕
            subtitle_url = f"{BILIBILI_API}/x/v1/dm/list.so"
            subtitle_response = await client.get(subtitle_url, params={"oid": pages[0]["cid"] if pages else 0})
            
            # 模拟视频摘要生成（实际应用中需要使用LLM分析字幕内容）
            summary = generate_mock_summary(video_info)
            
            # 生成时间戳
            timestamps = generate_timestamps(video_info, output_duration)
            
            # 生成关键点
            key_points = generate_key_points(video_info)
            
            return VideoSummaryResult(
                video=VideoInfo(
                    bvid=bvid,
                    title=video_info.get("title", ""),
                    description=video_info.get("desc", ""),
                    cover=video_info.get("pic", ""),
                    duration=video_info.get("duration", 0),
                    author=video_info.get("owner", {}).get("name", ""),
                    view_count=video_info.get("stat", {}).get("view", 0),
                    pubdate=video_info.get("pubdate", 0),
                    url=f"https://www.bilibili.com/video/{bvid}"
                ),
                summary=summary,
                key_points=key_points,
                timestamps=timestamps,
                generated_at=datetime.now().isoformat()
            )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@app.get("/api/v1/video/professional/{major_name}")
async def get_professional_videos(
    major_name: str,
    page: int = Query(1, description="页码"),
    page_size: int = Query(5, description="每页数量")
):
    """
    获取专业相关视频
    
    搜索指定专业的教学、介绍类视频
    """
    # 构建搜索关键词
    keywords = [
        f"{major_name}专业介绍",
        f"{major_name}专业解读",
        f"什么是{major_name}",
        f"{major_name}就业前景"
    ]
    
    # B站API需要特定请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com"
    }
    
    all_results = []
    
    for keyword in keywords:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                search_url = f"{BILIBILI_API}/x/web-interface/search/type"
                params = {
                    "search_type": "video",
                    "keyword": keyword,
                    "page": page,
                    "page_size": page_size,
                    "order": "totalrank"
                }
                
                response = await client.get(search_url, params=params)
                
                if response.status_code != 200:
                    continue
                
                try:
                    data = response.json()
                except:
                    continue
                
                if data.get("code") != 0:
                    continue
                
                result_list = data.get("data", {}).get("result", [])
                if not result_list:
                    continue
                
                for item in result_list:
                    if not isinstance(item, dict):
                        continue
                    
                    title = item.get("title", "")
                    if not title:
                        continue
                    
                    # 清理标题中的HTML标签
                    title = title.replace("<em class=\"keyword\">", "").replace("</em>", "")
                    
                    # 解析时长
                    duration_str = item.get("duration", "0:00")
                    duration_parts = duration_str.split(":")
                    try:
                        duration_seconds = int(duration_parts[0]) * 60 + int(duration_parts[1])
                    except:
                        duration_seconds = 0
                    
                    all_results.append({
                        "bvid": item.get("bvid", ""),
                        "title": title,
                        "description": item.get("description", ""),
                        "cover": item.get("pic", ""),
                        "duration": duration_seconds,
                        "author": item.get("author", ""),
                        "view_count": item.get("play", 0),
                        "pubdate": item.get("pubdate", 0),
                        "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                        "search_keyword": keyword
                    })
        except Exception as e:
            print(f"搜索失败 {keyword}: {e}")
            continue
    
    # 去重并返回
    seen_bvids = set()
    unique_results = []
    for video in all_results:
        if video["bvid"] and video["bvid"] not in seen_bvids:
            seen_bvids.add(video["bvid"])
            unique_results.append(video)
    
    return {
        "major_name": major_name,
        "total_results": len(unique_results),
        "page": page,
        "page_size": page_size,
        "videos": unique_results[:page_size]
    }


def generate_mock_summary(video_info: Dict) -> str:
    """生成模拟的视频摘要"""
    title = video_info.get("title", "")
    desc = video_info.get("desc", "")
    
    summary_parts = [
        f"本视频主要介绍{title}相关内容。",
        f"视频详细讲解了相关概念和原理，",
        f"适合对该领域感兴趣的观众观看学习。",
        f"通过本视频可以了解{title}的基本知识和应用场景。"
    ]
    
    return "".join(summary_parts)


def generate_timestamps(video_info: Dict, output_duration: int) -> List[Dict[str, Any]]:
    """生成时间戳"""
    duration = video_info.get("duration", 0)
    if isinstance(duration, str):
        # 格式如 "12:34"
        parts = duration.split(":")
        duration = int(parts[0]) * 60 + int(parts[1])
    
    # 生成3-5个时间戳
    num_timestamps = min(5, max(3, duration // 300))
    timestamps = []
    
    for i in range(num_timestamps):
        time_offset = int(duration * i / num_timestamps)
        timestamps.append({
            "time": time_offset,
            "label": f"章节{i+1}"
        })
    
    return timestamps


def generate_key_points(video_info: Dict) -> List[str]:
    """生成关键点"""
    title = video_info.get("title", "")
    
    return [
        f"了解{title}的基本概念",
        "掌握相关核心知识点",
        "学习实际应用案例",
        "理解未来发展趋势"
    ]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8007))
    uvicorn.run(app, host="0.0.0.0", port=port)
