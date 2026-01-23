"""
Redis缓存服务
提供数据缓存功能，支持缓存读写、失效、统计等操作
"""

import json
import logging
from datetime import datetime
from typing import Optional, Any, Dict, List
import redis
import os

logger = logging.getLogger(__name__)


class RedisConfig:
    """Redis配置"""
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.password = os.getenv("REDIS_PASSWORD", "")
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))


class CacheKeyBuilder:
    """缓存键构建器"""
    
    @staticmethod
    def categories(all_key: str = "all") -> str:
        return f"categories:{all_key}"
    
    @staticmethod
    def category(category_id: int) -> str:
        return f"categories:{category_id}"
    
    @staticmethod
    def majors_list(page: int, category: Optional[str] = None) -> str:
        if category:
            return f"majors:list:{category}:{page}"
        return f"majors:list:all:{page}"
    
    @staticmethod
    def major(major_id: int) -> str:
        return f"majors:{major_id}"
    
    @staticmethod
    def universities_list(page: int, province: Optional[str] = None) -> str:
        if province:
            return f"universities:list:{province}:{page}"
        return f"universities:list:all:{page}"
    
    @staticmethod
    def university(university_id: int) -> str:
        return f"universities:{university_id}"
    
    @staticmethod
    def admission_scores(university_id: int, year: Optional[int] = None) -> str:
        if year:
            return f"admission:{university_id}:{year}"
        return f"admission:{university_id}:latest"
    
    @staticmethod
    def market_data(category: Optional[str] = None) -> str:
        if category:
            return f"market-data:{category}"
        return "market-data:all"
    
    @staticmethod
    def industry_trends(industry: Optional[str] = None) -> str:
        if industry:
            return f"trends:{industry}"
        return "trends:all"
    
    @staticmethod
    def videos_list(major: str, page: int) -> str:
        return f"videos:{major}:{page}"
    
    @staticmethod
    def crawl_history_list(page: int) -> str:
        return f"crawl-history:{page}"
    
    @staticmethod
    def quota_status() -> str:
        return "quota:status"
    
    @staticmethod
    def crawl_task(task_id: str) -> str:
        return f"crawl-task:{task_id}"


class RedisCacheService:
    """Redis缓存服务"""
    
    # 缓存TTL配置（秒）
    TTL_CONFIG = {
        "categories:all": 86400,        # 24小时
        "categories:*": 86400,          # 24小时
        "majors:list:*": 43200,         # 12小时
        "majors:*": 21600,              # 6小时
        "universities:list:*": 43200,   # 12小时
        "universities:*": 21600,        # 6小时
        "admission:*": 86400,           # 24小时
        "market-data:*": 43200,         # 12小时
        "trends:*": 43200,              # 12小时
        "videos:*": 86400,              # 24小时
        "crawl-history:*": 3600,        # 1小时
        "quota:*": 3600,                # 1小时
        "crawl-task:*": 86400,          # 24小时
    }
    
    def __init__(self, config: Optional[RedisConfig] = None):
        self.config = config or RedisConfig()
        self._client: Optional[redis.Redis] = None
    
    def _get_client(self) -> redis.Redis:
        """获取Redis客户端"""
        if self._client is None:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password if self.config.password else None,
                db=self.config.db,
                max_connections=self.config.max_connections,
                decode_responses=True
            )
        return self._client
    
    def _get_ttl(self, key: str) -> int:
        """获取缓存TTL"""
        # 精确匹配
        if key in self.TTL_CONFIG:
            return self.TTL_CONFIG[key]
        
        # 模式匹配
        for pattern, ttl in self.TTL_CONFIG.items():
            if pattern.endswith('*'):
                prefix = pattern[:-1]
                if key.startswith(prefix):
                    return ttl
        
        # 默认TTL
        return 3600  # 1小时
    
    def _serialize(self, value: Any) -> str:
        """序列化值"""
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, default=str)
    
    def _deserialize(self, value: str) -> Any:
        """反序列化值"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    # ========== 基本操作 ==========
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            client = self._get_client()
            value = client.get(key)
            return self._deserialize(value) if value else None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            client = self._get_client()
            ttl = ttl or self._get_ttl(key)
            serialized = self._serialize(value)
            client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            client = self._get_client()
            client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """批量删除匹配模式的缓存"""
        try:
            client = self._get_client()
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE pattern error for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            client = self._get_client()
            return bool(client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间"""
        try:
            client = self._get_client()
            return bool(client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    # ========== 缓存模式操作 ==========
    
    def invalidate_categories(self):
        """清除学科分类缓存"""
        return self.delete_pattern("categories:*")
    
    def invalidate_majors(self):
        """清除专业列表缓存"""
        return self.delete_pattern("majors:*")
    
    def invalidate_majors_list(self, category: Optional[str] = None):
        """清除专业列表缓存"""
        if category:
            return self.delete_pattern(f"majors:list:{category}:*")
        return self.delete_pattern("majors:list:*")
    
    def invalidate_universities(self):
        """清除大学缓存"""
        return self.delete_pattern("universities:*")
    
    def invalidate_universities_list(self, province: Optional[str] = None):
        """清除大学列表缓存"""
        if province:
            return self.delete_pattern(f"universities:list:{province}:*")
        return self.delete_pattern("universities:list:*")
    
    def invalidate_admission_scores(self, university_id: Optional[int] = None):
        """清除录取分数缓存"""
        if university_id:
            return self.delete_pattern(f"admission:{university_id}:*")
        return self.delete_pattern("admission:*")
    
    def invalidate_market_data(self, category: Optional[str] = None):
        """清除行情数据缓存"""
        if category:
            return self.delete_pattern(f"market-data:{category}")
        return self.delete_pattern("market-data:*")
    
    def invalidate_trends(self, industry: Optional[str] = None):
        """清除行业趋势缓存"""
        if industry:
            return self.delete_pattern(f"trends:{industry}")
        return self.delete_pattern("trends:*")
    
    def invalidate_videos(self, major: Optional[str] = None):
        """清除视频缓存"""
        if major:
            return self.delete_pattern(f"videos:{major}:*")
        return self.delete_pattern("videos:*")
    
    def invalidate_crawl_history(self):
        """清除爬取历史缓存"""
        return self.delete_pattern("crawl-history:*")
    
    def invalidate_quota_status(self):
        """清除配额状态缓存"""
        return self.delete_pattern("quota:*")
    
    def invalidate_all_data(self):
        """清除所有数据缓存（爬取完成后调用）"""
        counts = 0
        counts += self.invalidate_categories()
        counts += self.invalidate_majors()
        counts += self.invalidate_universities()
        counts += self.invalidate_admission_scores()
        counts += self.invalidate_market_data()
        counts += self.invalidate_trends()
        counts += self.invalidate_videos()
        counts += self.invalidate_crawl_history()
        counts += self.invalidate_quota_status()
        return counts
    
    # ========== 统计数据 ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            client = self._get_client()
            info = client.info("memory")
            return {
                "used_memory": info.get("used_memory_human", "N/A"),
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "max_memory": info.get("maxmemory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": client.dbsize()
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {"error": str(e)}
    
    def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
        """获取缓存键的详细信息"""
        try:
            client = self._get_client()
            ttl = client.ttl(key)
            value = client.get(key)
            
            if value is None:
                return None
                
            return {
                "key": key,
                "value": self._deserialize(value)[:100] + "..." if len(str(value)) > 100 else self._deserialize(value),
                "ttl": ttl,
                "remaining_seconds": ttl,
                "size_bytes": len(value)
            }
        except Exception as e:
            logger.error(f"Redis cache info error for {key}: {e}")
            return None
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            client = self._get_client()
            return client.ping()
        except Exception as e:
            logger.error(f"Redis health check error: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None


# 全局缓存服务实例
cache_service = RedisCacheService()


def get_cache_service() -> RedisCacheService:
    """获取缓存服务实例"""
    return cache_service
