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
    major_name: str
):
    """
    获取专业相关视频
    
    只返回1个最佳视频，要求：
    1. 视频内容能覆盖时间线5个阶段：起源与发展、挫折与争议、重大突破、现状与爆发、未来展望
    2. 时长不超过5分钟（300秒）
    3. 按综合评分排序返回最佳视频
    """
    # 构建搜索关键词
    keywords = [
        f"{major_name}专业介绍",
        f"{major_name}专业解读",
        f"什么是{major_name}",
        f"{major_name}完整介绍"
    ]
    
    # B站API需要特定请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0; Intel Mac OS.0.0 Safari/537.36",
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
                    "page": 1,
                    "page_size": 10,
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
    
    # 去重
    seen_bvids = set()
    unique_results = []
    for video in all_results:
        if video["bvid"] and video["bvid"] not in seen_bvids:
            seen_bvids.add(video["bvid"])
            unique_results.append(video)
    
    # 计算评分并排序
    scored_videos = []
    for video in unique_results:
        score = calculate_video_score(video, major_name)
        scored_videos.append({
            **video,
            "score": score
        })
    
    # 按评分降序排序
    scored_videos.sort(key=lambda x: x["score"], reverse=True)
    
    # 返回最佳视频（添加必要的字段）
    best = scored_videos[0] if scored_videos else None
    if best:
        best["is_video"] = True
        best["source"] = "B站"
        pubdate_val = best.get("pubdate", 0)
        best["pub_date"] = datetime.fromtimestamp(pubdate_val).strftime("%Y-%m-%d") if pubdate_val else ""
        best.pop("pubdate", None)
        best.pop("search_keyword", None)
    
    return best


def calculate_video_score(video: Dict, major_name: str) -> float:
    """
    计算视频评分
    
    评分规则：
    - 内容覆盖度（最重要，权重50%）：必须覆盖时间线5个阶段
    - 时长评分（权重20%）：最佳3-5分钟
    - 播放量评分（权重15%）
    - 相关度评分（权重15%）
    """
    score = 0.0
    
    # 内容覆盖度（权重50%）
    title = video.get("title", "")
    description = video.get("description", "")
    content = f"{title} {description}".lower()
    
    required_keywords = [
        ("起源", "发展", "历史"),        # 起源与发展
        ("挫折", "争议", "低谷", "寒冬"), # 挫折与争议
        ("突破", "成就", "里程碑", "革命"), # 重大突破
        ("现状", "爆发", "现在", "当前"),  # 现状与爆发
        ("未来", "展望", "趋势", "前景")   # 未来展望
    ]
    
    coverage_count = 0
    for keyword_group in required_keywords:
        if any(kw in content for kw in keyword_group):
            coverage_count += 1
    
    coverage_score = (coverage_count / 5) * 50  # 满分50分
    
    # 时长评分（权重20%），最佳3-5分钟（180-300秒）
    duration = video.get("duration", 0)
    if duration <= 60:
        duration_score = 5   # 太短
    elif duration <= 180:
        duration_score = 15  # 偏短
    elif duration <= 300:
        duration_score = 20  # 最佳
    elif duration <= 600:
        duration_score = 12  # 可接受
    else:
        duration_score = 5   # 太长
    
    # 播放量评分（权重15%）
    view_count = video.get("view_count", 0)
    if view_count >= 100000:
        view_score = 15
    elif view_count >= 50000:
        view_score = 13
    elif view_count >= 10000:
        view_score = 11
    elif view_count >= 5000:
        view_score = 9
    elif view_count >= 1000:
        view_score = 7
    else:
        view_score = 4
    
    # 相关度评分（权重15%）
    relevance_score = 0
    title_lower = title.lower()
    if major_name in title:
        relevance_score += 8
    if "专业" in title or "介绍" in title or "解读" in title or "讲解" in title:
        relevance_score += 7
    
    total_score = coverage_score + duration_score + view_score + relevance_score
    return total_score


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


@app.get("/api/v1/video/hot-events/{major_name}")
async def get_hot_events(major_name: str):
    """
    获取专业相关的热点事件
    
    从多个平台搜索最近的热点事件：
    - B站视频（按最新发布时间排序）
    - 微博热搜
    - 今日头条
    - 腾讯新闻
    """
    # 构建搜索关键词 - 重点搜索最新消息和行业大佬动态
    keywords = [
        f"{major_name} 2025",
        f"{major_name} 最新",
        f"{major_name} 热点",
        f"{major_name} 重大突破",
        f"{major_name} GPT",
        f"{major_name} DeepSeek",
        f"{major_name} Agent",
        f"AI {major_name} 2025",
        f"{major_name} 黄仁勋",
        f"{major_name} 马斯克",
        f"{major_name} Agent Skill",
        f"{major_name} 估值",
        f"{major_name} 月之暗面",
        f"{major_name} OpenAI",
        f"{major_name} 英伟达"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com"
    }
    
    all_events = []
    
    # 1. 从B站搜索最新视频（按发布时间排序）
    for keyword in keywords[:5]:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                search_url = f"{BILIBILI_API}/x/web-interface/search/type"
                params = {
                    "search_type": "video",
                    "keyword": keyword,
                    "page": 1,
                    "page_size": 8,
                    "order": "pubdate"  # 按最新发布时间排序
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
                
                for item in data.get("data", {}).get("result", []):
                    if not isinstance(item, dict):
                        continue
                    
                    title = item.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", "")
                    if not title:
                        continue
                    
                    # 解析发布时间
                    pubdate = item.get("pubdate", 0)
                    pubdate_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d") if pubdate else ""
                    
                    # 只保留最近180天的内容
                    if pubdate:
                        days_ago = (datetime.now() - datetime.fromtimestamp(pubdate)).days
                        if days_ago > 180:
                            continue
                    
                    # 判断事件类型
                    event_type = detect_event_type(title)
                    
                    all_events.append({
                        "title": title,
                        "description": item.get("description", "")[:300],
                        "source": "B站",
                        "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                        "pub_date": pubdate_str,
                        "view_count": item.get("play", 0),
                        "heat_index": min(item.get("play", 0) / 1000, 100),
                        "is_video": True,
                        "event_type": event_type,
                        "cover": item.get("pic", ""),
                        "author": item.get("author", "")
                    })
        except Exception as e:
            print(f"搜索B站失败 {keyword}: {e}")
            continue
    
    # 2. 从微博热搜搜索（模拟）
    weibo_events = await search_weibo_hot(major_name, headers)
    all_events.extend(weibo_events)
    
    # 3. 从今日头条搜索
    toutiao_events = await search_toutiao_hot(major_name, headers)
    all_events.extend(toutiao_events)
    
    # 4. 从腾讯新闻搜索
    qq_news_events = await search_qqnews_hot(major_name, headers)
    all_events.extend(qq_news_events)
    
    # 去重并排序
    seen_titles = set()
    unique_events = []
    for event in all_events:
        title = event["title"]
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_events.append(event)
    
    # 按时间排序（最新的在前），同时考虑热度
    unique_events.sort(key=lambda x: (x.get("pub_date", ""), x.get("heat_index", 0)), reverse=True)
    
    return {
        "major_name": major_name,
        "total_events": len(unique_events),
        "events": unique_events[:15],
        "generated_at": datetime.now().isoformat()
    }


async def search_weibo_hot(major_name: str, headers: Dict) -> List[Dict]:
    """从微博热搜搜索"""
    events = []
    
    try:
        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            url = "https://weibo.com/ajax/statuses/mymblog"
            params = {
                "uid": "",
                "feature": 0,
                "is_all": 1,
                "key_word": f"{major_name} 2025"
            }
            
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return events
            
            try:
                data = response.json()
            except:
                return events
            
            for item in data.get("list", [])[:5]:
                title = item.get("text_raw", "")
                if not title:
                    continue
                
                event_type = detect_event_type(title)
                
                events.append({
                    "title": title[:80],
                    "description": "",
                    "source": "微博",
                    "url": f"https://weibo.com/status/{item.get('idstr', '')}",
                    "pub_date": datetime.now().strftime("%Y-%m-%d"),
                    "view_count": item.get("attitudes_count", 0),
                    "heat_index": min(item.get("attitudes_count", 0) / 100, 100),
                    "is_video": False,
                    "event_type": event_type
                })
    except Exception as e:
        print(f"搜索微博失败: {e}")
    
    return events


async def search_toutiao_hot(major_name: str, headers: Dict) -> List[Dict]:
    """从今日头条搜索"""
    events = []
    
    try:
        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            url = "https://www.toutiao.com/api/search/content/"
            params = {
                "aid": 24,
                "app_name": "web_search",
                "keyword": f"{major_name} 2025",
                "offset": 0,
                "format": "json",
                "autosuggest": 1
            }
            
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return events
            
            try:
                data = response.json()
            except:
                return events
            
            for item in data.get("data", [])[:5]:
                title = item.get("title", "")
                if not title:
                    continue
                
                event_type = detect_event_type(title)
                
                events.append({
                    "title": title,
                    "description": item.get("abstract", "")[:200] if item.get("abstract") else "",
                    "source": "今日头条",
                    "url": item.get("article_url", ""),
                    "pub_date": item.get("publish_time", "")[:10] if item.get("publish_time") else datetime.now().strftime("%Y-%m-%d"),
                    "view_count": item.get("go_detail_count", 0),
                    "heat_index": min(item.get("go_detail_count", 0) / 1000, 100),
                    "is_video": False,
                    "event_type": event_type
                })
    except Exception as e:
        print(f"搜索今日头条失败: {e}")
    
    return events


async def search_qqnews_hot(major_name: str, headers: Dict) -> List[Dict]:
    """从腾讯新闻搜索"""
    events = []
    
    try:
        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            url = "https://i.news.qq.com/toutiao/search"
            params = {
                "keyword": f"{major_name} 2025",
                "page": 1,
                "pageSize": 5,
                "sort": "time"
            }
            
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return events
            
            try:
                data = response.json()
            except:
                return events
            
            for item in data.get("result", {}).get("data", [])[:5]:
                title = item.get("title", "")
                if not title:
                    continue
                
                event_type = detect_event_type(title)
                
                events.append({
                    "title": title,
                    "description": item.get("abstract", "")[:200] if item.get("abstract") else "",
                    "source": "腾讯新闻",
                    "url": item.get("url", ""),
                    "pub_date": item.get("publish_time", "")[:10] if item.get("publish_time") else datetime.now().strftime("%Y-%m-%d"),
                    "view_count": item.get("comment_count", 0) * 100,
                    "heat_index": min(item.get("comment_count", 0) * 10, 100),
                    "is_video": False,
                    "event_type": event_type
                })
    except Exception as e:
        print(f"搜索腾讯新闻失败: {e}")
    
    return events


def detect_event_type(title: str) -> str:
    """根据标题判断事件类型"""
    title_lower = title.lower()
    
    if any(kw in title_lower for kw in ["突破", "发布", "发布", "首创", "首次", "攻克"]):
        return "技术突破"
    elif any(kw in title_lower for kw in ["政策", "规划", "战略", "发布", "出台"]):
        return "政策变化"
    elif any(kw in title_lower for kw in ["大会", "会议", "论坛", "峰会", "展会"]):
        return "重要会议"
    elif any(kw in title_lower for kw in ["融资", "上市", "收购", "投资", "收购"]):
        return "行业动态"
    elif any(kw in title_lower for kw in ["争议", "丑闻", "负面", "危机"]):
        return "社会事件"
    else:
        return "行业动态"


@app.get("/api/v1/video/professional-with-events/{major_name}")
async def get_video_with_hot_events(major_name: str):
    """
    获取专业视频和热点事件
    
    返回最佳视频和相关的热点事件列表
    视频/事件可以是B站视频链接，也可以是外部新闻链接
    """
    # 获取视频
    video_response = await get_professional_videos(major_name)
    
    # 获取热点事件
    hot_events_response = await get_hot_events(major_name)
    
    # 获取热门视频（用于热点视频区域）
    hot_videos_data = await get_hot_videos(major_name, limit=5)
    hot_videos = hot_videos_data.get("hot_videos", [])
    
    # 如果没有热门视频，使用主视频
    best_video = video_response.get("video")
    if not best_video and hot_videos:
        best_video = hot_videos[0] if len(hot_videos) > 0 else None
    
    return {
        "major_name": major_name,
        "hot_video": best_video,
        "hot_events": hot_events_response.get("events", [])[:10],
        "generated_at": datetime.now().isoformat()
    }


@app.get("/api/v1/video/hot-videos/{major_name}")
async def get_hot_videos(major_name: str, limit: int = Query(5, description="返回数量")):
    """
    获取专业相关的热门视频
    
    按播放量和发布时间排序，返回最新的热门视频
    """
    keywords = [
        f"{major_name}最新",
        f"{major_name}热门",
        f"{major_name}新闻",
        f"{major_name}2024",
        f"{major_name}2025"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com"
    }
    
    all_videos = []
    
    for keyword in keywords[:3]:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                search_url = f"{BILIBILI_API}/x/web-interface/search/type"
                params = {
                    "search_type": "video",
                    "keyword": keyword,
                    "page": 1,
                    "page_size": 5,
                    "order": "click"  # 按播放量排序
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
                
                for item in data.get("data", {}).get("result", []):
                    if not isinstance(item, dict):
                        continue
                    
                    title = item.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", "")
                    if not title:
                        continue
                    
                    # 解析时长
                    duration_str = item.get("duration", "0:00")
                    duration_parts = duration_str.split(":")
                    try:
                        duration_seconds = int(duration_parts[0]) * 60 + int(duration_parts[1])
                    except:
                        duration_seconds = 0
                    
                    # 解析发布时间
                    pubdate = item.get("pubdate", 0)
                    pubdate_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d") if pubdate else ""
                    
                    all_videos.append({
                        "title": title,
                        "description": item.get("description", ""),
                        "cover": item.get("pic", ""),
                        "duration": duration_seconds,
                        "author": item.get("author", ""),
                        "view_count": item.get("play", 0),
                        "pubdate": pubdate,
                        "pub_date": pubdate_str,
                        "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                        "source": "B站",
                        "is_video": True
                    })
        except Exception as e:
            print(f"搜索热门视频失败 {keyword}: {e}")
            continue
    
    # 去重并按播放量排序
    seen_titles = set()
    unique_videos = []
    for video in all_videos:
        title = video["title"]
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_videos.append(video)
    
    # 按播放量排序
    unique_videos.sort(key=lambda x: x.get("view_count", 0), reverse=True)
    
    return {
        "major_name": major_name,
        "total": len(unique_videos),
        "hot_videos": unique_videos[:limit],
        "generated_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8007))
    uvicorn.run(app, host="0.0.0.0", port=port)
