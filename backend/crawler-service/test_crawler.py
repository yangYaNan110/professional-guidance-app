#!/usr/bin/env python3
"""
简单的专业信息爬取测试脚本
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 简单的配置
config = {
    "data_sources": {
        "阳光高考": {
            "base_url": "https://gaokao.chsi.com.cn",
            "delay": 3,
            "enabled": True
        }
    }
}

async def main():
    """主函数"""
    try:
        logger.info("启动专业信息爬取任务")
        
        # 导入爬虫类
        from src.services.major_basic_crawler import MajorBasicCrawler
        
        # 初始化爬虫
        crawler = MajorBasicCrawler(config)
        
        # 爬取专业分类
        logger.info("开始爬取专业分类...")
        categories = await crawler.crawl_major_categories()
        logger.info(f"爬取到 {len(categories)} 个专业分类")
        
        # 输出前几个分类
        for i, cat in enumerate(categories[:3]):
            logger.info(f"分类 {i+1}: {cat}")
        
        # 清理资源
        await crawler.cleanup()
        
        logger.info("专业信息爬取任务完成")
        
    except Exception as e:
        logger.error(f"爬取任务失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())