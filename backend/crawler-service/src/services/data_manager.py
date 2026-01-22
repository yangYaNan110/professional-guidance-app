"""数据管理器 - 专业行情数据存储与去重"""
import os
import sys
import logging
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quota_manager import quota_manager

logger = logging.getLogger(__name__)

class MajorDataManager:
    """专业数据管理器 - 保证数据库最多存储10000条最新数据"""
    
    MAX_RECORDS = 10000
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "market_data.db"
        )
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS major_market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(500) NOT NULL,
                major_name VARCHAR(200),
                category VARCHAR(100),
                source_url VARCHAR(1000) UNIQUE,
                source_website VARCHAR(100),
                employment_rate DECIMAL(5,2),
                avg_salary VARCHAR(100),
                admission_score DECIMAL(5,2),
                heat_index DECIMAL(5,2),
                trend_data TEXT,
                description TEXT,
                courses TEXT,
                career_prospects TEXT,
                crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawled_at ON major_market_data(crawled_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_major_name ON major_market_data(major_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON major_market_data(category)')
        
        conn.commit()
        conn.close()
        logger.info(f"数据库初始化完成: {self.db_path}")
    
    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def save_crawled_data(self, new_data: List[Dict]) -> int:
        """
        保存爬取的数据，并确保数据库不超过最大记录数
        策略：
        1. 配额检查（每个学科最多100条，总共不超过10000条）
        2. 去重（根据URL+标题）
        3. 插入新数据
        4. 如果超过10000条，删除最旧的记录
        """
        if not new_data:
            return 0
        
        # 获取分配计划
        quota_plan = quota_manager.get_distribution_plan(len(new_data))
        logger.info(f"配额分配计划: {quota_plan}")
        
        conn = self._get_conn()
        cursor = conn.cursor()
        
        saved_count = 0
        
        try:
            for item in new_data:
                category = item.get('category', '未知')
                
                # 1. 配额检查
                if not quota_manager.can_crawl(category):
                    logger.info(f"学科 {category} 已达配额上限，跳过")
                    continue
                
                # 2. 去重检查
                cursor.execute(
                    "SELECT id FROM major_market_data WHERE source_url = ?",
                    (item.get('source_url', ''),)
                )
                if cursor.fetchone():
                    continue
                
                # 3. 分配配额
                if not quota_manager.allocate_quota(category):
                    logger.info(f"无法为学科 {category} 分配配额，跳过")
                    continue
                
                # 4. 插入数据
                try:
                    cursor.execute('''
                        INSERT INTO major_market_data (
                            title, major_name, category, source_url, source_website,
                            employment_rate, avg_salary, admission_score, heat_index,
                            trend_data, description, courses, career_prospects
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('title', ''),
                        item.get('major_name'),
                        category,
                        item.get('source_url'),
                        item.get('source_website'),
                        item.get('employment_rate'),
                        item.get('avg_salary'),
                        item.get('admission_score'),
                        item.get('heat_index'),
                        json.dumps(item.get('trend_data')) if item.get('trend_data') else None,
                        item.get('description'),
                        json.dumps(item.get('courses')) if item.get('courses') else None,
                        item.get('career_prospects')
                    ))
                    
                    saved_count += 1
                    
                except sqlite3.IntegrityError:
                    # URL重复，跳过
                    continue
                except Exception as e:
                    logger.error(f"保存单条数据失败: {e}")
                    continue
            
            conn.commit()
            logger.info(f"成功保存 {saved_count} 条数据")
            
            # 检查并清理旧数据（确保总数不超过10000）
            self.ensure_max_records(cursor)
            self.ensure_max_records(cursor)
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        return saved_count
    
    def ensure_max_records(self, cursor = None):
        """确保数据库中只有最新的10000条数据"""
        conn = cursor.connection if cursor else self._get_conn()
        needs_close = cursor is None
        
        if needs_close:
            cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM major_market_data")
            current_count = cursor.fetchone()[0]
            
            if current_count > self.MAX_RECORDS:
                excess = current_count - self.MAX_RECORDS
                
                # 删除最旧的excess条记录
                cursor.execute('''
                    DELETE FROM major_market_data
                    WHERE id IN (
                        SELECT id FROM major_market_data
                        ORDER BY crawled_at ASC
                        LIMIT ?
                    )
                ''', (excess,))
                
                conn.commit()
                logger.info(f"已清理 {excess} 条旧数据，当前数据库共有 {min(current_count, self.MAX_RECORDS)} 条最新记录")
                
        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
            if not needs_close:
                conn.rollback()
        finally:
            if needs_close:
                conn.close()
    
    def get_market_data(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        sort_by: str = "crawled_at",
        order: str = "desc"
    ) -> Tuple[List[Dict], int]:
        """获取专业行情数据"""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # 构建查询条件
            where_clause = ""
            params = []
            if category:
                where_clause = "WHERE category = ?"
                params.append(category)
            
            # 排序
            order_dir = "DESC" if order.lower() == "desc" else "ASC"
            valid_sort_fields = ['crawled_at', 'heat_index', 'employment_rate', 'created_at']
            sort_field = sort_by if sort_by in valid_sort_fields else 'crawled_at'
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM major_market_data {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']
            
            # 查询数据
            offset = (page - 1) * page_size
            sql = f'''
                SELECT id, title, major_name, category, source_website,
                       employment_rate, avg_salary, heat_index,
                       crawled_at, description, courses
                FROM major_market_data
                {where_clause}
                ORDER BY {sort_field} {order_dir}
                LIMIT ? OFFSET ?
            '''
            
            params.extend([page_size, offset])
            cursor.execute(sql, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "title": row["title"],
                    "major_name": row["major_name"],
                    "category": row["category"],
                    "source_website": row["source_website"],
                    "employment_rate": row["employment_rate"],
                    "avg_salary": row["avg_salary"],
                    "heat_index": row["heat_index"],
                    "crawled_at": row["crawled_at"],
                    "description": row["description"],
                    "courses": json.loads(row["courses"]) if row["courses"] else []
                })
            
            return results, total
            
        finally:
            conn.close()
    
    def get_stats(self) -> Dict:
        """获取统计数据"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # 总数
            cursor.execute("SELECT COUNT(*) as total FROM major_market_data")
            stats["total"] = cursor.fetchone()["total"]
            
            # 按类别统计
            cursor.execute('''
                SELECT category, COUNT(*) as count
                FROM major_market_data
                GROUP BY category
                ORDER BY count DESC
            ''')
            stats["by_category"] = [
                {"category": row["category"], "count": row["count"]}
                for row in cursor.fetchall()
            ]
            
            # 最新爬取时间
            cursor.execute("SELECT MAX(crawled_at) as last_crawl FROM major_market_data")
            stats["last_crawl"] = cursor.fetchone()["last_crawl"]
            
            return stats
            
        finally:
            conn.close()
    
    def get_record_count(self) -> int:
        """获取当前数据条数"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM major_market_data")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_existing_urls(self) -> set:
        """获取所有现有数据的URL（用于去重）"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT source_url FROM major_market_data WHERE source_url != ''")
        urls = {row[0] for row in cursor.fetchall() if row[0]}
        conn.close()
        return urls
    
    def get_subject_data_count(self, category: str) -> int:
        """获取某个学科的数据条数"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM major_market_data WHERE category = ?", (category,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_subjects_needing_data(self, min_data: int = 10) -> List[str]:
        """获取需要补充数据的学科列表"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category FROM major_market_data 
            GROUP BY category 
            HAVING COUNT(*) < ?
        ''', (min_data,))
        
        # 获取当前有数据的学科中，数据不足的
        subjects_with_insufficient_data = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 获取所有配置的学科
        all_subjects = set(quota_manager.SUBJECT_QUOTAS.keys())
        existing_subjects = set(subjects_with_insufficient_data)
        
        # 找出完全没有数据的学科
        missing_subjects = all_subjects - existing_subjects
        
        return list(missing_subjects) + subjects_with_insufficient_data
    
    def ensure_min_data_for_all_subjects(self, min_data: int = 10) -> Dict[str, int]:
        """确保每个学科至少有min_data条数据
        
        Returns:
            补充数据的统计信息
        """
        subjects_needing = self.get_subjects_needing_data(min_data)
        if not subjects_needing:
            return {"status": "ok", "message": "所有学科数据充足"}
        
        result = {
            "status": "need_crawl",
            "subjects_needing": subjects_needing,
            "min_data_required": min_data
        }
        
        return result
    
    def batch_insert(self, data: List[Dict]):
        """批量插入数据"""
        return self.save_crawled_data(data)
    
    def delete_oldest_records(self, count: int):
        """删除最旧的count条记录"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM major_market_data
            WHERE id IN (
                SELECT id FROM major_market_data
                ORDER BY crawled_at ASC
                LIMIT ?
            )
        ''', (count,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
