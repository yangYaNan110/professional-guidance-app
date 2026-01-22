"""爬虫配额管理器 - 控制各学科爬取数量"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logging = logging.getLogger(__name__)

@dataclass
class SubjectQuota:
    """学科配额"""
    category: str           # 学科名称
    max_quota: int          # 最大配额
    current_count: int      # 当前已爬取数量
    priority: int           # 优先级（数字越大越热门）
    last_crawl: Optional[datetime] = None  # 最后爬取时间

class CrawlerQuotaManager:
    """爬虫配额管理器"""
    
    # 学科配额配置
    # 每个学科至少10条数据，冷门专业热门专业都是10条起步
    SUBJECT_QUOTAS = {
        # 热门学科（优先级高，但最少10条）
        "工学": {"quota": 100, "priority": 10},
        "理学": {"quota": 80, "priority": 9},
        "经济学": {"quota": 80, "priority": 9},
        "管理学": {"quota": 70, "priority": 8},
        
        # 中等学科
        "医学": {"quota": 60, "priority": 7},
        "法学": {"quota": 60, "priority": 7},
        "文学": {"quota": 50, "priority": 6},
        "教育学": {"quota": 50, "priority": 6},
        
        # 较少学科（但至少10条）
        "哲学": {"quota": 30, "priority": 4},
        "历史学": {"quota": 30, "priority": 4},
        "艺术学": {"quota": 40, "priority": 5},
        "农学": {"quota": 30, "priority": 4},
        "军事学": {"quota": 20, "priority": 3},
    }
    
    # 每个学科最少保证的数据量
    MIN_DATA_PER_SUBJECT = 10
    
    def __init__(self):
        self.quotas: Dict[str, SubjectQuota] = {}
        self.total_max = 10000
        self._init_quotas()
    
    def _init_quotas(self):
        """初始化各学科配额"""
        for category, config in self.SUBJECT_QUOTAS.items():
            self.quotas[category] = SubjectQuota(
                category=category,
                max_quota=config["quota"],
                current_count=0,
                priority=config["priority"]
            )
    
    def get_total_quota(self) -> int:
        """获取总配额"""
        return sum(q.max_quota for q in self.quotas.values())
    
    def get_remaining_quota(self) -> int:
        """获取剩余配额"""
        return self.total_max - sum(q.current_count for q in self.quotas.values())
    
    def get_quota_status(self) -> Dict:
        """获取配额状态"""
        return {
            "total_max": self.total_max,
            "total_used": sum(q.current_count for q in self.quotas.values()),
            "total_remaining": self.get_remaining_quota(),
            "subjects": {
                category: {
                    "max_quota": quota.max_quota,
                    "current": quota.current_count,
                    "remaining": quota.max_quota - quota.current_count,
                    "priority": quota.priority
                }
                for category, quota in self.quotas.items()
            }
        }
    
    def get_hot_categories(self, limit: int = 10) -> List[Dict]:
        """获取学科列表（按优先级排序）
        
        规则：所有配置的学科都必须返回，即使某些学科暂时没有数据
        每个学科至少保证10条数据展示
        
        Args:
            limit: 返回数量限制，默认10个
        
        Returns:
            学科列表，每个包含name、priority、quota、current
        """
        # 按优先级降序排序
        sorted_subjects = sorted(
            self.quotas.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        # 取前N个（如果配置了超过limit个学科）
        result = []
        for i, (category, quota) in enumerate(sorted_subjects[:limit]):
            result.append({
                "id": i + 1,
                "name": category,
                "priority": quota.priority,
                "quota": quota.max_quota,
                "current": quota.current_count,
                "has_enough_data": quota.current_count >= self.MIN_DATA_PER_SUBJECT
            })
        
        return result
    
    def get_all_subjects(self) -> List[Dict]:
        """获取所有配置的学科（不限制数量）
        
        Returns:
            所有学科列表，包括没有数据的学科
        """
        sorted_subjects = sorted(
            self.quotas.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        result = []
        for i, (category, quota) in enumerate(sorted_subjects):
            result.append({
                "id": i + 1,
                "name": category,
                "priority": quota.priority,
                "quota": quota.max_quota,
                "current": quota.current_count,
                "has_enough_data": quota.current_count >= self.MIN_DATA_PER_SUBJECT
            })
        
        return result
    
    def can_crawl(self, category: str) -> bool:
        """检查是否可以爬取该学科"""
        if category not in self.quotas:
            # 未知学科，默认使用最小配额
            return True
        
        quota = self.quotas[category]
        return quota.current_count < quota.max_quota
    
    def get_remaining_for_category(self, category: str) -> int:
        """获取该学科剩余配额"""
        if category not in self.quotas:
            return 20  # 未知学科默认20条
        
        return self.quotas[category].max_quota - self.quotas[category].current_count
    
    def allocate_quota(self, category: str, count: int = 1) -> bool:
        """分配配额"""
        if category not in self.quotas:
            # 未知学科，初始化配额
            self.quotas[category] = SubjectQuota(
                category=category,
                max_quota=20,  # 默认20条
                current_count=0,
                priority=1
            )
        
        if self.quotas[category].current_count + count > self.quotas[category].max_quota:
            return False
        
        self.quotas[category].current_count += count
        self.quotas[category].last_crawl = datetime.utcnow()
        return True
    
    def get_crawl_order(self) -> List[str]:
        """获取爬取顺序（按优先级降序）"""
        return sorted(
            self.quotas.keys(),
            key=lambda x: self.quotas[x].priority,
            reverse=True
        )
    
    def get_distribution_plan(self, total_items: int) -> Dict[str, int]:
        """获取爬取分配计划（按学科优先级分配）"""
        if total_items > self.total_max:
            total_items = self.total_max
        
        plan = {}
        remaining = total_items
        
        # 按优先级排序
        sorted_subjects = sorted(
            self.quotas.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        for category, quota in sorted_subjects:
            available = quota.max_quota - quota.current_count
            if available <= 0:
                continue
            
            # 按优先级分配：优先级高的学科分配更多
            if remaining <= 0:
                break
            
            # 计算分配数量
            if remaining >= available:
                allocate = available
            else:
                # 按比例分配
                allocate = max(1, int(available * (remaining / sum(q.max_quota for q in self.quotas.values()))))
                allocate = min(allocate, available)
            
            plan[category] = allocate
            remaining -= allocate
        
        return plan
    
    def reset_counts(self):
        """重置计数器（用于新一轮爬取）"""
        for quota in self.quotas.values():
            quota.current_count = 0
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_used = sum(q.current_count for q in self.quotas.values())
        total_quota = sum(q.max_quota for q in self.quotas.values())
        
        return {
            "total_max": self.total_max,
            "total_quota": total_quota,
            "total_used": total_used,
            "utilization_rate": round(total_used / self.total_max * 100, 2) if self.total_max > 0 else 0,
            "subjects": {
                category: {
                    "quota": quota.max_quota,
                    "used": quota.current_count,
                    "rate": round(quota.current_count / quota.max_quota * 100, 2) if quota.max_quota > 0 else 0,
                    "priority": quota.priority
                }
                for category, quota in self.quotas.items()
            }
        }


# 单例实例
quota_manager = CrawlerQuotaManager()
