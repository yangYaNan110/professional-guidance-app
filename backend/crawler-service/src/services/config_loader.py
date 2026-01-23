"""
配置加载服务
从JSON配置文件读取爬虫调度策略和业务数据配置
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class CrawlerConfig:
    """爬虫配置类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认从环境变量或默认路径读取
        """
        if config_path is None:
            # 默认配置路径
            config_path = os.getenv(
                "CRAWLER_CONFIG_PATH",
                str(Path(__file__).parent.parent.parent.parent / "config" / "crawler_config.json")
            )
        
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"成功加载配置文件: {self.config_path}")
            logger.info(f"配置版本: {self.config.get('version', 'unknown')}")
        except FileNotFoundError:
            logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            self.config = self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"配置文件解析失败: {e}，使用默认配置")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version": "1.0.0",
            "force_re_crawl_on_startup": False,
            "data_sources": {},
            "scheduler": {
                "check_interval_seconds": 3600,
                "default_timezone": "Asia/Shanghai",
                "task_execution_window": {
                    "start": "02:00",
                    "end": "06:00"
                }
            },
            "cache": {
                "enabled": True,
                "default_ttl_hours": 12
            },
            "crawler": {
                "default_request_delay_seconds": 2,
                "max_concurrent_requests": 5
            }
        }
    
    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()
    
    @property
    def version(self) -> str:
        """获取配置版本"""
        return self.config.get("version", "1.0.0")
    
    @property
    def force_re_crawl_on_startup(self) -> bool:
        """获取启动时是否强制重爬"""
        return self.config.get("force_re_crawl_on_startup", False)
    
    @force_re_crawl_on_startup.setter
    def force_re_crawl_on_startup(self, value: bool) -> None:
        """设置启动时是否强制重爬"""
        self.config["force_re_crawl_on_startup"] = value
    
    def get_data_source_config(self, data_type: str) -> Optional[Dict[str, Any]]:
        """
        获取指定数据类型的数据源配置
        
        Args:
            data_type: 数据类型，如 major_categories, majors, universities 等
            
        Returns:
            数据源配置字典，如果不存在返回None
        """
        return self.config.get("data_sources", {}).get(data_type)
    
    def get_all_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """获取所有数据源配置"""
        return self.config.get("data_sources", {})
    
    def get_enabled_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """获取所有启用的数据源配置"""
        all_sources = self.get_all_data_sources()
        return {
            key: config for key, config in all_sources.items()
            if config.get("enabled", True)
        }
    
    def get_schedule_tasks(self) -> List[Dict[str, Any]]:
        """获取所有需要调度的任务配置"""
        enabled_sources = self.get_enabled_data_sources()
        tasks = []
        
        for task_key, config in enabled_sources.items():
            if config.get("crawl_strategy") != "none":
                tasks.append({
                    "task_key": task_key,
                    "description": config.get("description", ""),
                    "table_name": config.get("table_name", ""),
                    "update_cycle_hours": config.get("update_cycle_hours", 72),
                    "priority": config.get("priority", 10),
                    "crawl_strategy": config.get("crawl_strategy", "incremental"),
                    "data_source": config.get("data_source", ""),
                    "cache_ttl_hours": config.get("cache_ttl_hours", 12),
                    "quota": config.get("quota")
                })
        
        # 按优先级排序
        tasks.sort(key=lambda x: x.get("priority", 10))
        return tasks
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """获取调度器配置"""
        return self.config.get("scheduler", {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return self.config.get("cache", {})
    
    def get_crawler_config(self) -> Dict[str, Any]:
        """获取爬虫配置"""
        return self.config.get("crawler", {})
    
    def get_update_cycle_hours(self, data_type: str) -> int:
        """
        获取指定数据类型的更新周期
        
        Args:
            data_type: 数据类型
            
        Returns:
            更新周期（小时）
        """
        config = self.get_data_source_config(data_type)
        if config:
            return config.get("update_cycle_hours", 72)
        return 72  # 默认72小时
    
    def is_enabled(self, data_type: str) -> bool:
        """检查数据类型是否启用"""
        config = self.get_data_source_config(data_type)
        return config.get("enabled", True) if config else True
    
    def get_quota_config(self, data_type: str) -> Optional[Dict[str, Any]]:
        """获取指定数据类型的配额配置"""
        config = self.get_data_source_config(data_type)
        if config:
            return config.get("quota")
        return None
    
    def get_coverage_requirement(self, data_type: str) -> Optional[Dict[str, Any]]:
        """获取数据覆盖要求"""
        config = self.get_data_source_config(data_type)
        if config:
            return config.get("coverage_requirement")
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转为字典"""
        return self.config
    
    def save(self, output_path: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            output_path: 输出路径，默认覆盖原文件
        """
        path = output_path or self.config_path
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        logger.info(f"配置已保存到: {path}")


class ConfigManager:
    """配置管理器 - 单例模式"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[CrawlerConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = CrawlerConfig()
    
    @property
    def config(self) -> CrawlerConfig:
        """获取配置对象"""
        return self._config
    
    def reload(self) -> None:
        """重新加载配置"""
        self._config = CrawlerConfig()
    
    def get_data_source_config(self, data_type: str) -> Optional[Dict[str, Any]]:
        """获取数据源配置"""
        return self._config.get_data_source_config(data_type)
    
    def get_schedule_tasks(self) -> List[Dict[str, Any]]:
        """获取调度任务列表"""
        return self._config.get_schedule_tasks()
    
    @property
    def force_re_crawl_on_startup(self) -> bool:
        """获取启动时是否强制重爬"""
        return self._config.force_re_crawl_on_startup


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    return config_manager


def get_crawler_config() -> CrawlerConfig:
    """获取爬虫配置"""
    return config_manager.config
