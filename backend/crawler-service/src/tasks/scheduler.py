"""定时爬虫任务 - 每3天自动执行"""
import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.data_manager import MajorDataManager
from services.crawler import MajorDataCrawler, generate_mock_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduledCrawler:
    """定时爬虫任务管理器"""
    
    def __init__(self):
        self.data_manager = MajorDataManager()
        self.crawler = MajorDataCrawler()
        self.crawl_interval_days = 3
        self.last_crawl_time = None
        self.is_running = False
    
    async def run_scheduled_crawl(self):
        """执行定时爬取任务"""
        if self.is_running:
            logger.warning("爬虫任务正在运行中，跳过本次调度")
            return
        
        self.is_running = True
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"开始执行定时爬虫任务...")
            
            # 1. 爬取数据
            logger.info("步骤1: 爬取数据...")
            new_data = await self.crawler.crawl_all_sources()
            
            if not new_data:
                # 使用模拟数据（测试用）
                logger.info("未获取到数据，使用模拟数据测试...")
                new_data = generate_mock_data(10)
            
            logger.info(f"获取到 {len(new_data)} 条新数据")
            
            # 2. 保存数据（自动去重和数量限制）
            logger.info("步骤2: 保存数据...")
            saved_count = self.data_manager.save_crawled_data(new_data)
            
            # 3. 统计信息
            current_count = self.data_manager.get_record_count()
            
            self.last_crawl_time = start_time
            
            logger.info("=" * 50)
            logger.info("定时爬虫任务完成")
            logger.info(f"  - 新增数据: {saved_count} 条")
            logger.info(f"  - 数据库总量: {current_count} 条")
            logger.info(f"  - 最大容量: {self.data_manager.MAX_RECORDS} 条")
            logger.info(f"  - 执行时间: {start_time}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"定时爬虫任务失败: {e}")
        finally:
            self.is_running = False
    
    def should_run(self) -> bool:
        """检查是否应该执行爬取"""
        if self.last_crawl_time is None:
            return True
        
        elapsed = datetime.utcnow() - self.last_crawl_time
        return elapsed.days >= self.crawl_interval_days
    
    def get_status(self) -> dict:
        """获取爬虫状态"""
        return {
            "is_running": self.is_running,
            "last_crawl_time": self.last_crawl_time.isoformat() if self.last_crawl_time else None,
            "next_crawl_time": (
                self.last_crawl_time + timedelta(days=self.crawl_interval_days)
            ).isoformat() if self.last_crawl_time else "立即执行",
            "should_run": self.should_run(),
            "interval_days": self.crawl_interval_days
        }


async def run_scheduler():
    """运行调度器"""
    logger.info("启动定时爬虫调度器...")
    
    scheduler = ScheduledCrawler()
    
    while True:
        try:
            if scheduler.should_run():
                await scheduler.run_scheduled_crawl()
            else:
                status = scheduler.get_status()
                next_run = status.get("next_crawl_time", "未知")
                logger.info(f"爬虫任务已在 {status['last_crawl_time']} 执行，下一次: {next_run}")
            
            # 每小时检查一次
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"调度器异常: {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    print("启动定时爬虫...")
    asyncio.run(run_scheduler())
