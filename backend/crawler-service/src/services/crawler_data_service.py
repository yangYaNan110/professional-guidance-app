"""
爬虫数据模块数据访问层
数据库版本: 1.0.0
日期: 2026-01-23
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from models.database import (
    Major, MajorMarketData, University, AdmissionScore,
    IndustryTrend, VideoContent, CrawlHistory, CrawlQuota,
    MajorCategory, MajorListResponse, UniversityListResponse,
    MajorMarketDataListResponse, AdmissionScoreListResponse,
    IndustryTrendListResponse, VideoContentListResponse,
    CrawlHistoryListResponse, CrawlQuotaListResponse
)

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """数据库配置"""
    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.database = os.getenv("POSTGRES_DB", "employment")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")


class CrawlerDataService:
    """爬虫数据访问服务"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._connection = None
    
    def _get_connection(self):
        """获取数据库连接"""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password
            )
        return self._connection
    
    def _close_connection(self):
        """关闭数据库连接"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    # =====================================================
    # 学科分类操作
    # =====================================================
    
    def get_categories(self, parent_id: Optional[int] = None) -> List[MajorCategory]:
        """获取学科分类列表"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if parent_id is None:
                    cursor.execute("SELECT * FROM major_categories WHERE parent_id IS NULL ORDER BY sort_order")
                else:
                    cursor.execute("SELECT * FROM major_categories WHERE parent_id = %s ORDER BY sort_order", (parent_id,))
                rows = cursor.fetchall()
                return [MajorCategory(**row) for row in rows]
        except Exception as e:
            logger.error(f"获取学科分类失败: {e}")
            raise
    
    def get_category_by_id(self, category_id: int) -> Optional[MajorCategory]:
        """根据ID获取学科分类"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM major_categories WHERE id = %s", (category_id,))
                row = cursor.fetchone()
                return MajorCategory(**row) if row else None
        except Exception as e:
            logger.error(f"获取学科分类失败: {e}")
            raise
    
    # =====================================================
    # 专业操作
    # =====================================================
    
    def get_majors(
        self,
        category_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> MajorListResponse:
        """获取专业列表"""
        conn = self._get_connection()
        try:
            offset = (page - 1) * page_size
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 获取总数
                if category_id:
                    cursor.execute("SELECT COUNT(*) FROM majors WHERE category_id = %s", (category_id,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM majors")
                count_result = cursor.fetchone()
                total = count_result['count'] if count_result else 0

                # 获取数据
                if category_id:
                    cursor.execute(
                        "SELECT * FROM majors WHERE category_id = %s ORDER BY heat_index DESC NULLS LAST LIMIT %s OFFSET %s",
                        (category_id, page_size, offset)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM majors ORDER BY heat_index DESC NULLS LAST LIMIT %s OFFSET %s",
                        (page_size, offset)
                    )
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    # 转换core_courses字段（确保始终是列表）
                    courses_val = row.get('core_courses')
                    if courses_val and isinstance(courses_val, str):
                        if courses_val and courses_val != '{}':
                            row['core_courses'] = courses_val.strip('{}').split(',')
                        else:
                            row['core_courses'] = []
                    elif courses_val is None or courses_val == '{}':
                        row['core_courses'] = []
                    data.append(Major(**row))
                
                return MajorListResponse(data=data, total=total, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"获取专业列表失败: {e}")
            raise
    
    def get_major_by_id(self, major_id: int) -> Optional[Major]:
        """根据ID获取专业"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM majors WHERE id = %s", (major_id,))
                row = cursor.fetchone()
                if row:
                    # 转换core_courses字段（确保始终是列表）
                    courses_val = row.get('core_courses')
                    if courses_val and isinstance(courses_val, str):
                        if courses_val and courses_val != '{}':
                            row['core_courses'] = courses_val.strip('{}').split(',')
                        else:
                            row['core_courses'] = []
                    elif courses_val is None or courses_val == '{}':
                        row['core_courses'] = []
                    return Major(**row)
                return None
        except Exception as e:
            logger.error(f"获取专业失败: {e}")
            raise
    
    def insert_major(self, major: Major) -> int:
        """插入专业"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                core_courses_str = '{' + ','.join(major.core_courses) + '}' if major.core_courses else '{}'
                cursor.execute("""
                    INSERT INTO majors (name, category_id, category_name, description, core_courses, 
                                       employment_rate, avg_salary, heat_index)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    major.name, major.category_id, major.category_name, major.description,
                    core_courses_str, major.employment_rate, major.avg_salary, major.heat_index
                ))
                major_id_result = cursor.fetchone()
                major_id = major_id_result[0] if major_id_result else 0
                conn.commit()
                return major_id
        except Exception as e:
            conn.rollback()
            logger.error(f"插入专业失败: {e}")
            raise
    
    # =====================================================
    # 专业行情数据操作
    # =====================================================
    
    def get_major_market_data(
        self,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> MajorMarketDataListResponse:
        """获取专业行情数据列表"""
        conn = self._get_connection()
        try:
            offset = (page - 1) * page_size
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 获取总数
                if category:
                    cursor.execute("SELECT COUNT(*) FROM major_market_data WHERE category = %s", (category,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM major_market_data")
                count_result = cursor.fetchone()
                total = count_result['count'] if count_result else 0

                # 获取数据
                if category:
                    cursor.execute("""
                        SELECT * FROM major_market_data 
                        WHERE category = %s 
                        ORDER BY crawled_at DESC 
                        LIMIT %s OFFSET %s
                    """, (category, page_size, offset))
                else:
                    cursor.execute("""
                        SELECT * FROM major_market_data 
                        ORDER BY crawled_at DESC 
                        LIMIT %s OFFSET %s
                    """, (page_size, offset))
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    # 转换JSON字段
                    if row.get('courses'):
                        courses_val = row['courses']
                        if isinstance(courses_val, str) and courses_val:
                            row['courses'] = courses_val.strip('{}').split(',') if courses_val and courses_val != '{}' else []
                        elif courses_val == '{}':
                            row['courses'] = []
                    else:
                        row['courses'] = []
                    
                    if row.get('trend_data'):
                        trend_val = row['trend_data']
                        if isinstance(trend_val, str) and trend_val:
                            try:
                                import json
                                row['trend_data'] = json.loads(trend_val)
                            except:
                                row['trend_data'] = {}
                    data.append(MajorMarketData(**row))
                
                return MajorMarketDataListResponse(data=data, total=total, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"获取专业行情数据失败: {e}")
            raise
    
    def insert_major_market_data(self, data: MajorMarketData) -> int:
        """插入专业行情数据"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                courses_str = None
                if data.courses:
                    courses_str = '{' + ','.join(data.courses) + '}'
                
                cursor.execute("""
                    INSERT INTO major_market_data (
                        title, major_name, category, source_url, source_website,
                        employment_rate, avg_salary, admission_score, heat_index,
                        trend_data, description, courses, career_prospects
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_url) DO NOTHING
                    RETURNING id
                """, (
                    data.title, data.major_name, data.category, data.source_url, data.source_website,
                    data.employment_rate, data.avg_salary, data.admission_score, data.heat_index,
                    str(data.trend_data) if data.trend_data else None,
                    data.description, courses_str, data.career_prospects
                ))
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else 0
        except Exception as e:
            conn.rollback()
            logger.error(f"插入专业行情数据失败: {e}")
            raise
    
    # =====================================================
    # 大学操作
    # =====================================================
    
    def get_universities(
        self,
        province: Optional[str] = None,
        level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> UniversityListResponse:
        """获取大学列表"""
        conn = self._get_connection()
        try:
            offset = (page - 1) * page_size
            conditions = []
            params = []
            
            if province:
                conditions.append("province = %s")
                params.append(province)
            if level:
                conditions.append("level = %s")
                params.append(level)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 获取总数
                cursor.execute(f"SELECT COUNT(*) FROM universities WHERE {where_clause}", tuple(params))
                count_result = cursor.fetchone()
                total = count_result['count'] if count_result else 0

                # 获取数据
                params.extend([page_size, offset])
                cursor.execute(f"""
                    SELECT * FROM universities 
                    WHERE {where_clause} 
                    ORDER BY employment_rate DESC NULLS LAST 
                    LIMIT %s OFFSET %s
                """, tuple(params))
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    if row.get('major_strengths') and isinstance(row['major_strengths'], str):
                        row['major_strengths'] = row['major_strengths'].strip('{}').split(',') if row['major_strengths'] else []
                    data.append(University(**row))
                
                return UniversityListResponse(data=data, total=total, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"获取大学列表失败: {e}")
            raise
    
    def get_university_by_id(self, university_id: int) -> Optional[University]:
        """根据ID获取大学"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM universities WHERE id = %s", (university_id,))
                row = cursor.fetchone()
                if row:
                    if row.get('major_strengths') and isinstance(row['major_strengths'], str):
                        row['major_strengths'] = row['major_strengths'].strip('{}').split(',') if row['major_strengths'] else []
                    return University(**row)
                return None
        except Exception as e:
            logger.error(f"获取大学失败: {e}")
            raise
    
    def insert_university(self, university: University) -> int:
        """插入大学"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                major_strengths_str = None
                if university.major_strengths:
                    major_strengths_str = '{' + ','.join(university.major_strengths) + '}'
                
                cursor.execute("""
                    INSERT INTO universities (name, level, province, city, employment_rate, type,
                                            location, founded_year, website, major_strengths)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    university.name, university.level, university.province, university.city,
                    university.employment_rate, university.type, university.location,
                    university.founded_year, university.website, major_strengths_str
                ))
                university_id_result = cursor.fetchone()
                university_id = university_id_result[0] if university_id_result else 0
                conn.commit()
                return university_id
        except Exception as e:
            conn.rollback()
            logger.error(f"插入大学失败: {e}")
            raise
    
    # =====================================================
    # 录取分数操作
    # =====================================================
    
    def get_admission_scores(
        self,
        university_id: Optional[int] = None,
        major_id: Optional[int] = None,
        province: Optional[str] = None,
        year: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> AdmissionScoreListResponse:
        """获取录取分数列表"""
        conn = self._get_connection()
        try:
            offset = (page - 1) * page_size
            conditions = []
            params = []
            
            if university_id:
                conditions.append("university_id = %s")
                params.append(university_id)
            if major_id:
                conditions.append("major_id = %s")
                params.append(major_id)
            if province:
                conditions.append("province = %s")
                params.append(province)
            if year:
                conditions.append("year = %s")
                params.append(year)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM university_admission_scores WHERE {where_clause}", tuple(params))
                count_result = cursor.fetchone()
                total = count_result['count'] if count_result else 0

                params.extend([page_size, offset])
                cursor.execute(f"""
                    SELECT * FROM university_admission_scores 
                    WHERE {where_clause} 
                    ORDER BY year DESC, min_score DESC 
                    LIMIT %s OFFSET %s
                """, tuple(params))
                rows = cursor.fetchall()
                
                data = [AdmissionScore(**row) for row in rows]
                return AdmissionScoreListResponse(data=data, total=total, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"获取录取分数失败: {e}")
            raise
    
    def insert_admission_score(self, score: AdmissionScore) -> int:
        """插入录取分数"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO university_admission_scores (
                        university_id, university_name, major_id, major_name, year,
                        min_score, max_score, avg_score, province, batch, enrollment_count
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    score.university_id, score.university_name, score.major_id, score.major_name, score.year,
                    score.min_score, score.max_score, score.avg_score, score.province, score.batch, score.enrollment_count
                ))
                score_id_result = cursor.fetchone()
                score_id = score_id_result[0] if score_id_result else 0
                conn.commit()
                return score_id
        except Exception as e:
            conn.rollback()
            logger.error(f"插入录取分数失败: {e}")
            raise
    
    # =====================================================
    # 行业趋势操作
    # =====================================================
    
    def get_industry_trends(
        self,
        industry_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> IndustryTrendListResponse:
        """获取行业趋势列表"""
        conn = self._get_connection()
        try:
            offset = (page - 1) * page_size
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if industry_name:
                    cursor.execute("""
                        SELECT * FROM industry_trends 
                        WHERE industry_name = %s 
                        ORDER BY publish_time DESC NULLS LAST 
                        LIMIT %s OFFSET %s
                    """, (industry_name, page_size, offset))
                else:
                    cursor.execute("""
                        SELECT * FROM industry_trends 
                        ORDER BY publish_time DESC NULLS LAST 
                        LIMIT %s OFFSET %s
                    """, (page_size, offset))
                rows = cursor.fetchall()
                
                total = len(rows)
                data = []
                for row in rows:
                    if row.get('trend_data') and isinstance(row['trend_data'], str):
                        row['trend_data'] = {}
                    data.append(IndustryTrend(**row))
                
                return IndustryTrendListResponse(data=data, total=total, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"获取行业趋势失败: {e}")
            raise
    
    def insert_industry_trend(self, trend: IndustryTrend) -> int:
        """插入行业趋势"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO industry_trends (
                        industry_name, trend_data, policy_change, salary_change,
                        source, source_url, publish_time, heat_index
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    trend.industry_name, str(trend.trend_data), trend.policy_change, trend.salary_change,
                    trend.source, trend.source_url, trend.publish_time, trend.heat_index
                ))
                result = cursor.fetchone()
                trend_id = result[0] if result else 0
                conn.commit()
                return trend_id
        except Exception as e:
            conn.rollback()
            logger.error(f"插入行业趋势失败: {e}")
            raise
    
    # =====================================================
    # 视频内容操作
    # =====================================================
    
    def get_videos(
        self,
        platform: Optional[str] = None,
        related_major: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> VideoContentListResponse:
        """获取视频内容列表"""
        conn = self._get_connection()
        try:
            offset = (page - 1) * page_size
            conditions = []
            params = []
            
            if platform:
                conditions.append("platform = %s")
                params.append(platform)
            if related_major:
                conditions.append("related_major = %s")
                params.append(related_major)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM video_content WHERE {where_clause}", tuple(params))
                count_result = cursor.fetchone()
                total = count_result['count'] if count_result else 0

                params.extend([page_size, offset])
                cursor.execute(f"""
                    SELECT * FROM video_content 
                    WHERE {where_clause} 
                    ORDER BY view_count DESC 
                    LIMIT %s OFFSET %s
                """, tuple(params))
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    if row.get('keywords') and isinstance(row['keywords'], str):
                        row['keywords'] = row['keywords'].strip('{}').split(',') if row['keywords'] else []
                    data.append(VideoContent(**row))
                
                return VideoContentListResponse(data=data, total=total, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"获取视频内容失败: {e}")
            raise
    
    def insert_video_content(self, video: VideoContent) -> int:
        """插入视频内容"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                keywords_str = None
                if video.keywords:
                    keywords_str = '{' + ','.join(video.keywords) + '}'
                
                cursor.execute("""
                    INSERT INTO video_content (
                        title, description, url, cover_url, duration, view_count,
                        author, publish_time, platform, related_major, keywords, heat_index
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                """, (
                    video.title, video.description, video.url, video.cover_url, video.duration, video.view_count,
                    video.author, video.publish_time, video.platform, video.related_major, keywords_str, video.heat_index
                ))
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else 0
        except Exception as e:
            conn.rollback()
            logger.error(f"插入视频内容失败: {e}")
            raise
    
    # =====================================================
    # 爬取历史操作
    # =====================================================
    
    def get_crawl_history(
        self,
        task_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> CrawlHistoryListResponse:
        """获取爬取历史列表"""
        conn = self._get_connection()
        try:
            offset = (page - 1) * page_size
            conditions = []
            params = []
            
            if task_type:
                conditions.append("task_type = %s")
                params.append(task_type)
            if status:
                conditions.append("status = %s")
                params.append(status)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM crawl_history WHERE {where_clause}", tuple(params))
                count_result = cursor.fetchone()
                total = count_result['count'] if count_result else 0

                params.extend([page_size, offset])
                cursor.execute(f"""
                    SELECT * FROM crawl_history 
                    WHERE {where_clause} 
                    ORDER BY start_time DESC 
                    LIMIT %s OFFSET %s
                """, tuple(params))
                rows = cursor.fetchall()
                
                data = [CrawlHistory(**row) for row in rows]
                return CrawlHistoryListResponse(data=data, total=total, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"获取爬取历史失败: {e}")
            raise
    
    def log_crawl_history(self, history: CrawlHistory) -> int:
        """记录爬取历史"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO crawl_history (
                        task_id, task_type, start_time, end_time, status,
                        crawled_count, success_count, failed_count, error_message
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    history.task_id, history.task_type, history.start_time, history.end_time, history.status,
                    history.crawled_count, history.success_count, history.failed_count, history.error_message
                ))
                history_id_result = cursor.fetchone()
                history_id = history_id_result[0] if history_id_result else 0
                conn.commit()
                return history_id
        except Exception as e:
            conn.rollback()
            logger.error(f"记录爬取历史失败: {e}")
            raise
    
    def update_crawl_history(self, task_id: str, **kwargs) -> bool:
        """更新爬取历史"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
                params = list(kwargs.values())
                params.append(task_id)
                
                cursor.execute(f"""
                    UPDATE crawl_history 
                    SET {set_clause} 
                    WHERE task_id = %s
                """, params)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"更新爬取历史失败: {e}")
            raise
    
    # =====================================================
    # 爬取配额操作
    # =====================================================
    
    def get_crawl_quotas(self) -> CrawlQuotaListResponse:
        """获取爬取配额列表"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM crawl_quota ORDER BY priority DESC")
                rows = cursor.fetchall()
                data = [CrawlQuota(**row) for row in rows]
                return CrawlQuotaListResponse(data=data, total=len(data))
        except Exception as e:
            logger.error(f"获取爬取配额失败: {e}")
            raise
    
    def increment_quota_used(self, category: str, count: int = 1) -> bool:
        """增加配额使用计数"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE crawl_quota 
                    SET used_count = used_count + %s, updated_at = NOW()
                    WHERE category = %s
                """, (count, category))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"更新配额使用计数失败: {e}")
            raise
    
    def reset_quota_used(self, category: Optional[str] = None) -> int:
        """重置配额使用计数"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                if category:
                    cursor.execute("""
                        UPDATE crawl_quota 
                        SET used_count = 0, last_reset_time = NOW()
                        WHERE category = %s
                    """, (category,))
                else:
                    cursor.execute("""
                        UPDATE crawl_quota 
                        SET used_count = 0, last_reset_time = NOW()
                    """)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"重置配额使用计数失败: {e}")
            raise
