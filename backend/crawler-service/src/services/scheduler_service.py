"""
调度服务
负责定时触发爬虫Agent执行数据爬取任务
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import httpx
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import CrawlStatus, CrawlTaskType

logger = logging.getLogger(__name__)


class SchedulerConfig:
    """调度配置"""
    
    # 数据更新周期配置
    SCHEDULE_CONFIG = {
        "major_market_data": {
            "crawler_service_url": "http://localhost:8004",
            "task_type": CrawlTaskType.MAJOR.value,
            "interval_hours": 72,  # 每3天
            "priority": 1,
            "full_crawl": False
        },
        "university_admission_scores": {
            "crawler_service_url": "http://localhost:8004",
            "task_type": CrawlTaskType.UNIVERSITY.value,
            "interval_hours": 168,  # 每周
            "priority": 2,
            "full_crawl": False
        },
        "industry_trends": {
            "crawler_service_url": "http://localhost:8004",
            "task_type": CrawlTaskType.TREND.value,
            "interval_hours": 24,  # 每日
            "priority": 3,
            "full_crawl": False
        },
        "video_content": {
            "crawler_service_url": "http://localhost:8004",
            "task_type": CrawlTaskType.VIDEO.value,
            "interval_hours": 168,  # 每周
            "priority": 4,
            "full_crawl": False
        },
        "major_categories": {
            "crawler_service_url": "http://localhost:8004",
            "task_type": CrawlTaskType.MAJOR.value,
            "interval_hours": 720,  # 每月
            "priority": 5,
            "full_crawl": False
        }
    }
    
    # 默认爬取周期（小时）
    DEFAULT_INTERVAL_HOURS = 72
    
    # 调度服务端口
    SCHEDULER_PORT = 8006


class SchedulerService:
    """调度服务"""
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        self.config = config or SchedulerConfig()
        self.running_tasks: Dict[str, Dict[str, Any]] = {}
        self.last_run_times: Dict[str, datetime] = {}
    
    async def trigger_crawl(
        self,
        task_type: str,
        crawler_service_url: str,
        full_crawl: bool = False
    ) -> Dict[str, Any]:
        """
        触发爬虫任务
        
        Args:
            task_type: 任务类型 (major/university/video/trend)
            crawler_service_url: 爬虫服务URL
            full_crawl: 是否全量爬取
            
        Returns:
            任务信息字典
        """
        import uuid
        
        task_id = str(uuid.uuid4())
        
        logger.info(f"触发爬虫任务: task_type={task_type}, full_crawl={full_crawl}, task_id={task_id}")
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                if full_crawl:
                    # 全量爬取
                    response = await client.post(
                        f"{crawler_service_url}/api/v1/admin/crawler/full-crawl",
                        json={"task_type": task_type}
                    )
                else:
                    # 增量爬取
                    response = await client.post(
                        f"{crawler_service_url}/api/v1/admin/crawler/crawl",
                        json={"force": True}
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    self.running_tasks[task_id] = {
                        "task_id": task_id,
                        "task_type": task_type,
                        "status": CrawlStatus.RUNNING.value,
                        "started_at": datetime.utcnow().isoformat(),
                        "full_crawl": full_crawl,
                        "crawler_response": result
                    }
                    
                    return {
                        "task_id": task_id,
                        "status": "started",
                        "message": f"{'全量' if full_crawl else '增量'}爬取任务已启动",
                        "task_type": task_type,
                        "full_crawl": full_crawl
                    }
                else:
                    error_msg = f"触发爬虫失败: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "task_id": task_id,
                        "status": "failed",
                        "message": error_msg,
                        "task_type": task_type,
                        "full_crawl": full_crawl
                    }
                    
        except Exception as e:
            error_msg = f"触发爬虫异常: {str(e)}"
            logger.error(error_msg)
            return {
                "task_id": task_id,
                "status": "failed",
                "message": error_msg,
                "task_type": task_type,
                "full_crawl": full_crawl
            }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id in self.running_tasks:
            task_info = self.running_tasks[task_id]
            
            # 查询爬虫服务获取最新状态
            try:
                crawler_service_url = "http://localhost:8004"
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{crawler_service_url}/api/v1/crawler/status/{task_id}"
                    )
                    if response.status_code == 200:
                        crawler_status = response.json()
                        task_info["crawler_status"] = crawler_status
                        
                        # 更新本地状态
                        if crawler_status.get("status") == "completed":
                            task_info["status"] = CrawlStatus.COMPLETED.value
                        elif crawler_status.get("status") == "failed":
                            task_info["status"] = CrawlStatus.FAILED.value
                            
            except Exception as e:
                logger.warning(f"查询任务状态失败: {e}")
                
            return task_info
        return None
    
    def should_run_task(self, task_key: str) -> bool:
        """检查是否应该执行任务"""
        if task_key not in self.SCHEDULE_CONFIG:
            return False
            
        config = self.SCHEDULE_CONFIG[task_key]
        interval_hours = config.get("interval_hours", self.config.DEFAULT_INTERVAL_HOURS)
        
        if task_key not in self.last_run_times:
            return True
            
        last_run = self.last_run_times[task_key]
        time_since_last_run = (datetime.utcnow() - last_run).total_seconds() / 3600
        
        return time_since_last_run >= interval_hours
    
    async def run_scheduled_tasks(self):
        """运行所有定时任务"""
        logger.info("开始检查定时任务...")
        
        for task_key, config in self.config.SCHEDULE_CONFIG.items():
            if self.should_run_task(task_key):
                logger.info(f"执行定时任务: {task_key}")
                
                task_type = config.get("task_type", task_key)
                crawler_service_url = config.get("crawler_service_url", "http://localhost:8004")
                full_crawl = config.get("full_crawl", False)
                
                result = await self.trigger_crawl(
                    task_type=task_type,
                    crawler_service_url=crawler_service_url,
                    full_crawl=full_crawl
                )
                
                if result.get("status") == "started":
                    self.last_run_times[task_key] = datetime.utcnow()
                    
                logger.info(f"任务 {task_key} 执行结果: {result}")
    
    async def start_scheduler(self):
        """启动调度器"""
        logger.info("启动调度服务...")
        
        while True:
            try:
                await self.run_scheduled_tasks()
            except Exception as e:
                logger.error(f"调度任务执行错误: {e}")
            
            # 等待1小时后再次检查
            await asyncio.sleep(3600)


async def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scheduler = SchedulerService()
    
    # 立即执行一次定时任务检查
    await scheduler.run_scheduled_tasks()
    
    # 启动持续调度
    await scheduler.start_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
