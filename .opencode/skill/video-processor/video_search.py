#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video-search Skill - 多平台视频搜索

功能：
1. 从B站、YouTube等平台搜索视频
2. 支持多平台并发搜索
3. 返回结构化的视频信息
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import aiohttp
import json
import logging


logger = logging.getLogger(__name__)


class Platform(Enum):
    """视频平台"""
    BILIBILI = "bilibili"
    YOUTUBE = "youtube"
    XIGUA = "xigua"
    ALL = "all"


@dataclass
class VideoInfo:
    """视频信息"""
    platform: Platform
    video_id: str
    title: str
    author: str
    author_id: Optional[str]
    description: str
    duration: int
    cover_url: str
    video_url: str
    publish_time: Optional[datetime]
    view_count: int
    like_count: int
    reply_count: int
    tags: List[str] = field(default_factory=list)
    relevance_score: float = 0.0


@dataclass
class SearchConfig:
    """搜索配置"""
    max_results: int = 10
    duration_filter: Optional[Dict[str, int]] = None
    sort_by: str = "totalrank"
    timeout: int = 30


class VideoSearcher:
    """多平台视频搜索器"""
    
    BILIBILI_API = {
        "search": "https://api.bilibili.com/x/web-interface/search/type",
        "video_info": "https://api.bilibili.com/x/web-interface/view"
    }
    
    def __init__(self, config: Optional[SearchConfig] = None):
        self.config = config or SearchConfig()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """初始化搜索器"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """关闭搜索器"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search(
        self,
        query: str,
        platforms: List[Platform] = [Platform.BILIBILI],
        config: Optional[SearchConfig] = None
    ) -> List[VideoInfo]:
        """搜索视频"""
        if not self.session:
            await self.initialize()
        
        config = config or self.config
        
        tasks = []
        for platform in platforms:
            if platform == Platform.BILIBILI or platform == Platform.ALL:
                tasks.append(self._search_bilibili(query, config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        videos = []
        for result in results:
            if isinstance(result, list):
                videos.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Search error: {result}")
        
        videos.sort(key=lambda x: x.relevance_score, reverse=True)
        return videos[:config.max_results]
    
    async def _search_bilibili(self, query: str, config: SearchConfig) -> List[VideoInfo]:
        """搜索B站视频"""
        videos = []
        
        params = {
            "search_type": "video",
            "keyword": query,
            "order": config.sort_by,
            "limit": config.max_results
        }
        
        try:
            async with self.session.get(
                self.BILIBILI_API["search"],
                params=params,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("code") == 0:
                        results = data.get("data", {}).get("result", [])
                        
                        for r in results:
                            video = VideoInfo(
                                platform=Platform.BILIBILI,
                                video_id=r.get("bvid", ""),
                                title=r.get("title", "").replace("<em class=\"search-key\">", "").replace("</em>", ""),
                                author=r.get("author", ""),
                                author_id=r.get("mid"),
                                description=r.get("description", ""),
                                duration=self._parse_duration(r.get("duration", "")),
                                cover_url=r.get("cover", ""),
                                video_url=f"https://www.bilibili.com/video/{r.get('bvid', '')}",
                                publish_time=None,
                                view_count=r.get("stat", {}).get("view", 0),
                                like_count=r.get("stat", {}).get("like", 0),
                                reply_count=r.get("stat", {}).get("reply", 0),
                                tags=r.get("tag", "").split(",") if r.get("tag") else [],
                                relevance_score=self._calculate_relevance(query, r)
                            )
                            videos.append(video)
                    
        except Exception as e:
            logger.error(f"Bilibili search error: {e}")
        
        return videos
    
    def _parse_duration(self, duration_str: str) -> int:
        """解析时长字符串"""
        parts = duration_str.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    
    def _calculate_relevance(self, query: str, result: Dict) -> float:
        """计算相关性评分"""
        score = 0.5
        
        title = result.get("title", "").lower()
        query_lower = query.lower()
        
        if query_lower in title:
            score += 0.3
        
        view_count = result.get("stat", {}).get("view", 0)
        score += min(view_count / 1000000, 0.2)
        
        return min(score, 1.0)


async def search_videos(
    query: str,
    platforms: List[Platform] = [Platform.BILIBILI],
    max_results: int = 10
) -> List[VideoInfo]:
    """搜索视频"""
    searcher = VideoSearcher()
    config = SearchConfig(max_results=max_results)
    
    try:
        await searcher.initialize()
        return await searcher.search(query, platforms, config)
    finally:
        await searcher.close()


if __name__ == "__main__":
    async def test():
        searcher = VideoSearcher()
        await searcher.initialize()
        
        videos = await searcher.search("社会学专业介绍", [Platform.BILIBILI])
        print(f"找到 {len(videos)} 个视频")
        
        for video in videos[:3]:
            print(f"\n标题: {video.title}")
            print(f"作者: {video.author}")
            print(f"时长: {video.duration}秒")
            print(f"相关性: {video.relevance_score:.2f}")
        
        await searcher.close()
    
    asyncio.run(test())
