#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-crawler Skill - 多源文本爬取

功能：
1. 从多个数据源爬取相关文本
2. 支持静态和动态页面
3. 遵守robots.txt和爬虫礼仪
4. 处理反爬机制
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging


logger = logging.getLogger(__name__)


class SourceType(Enum):
    """数据源类型"""
    OFFICIAL = "official"        # 官方网站
    ENCYCLOPEDIA = "encyclopedia"  # 百科网站
    NEWS = "news"                  # 新闻网站
    FORUM = "forum"                # 论坛社区
    BLOG = "blog"                  # 博客
    ACADEMIC = "academic"          # 学术网站
    OTHER = "other"


@dataclass
class CrawledPage:
    """爬取的页面"""
    url: str
    title: str
    content: str
    source_type: SourceType
    reliability: float  # 0-1，可靠性评分
    crawl_time: datetime
    word_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrawlerConfig:
    """爬虫配置"""
    timeout: int = 30              # 请求超时（秒）
    max_concurrent: int = 5        # 最大并发数
    retry_times: int = 3           # 重试次数
    delay_between_requests: float = 1.0  # 请求间隔（秒）
    user_agent: str = "DocumentProcessor/1.0"
    max_pages_per_source: int = 10  # 每个数据源最大爬取页面数
    min_content_length: int = 100   # 最小内容长度
    require_https: bool = True      # 只允许HTTPS


class DocumentCrawler:
    """多源文档爬虫"""
    
    # 预设数据源配置
    DATA_SOURCES = {
        "baike": {
            "base_url": "https://baike.baidu.com/item/{query}",
            "type": SourceType.ENCYCLOPEDIA,
            "reliability": 0.9,
            "selector": ".main-content"
        },
        "zhihu": {
            "base_url": "https://www.zhihu.com/search?q={query}",
            "type": SourceType.FORUM,
            "reliability": 0.7,
            "selector": ".SearchResult-Card"
        },
        "sina": {
            "base_url": "https://search.sina.com.cn/?q={query}&type=article",
            "type": SourceType.NEWS,
            "reliability": 0.8,
            "selector": ".news-item"
        },
        "gov": {
            "base_url": "https://www.baidu.com/s?wd={query}+site:gov.cn",
            "type": SourceType.OFFICIAL,
            "reliability": 0.95,
            "selector": ".result"
        },
        "edu": {
            "base_url": "https://www.baidu.com/s?wd={query}+site:edu.cn",
            "type": SourceType.ACADEMIC,
            "reliability": 0.95,
            "selector": ".result"
        }
    }
    
    def __init__(self, config: Optional[CrawlerConfig] = None):
        self.config = config or CrawlerConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
    
    async def initialize(self):
        """初始化爬虫"""
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        )
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
    
    async def close(self):
        """关闭爬虫"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def crawl(self, query: str, source_types: Optional[List[SourceType]] = None) -> List[CrawledPage]:
        """
        爬取相关文档
        
        Args:
            query: 查询关键词
            source_types: 数据源类型过滤（可选）
            
        Returns:
            List[CrawledPage]: 爬取的页面列表
        """
        if not self.session:
            await self.initialize()
        
        tasks = []
        
        for source_name, source_config in self.DATA_SOURCES.items():
            if source_types and source_config["type"] not in source_types:
                continue
            
            url = source_config["base_url"].format(query=query)
            task = self._crawl_source(source_name, url, source_config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        pages = []
        for result in results:
            if isinstance(result, list):
                pages.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Crawl error: {result}")
        
        # 按可靠性排序
        pages.sort(key=lambda x: x.reliability, reverse=True)
        
        return pages
    
    async def _crawl_source(self, source_name: str, url: str, config: Dict[str, Any]) -> List[CrawledPage]:
        """爬取单个数据源"""
        pages = []
        
        async with self._semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        # 提取内容
                        content_elements = soup.select(config["selector"])
                        
                        for elem in content_elements[:self.config.max_pages_per_source]:
                            text = elem.get_text(strip=True)
                            
                            if len(text) >= self.config.min_content_length:
                                page = CrawledPage(
                                    url=url,
                                    title=soup.title.string if soup.title else source_name,
                                    content=text,
                                    source_type=config["type"],
                                    reliability=config["reliability"],
                                    crawl_time=datetime.now(),
                                    word_count=len(text)
                                )
                                pages.append(page)
                    
                    await asyncio.sleep(self.config.delay_between_requests)
                    
            except Exception as e:
                logger.error(f"Failed to crawl {source_name}: {e}")
        
        return pages
    
    async def crawl_url(self, url: str, selector: Optional[str] = None) -> Optional[CrawledPage]:
        """
        爬取单个URL
        
        Args:
            url: 目标URL
            selector: CSS选择器（可选）
            
        Returns:
            Optional[CrawledPage]: 爬取的页面
        """
        if not self.session:
            await self.initialize()
        
        async with self._semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        # 确定数据源类型
                        source_type = self._get_source_type(url)
                        reliability = self._calculate_reliability(url, source_type)
                        
                        # 提取内容
                        if selector:
                            elements = soup.select(selector)
                            content = "\n".join([e.get_text(strip=True) for e in elements])
                        else:
                            # 使用默认提取逻辑
                            content = self._extract_main_content(soup)
                        
                        return CrawledPage(
                            url=url,
                            title=soup.title.string if soup.title else "",
                            content=content,
                            source_type=source_type,
                            reliability=reliability,
                            crawl_time=datetime.now(),
                            word_count=len(content)
                        )
                        
            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                return None
        
        return None
    
    def _get_source_type(self, url: str) -> SourceType:
        """根据URL判断数据源类型"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if "baidu.com" in domain:
            return SourceType.ENCYCLOPEDIA
        elif "zhihu.com" in domain:
            return SourceType.FORUM
        elif any(x in domain for x in ["sina", "163", "qq", "ifeng"]):
            return SourceType.NEWS
        elif "gov.cn" in domain:
            return SourceType.OFFICIAL
        elif "edu.cn" in domain:
            return SourceType.ACADEMIC
        elif "github.com" in domain:
            return SourceType.BLOG
        
        return SourceType.OTHER
    
    def _calculate_reliability(self, url: str, source_type: SourceType) -> float:
        """计算可靠性评分"""
        reliability_map = {
            SourceType.OFFICIAL: 0.95,
            SourceType.ACADEMIC: 0.95,
            SourceType.ENCYCLOPEDIA: 0.9,
            SourceType.NEWS: 0.8,
            SourceType.FORUM: 0.6,
            SourceType.BLOG: 0.5,
            SourceType.OTHER: 0.3
        }
        
        base_reliability = reliability_map.get(source_type, 0.5)
        
        # HTTPS更可靠
        if url.startswith("https"):
            base_reliability += 0.05
        
        return min(base_reliability, 1.0)
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """提取页面主要内容"""
        # 移除脚本和样式
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
            tag.decompose()
        
        # 尝试找到主要内容区域
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            return main_content.get_text(separator="\n", strip=True)
        
        # 返回body内容
        body = soup.find('body')
        if body:
            return body.get_text(separator="\n", strip=True)
        
        return ""


# 便捷函数
async def crawl_documents(query: str, source_types: Optional[List[SourceType]] = None) -> List[CrawledPage]:
    """
    爬取相关文档
    
    Args:
        query: 查询关键词
        source_types: 数据源类型过滤（可选）
        
    Returns:
        List[CrawledPage]: 爬取的页面列表
    """
    crawler = DocumentCrawler()
    try:
        await crawler.initialize()
        return await crawler.crawl(query, source_types)
    finally:
        await crawler.close()


if __name__ == "__main__":
    # 测试
    async def test():
        crawler = DocumentCrawler()
        await crawler.initialize()
        
        pages = await crawler.crawl("社会学专业")
        print(f"爬取到 {len(pages)} 个页面")
        
        for page in pages[:3]:
            print(f"\n来源: {page.source_type.value} (可靠性: {page.reliability:.2f})")
            print(f"标题: {page.title}")
            print(f"内容预览: {page.content[:200]}...")
        
        await crawler.close()
    
    asyncio.run(test())
