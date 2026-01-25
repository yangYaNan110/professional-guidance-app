#!/usr/bin/env python3
"""
专业信息爬取测试脚本
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.major_basic_crawler import MajorBasicCrawler
from src.services.config_loader import ConfigManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """主函数"""
    try:
        logger.info("启动专业信息爬取任务")
        
        # 加载配置
        config_loader = ConfigManager()
        config = config_loader.get_crawler_config()
        
        # 初始化爬虫
        crawler = MajorBasicCrawler(config)
        
        # 爬取专业分类
        logger.info("开始爬取专业分类...")
        categories = await crawler.crawl_major_categories()
        logger.info(f"爬取到 {len(categories)} 个专业分类")
        
        # 爬取专业基础信息
        logger.info("开始爬取专业基础信息...")
        majors = await crawler.crawl_majors_basic_info()
        logger.info(f"爬取到 {len(majors)} 个专业基础信息")
        
        # 输出统计信息
        stats = crawler.get_crawl_statistics()
        logger.info(f"爬取统计: {json.dumps(stats, ensure_ascii=False, indent=2)}")
        
        # 清理资源
        await crawler.cleanup()
        
        logger.info("专业信息爬取任务完成")
        
    except Exception as e:
        logger.error(f"爬取任务失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())