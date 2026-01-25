"""
专业推荐算法服务
基于热度指数、就业率、薪资水平等多维度进行专业推荐排序
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import psycopg2
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/employment'

class SortBy(Enum):
    """排序方式枚举"""
    HEAT_INDEX = "heat_index"          # 热度指数
    EMPLOYMENT_RATE = "employment_rate"  # 就业率
    AVG_SALARY = "avg_salary"          # 平均薪资
    FUTURE_PROSPECTS = "future_prospects_score"  # 发展前景
    INDUSTRY_DEMAND = "industry_demand_score"    # 行业需求
    CRAWLED_AT = "crawled_at"          # 最新时间

class SortOrder(Enum):
    """排序顺序枚举"""
    DESC = "desc"  # 降序
    ASC = "asc"    # 升序

@dataclass
class MajorRecommendation:
    """专业推荐数据结构"""
    id: int
    name: str
    category_name: str
    employment_rate: Optional[float]
    avg_salary: Optional[float]
    heat_index: Optional[float]
    industry_demand_score: Optional[float]
    future_prospects_score: Optional[float]
    talent_shortage: bool
    data_period: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "category_name": self.category_name,
            "employment_rate": float(self.employment_rate) if self.employment_rate is not None else None,
            "avg_salary": float(self.avg_salary) if self.avg_salary is not None else None,
            "heat_index": float(self.heat_index) if self.heat_index is not None else None,
            "industry_demand_score": float(self.industry_demand_score) if self.industry_demand_score is not None else None,
            "future_prospects_score": float(self.future_prospects_score) if self.future_prospects_score is not None else None,
            "talent_shortage": self.talent_shortage,
            "data_period": self.data_period,
            "description": self.description
        }

class MajorRecommendationEngine:
    """专业推荐引擎"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect_database(self) -> bool:
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cursor = self.conn.cursor()
            logger.info("✅ 数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """获取所有专业分类"""
        try:
            self.cursor.execute("""
                SELECT id, name, code, level 
                FROM major_categories 
                ORDER BY sort_order, name
            """)
            
            categories = []
            for row in self.cursor.fetchall():
                categories.append({
                    "id": row[0],
                    "name": row[1],
                    "code": row[2],
                    "level": row[3]
                })
            
            return categories
            
        except Exception as e:
            logger.error(f"❌ 获取分类失败: {e}")
            return []
    
    def get_major_recommendations(
        self,
        category_id: Optional[int] = None,
        sort_by: SortBy = SortBy.HEAT_INDEX,
        sort_order: SortOrder = SortOrder.DESC,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取专业推荐列表
        
        Args:
            category_id: 专业分类ID，None表示所有分类
            sort_by: 排序字段
            sort_order: 排序顺序
            page: 页码
            page_size: 每页数量
            
        Returns:
            推荐结果和分页信息
        """
        try:
            # 构建WHERE条件
            where_conditions = ["mmd.major_id IS NOT NULL"]
            params = []
            
            if category_id is not None:
                where_conditions.append("m.category_id = %s")
                params.append(category_id)
            
            where_clause = " AND ".join(where_conditions)
            
            # 构建ORDER BY子句
            valid_sort_fields = {
                SortBy.HEAT_INDEX: "mmd.heat_index",
                SortBy.EMPLOYMENT_RATE: "mmd.employment_rate", 
                SortBy.AVG_SALARY: "mmd.avg_salary",
                SortBy.FUTURE_PROSPECTS: "mmd.future_prospects_score",
                SortBy.INDUSTRY_DEMAND: "mmd.industry_demand_score",
                SortBy.CRAWLED_AT: "mmd.crawled_at"
            }
            
            order_field = valid_sort_fields.get(sort_by, "mmd.heat_index")
            order_direction = sort_order.value.upper()
            order_clause = f"ORDER BY {order_field} {order_direction}, mmd.heat_index DESC"
            
            # 计算分页
            offset = (page - 1) * page_size
            
            # 查询总数
            count_query = f"""
                SELECT COUNT(*)
                FROM majors m
                LEFT JOIN major_categories mc ON m.category_id = mc.id
                LEFT JOIN major_market_data mmd ON m.id = mmd.major_id
                WHERE {where_clause}
            """
            self.cursor.execute(count_query, params)
            total_count = self.cursor.fetchone()[0]
            
            # 查询数据
            query = f"""
                SELECT 
                    m.id,
                    m.name,
                    COALESCE(mc.name, '未分类') as category_name,
                    mmd.employment_rate,
                    mmd.avg_salary,
                    mmd.heat_index,
                    mmd.industry_demand_score,
                    mmd.future_prospects_score,
                    COALESCE(mmd.talent_shortage, false) as talent_shortage,
                    mmd.data_period
                FROM majors m
                LEFT JOIN major_categories mc ON m.category_id = mc.id
                LEFT JOIN major_market_data mmd ON m.id = mmd.major_id
                WHERE {where_clause}
                {order_clause}
                LIMIT %s OFFSET %s
            """
            
            query_params = params + [page_size, offset]
            self.cursor.execute(query, query_params)
            
            results = self.cursor.fetchall()
            
            # 构建推荐结果
            recommendations = []
            for row in results:
                recommendation = MajorRecommendation(
                    id=row[0],
                    name=row[1],
                    category_name=row[2],
                    employment_rate=row[3],
                    avg_salary=row[4],
                    heat_index=row[5],
                    industry_demand_score=row[6],
                    future_prospects_score=row[7],
                    talent_shortage=row[8],
                    data_period=row[9],
                    description=None
                )
                recommendations.append(recommendation)
            
            # 计算分页信息
            total_pages = (total_count + page_size - 1) // page_size
            
            result = {
                "success": True,
                "data": [rec.to_dict() for rec in recommendations],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "filters": {
                    "category_id": category_id,
                    "sort_by": sort_by.value,
                    "sort_order": sort_order.value
                },
                "message": f"成功获取 {len(recommendations)} 个专业推荐"
            }
            
            logger.info(f"📊 获取推荐: {len(recommendations)}/{total_count} 条记录 (第{page}页)")
            return result
            
        except Exception as e:
            logger.error(f"❌ 获取推荐失败: {e}")
            return {
                "success": False,
                "data": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False
                },
                "filters": {
                    "category_id": category_id,
                    "sort_by": sort_by.value,
                    "sort_order": sort_order.value
                },
                "message": f"获取推荐失败: {str(e)}"
            }
    
    def get_major_detail(self, major_id: int) -> Dict[str, Any]:
        """获取专业详情"""
        try:
            query = """
                SELECT 
                    m.id,
                    m.name,
                    m.code,
                    m.description,
                    m.training_objective,
                    m.main_courses,
                    m.employment_direction,
                    m.study_period,
                    m.degree_awarded,
                    m.national_key_major,
                    COALESCE(mc.name, '未分类') as category_name,
                    mmd.employment_rate,
                    mmd.avg_salary,
                    mmd.salary_growth_rate,
                    mmd.heat_index,
                    mmd.industry_demand_score,
                    mmd.future_prospects_score,
                    mmd.talent_shortage,
                    mmd.data_period,
                    mmd.employment_prospects,
                    mmd.source_urls as market_source_urls,
                    m.source_url as major_source_url
                FROM majors m
                LEFT JOIN major_categories mc ON m.category_id = mc.id
                LEFT JOIN major_market_data mmd ON m.id = mmd.major_id
                WHERE m.id = %s
            """
            
            self.cursor.execute(query, (major_id,))
            result = self.cursor.fetchone()
            
            if not result:
                return {
                    "success": False,
                    "message": "专业不存在"
                }
            
            # 构建专业详情 - 处理Decimal类型序列化
            def convert_decimal(value):
                if value is None:
                    return None
                return float(value) if hasattr(value, 'astype') else value
            
            detail = {
                "id": result[0],
                "name": result[1],
                "code": result[2],
                "description": result[3],
                "training_objective": result[4],
                "main_courses": result[5] or [],
                "employment_direction": result[6],
                "study_period": result[7],
                "degree_awarded": result[8],
                "national_key_major": result[9],
                "category_name": result[10],
                "market_data": {
                    "employment_rate": float(result[11]) if result[11] is not None else None,
                    "avg_salary": float(result[12]) if result[12] is not None else None,
                    "salary_growth_rate": float(result[13]) if result[13] is not None else None,
                    "heat_index": float(result[14]) if result[14] is not None else None,
                    "industry_demand_score": float(result[15]) if result[15] is not None else None,
                    "future_prospects_score": float(result[16]) if result[16] is not None else None,
                    "talent_shortage": result[17],
                    "data_period": result[18],
                    "employment_prospects": result[19]
                },
                "sources": {
                    "major_source_url": result[20],
                    "market_source_urls": result[21] or []
                }
            }
            
            return {
                "success": True,
                "data": detail,
                "message": "成功获取专业详情"
            }
            
        except Exception as e:
            logger.error(f"❌ 获取专业详情失败: {e}")
            return {
                "success": False,
                "message": f"获取专业详情失败: {str(e)}"
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取推荐统计信息"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_majors,
                    COUNT(CASE WHEN mmd.employment_rate >= 95 THEN 1 END) as high_employment,
                    COUNT(CASE WHEN mmd.avg_salary >= 15000 THEN 1 END) as high_salary,
                    COUNT(CASE WHEN mmd.talent_shortage = true THEN 1 END) as talent_shortage_count,
                    ROUND(AVG(mmd.employment_rate), 2) as avg_employment_rate,
                    ROUND(AVG(mmd.avg_salary), 2) as avg_salary,
                    ROUND(AVG(mmd.heat_index), 2) as avg_heat_index
                FROM majors m
                LEFT JOIN major_market_data mmd ON m.id = mmd.major_id
                WHERE mmd.major_id IS NOT NULL
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            
            statistics = {
                "total_majors": int(result[0]),
                "high_employment_majors": int(result[1]),
                "high_salary_majors": int(result[2]),
                "talent_shortage_majors": int(result[3]),
                "avg_employment_rate": float(result[4]) if result[4] else 0.0,
                "avg_salary": float(result[5]) if result[5] else 0.0,
                "avg_heat_index": float(result[6]) if result[6] else 0.0,
                "data_updated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": statistics,
                "message": "成功获取统计信息"
            }
            
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {
                "success": False,
                "message": f"获取统计信息失败: {str(e)}"
            }
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔚 数据库连接已关闭")

def main():
    """测试函数"""
    engine = MajorRecommendationEngine()
    
    try:
        if not engine.connect_database():
            return
        
        print("🧪 测试专业推荐引擎")
        
        # 测试获取推荐列表
        print("\\n1. 获取热度推荐 (前3个):")
        result = engine.get_major_recommendations(
            category_id=None,
            sort_by=SortBy.HEAT_INDEX,
            sort_order=SortOrder.DESC,
            page=1,
            page_size=3
        )
        
        if result["success"]:
            for i, major in enumerate(result["data"], 1):
                print(f"  {i}. {major['name']} (热度: {major['heat_index']:.1f})")
        
        # 测试按分类筛选
        print("\\n2. 获取工学类专业推荐:")
        result = engine.get_major_recommendations(
            category_id=1,  # 假设工学分类ID为1
            sort_by=SortBy.HEAT_INDEX,
            sort_order=SortOrder.DESC,
            page=1,
            page_size=5
        )
        
        if result["success"]:
            for i, major in enumerate(result["data"], 1):
                print(f"  {i}. {major['name']} (就业率: {major['employment_rate']}%)")
        
        # 测试获取统计信息
        print("\\n3. 统计信息:")
        stats = engine.get_statistics()
        if stats["success"]:
            data = stats["data"]
            print(f"  总专业数: {data['total_majors']}")
            print(f"  平均就业率: {data['avg_employment_rate']}%")
            print(f"  平均薪资: {data['avg_salary']}元")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
    finally:
        engine.close()

if __name__ == "__main__":
    main()