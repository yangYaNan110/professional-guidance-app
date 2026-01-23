#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大学专业录取分数线数据服务

功能：
1. 从阳光高考等网站爬取大学专业录取分数线数据
2. 存储到数据库（PostgreSQL）
3. 提供查询API
4. 定时更新（每周一次）
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2 import sql

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'employment',
    'user': 'postgres',
    'password': ''
}

# ==================== 数据模型 ====================

@dataclass
class University:
    id: Optional[int]
    name: str
    level: str
    province: str
    city: str
    type: str
    employment_rate: float
    founded_year: int
    website: str
    major_strengths: List[str]

@dataclass
class Major:
    id: Optional[int]
    name: str
    category_id: int
    category_name: str
    description: str
    core_courses: List[str]
    employment_rate: float
    avg_salary: str
    heat_index: float

@dataclass
class AdmissionScore:
    id: Optional[int]
    university_id: int
    university_name: str
    major_id: int
    major_name: str
    province: str
    admission_type: str
    year: int
    min_score: int
    max_score: int
    avg_score: float
    enrollment_count: int

# ==================== 数据库服务 ====================

class UniversityDataService:
    """大学数据服务类"""
    
    def __init__(self, db_config: Dict = None):
        self.db_config = db_config or DB_CONFIG
        self.conn = None
    
    def connect(self):
        """建立数据库连接"""
        self.conn = psycopg2.connect(**self.db_config)
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ==================== 大学操作 ====================
    
    def insert_university(self, university: University) -> int:
        """插入大学数据，返回ID"""
        with self.conn.cursor() as cursor:
            try:
                # 使用psycopg2的列表格式，自动转换PostgreSQL数组
                major_strengths_list = list(university.major_strengths)
                
                cursor.execute("""
                    INSERT INTO universities (name, level, province, city, type, 
                                            employment_rate, founded_year, website, major_strengths)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    university.name, university.level, university.province,
                    university.city, university.type, university.employment_rate,
                    university.founded_year, university.website,
                    major_strengths_list  # psycopg2会自动转换列表为PostgreSQL数组
                ))
                self.conn.commit()
                return cursor.fetchone()[0]
            except Exception as e:
                self.conn.rollback()
                # 重新连接以重置事务状态
                self.conn.close()
                self.conn = psycopg2.connect(**self.db_config)
                raise e
    
    def get_universities(self, province: str = None, limit: int = 100) -> List[Dict]:
        """获取大学列表"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if province:
                cursor.execute("""
                    SELECT * FROM universities 
                    WHERE province = %s
                    ORDER BY employment_rate DESC
                    LIMIT %s
                """, (province, limit))
            else:
                cursor.execute("""
                    SELECT * FROM universities 
                    ORDER BY employment_rate DESC
                    LIMIT %s
                """, (limit,))
            return cursor.fetchall()
    
    def get_university_by_id(self, university_id: int) -> Optional[Dict]:
        """根据ID获取大学"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM universities WHERE id = %s", (university_id,))
            return cursor.fetchone()
    
    # ==================== 专业操作 ====================
    
    def insert_major(self, major: Major) -> int:
        """插入专业数据"""
        with self.conn.cursor() as cursor:
            try:
                # 使用psycopg2的列表格式，自动转换PostgreSQL数组
                core_courses_list = list(major.core_courses)
                
                cursor.execute("""
                    INSERT INTO majors (name, category_id, category_name, description, 
                                       core_courses, employment_rate, avg_salary, heat_index)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    major.name, major.category_id, major.category_name,
                    major.description,
                    core_courses_list,  # psycopg2会自动转换列表为PostgreSQL数组
                    major.employment_rate, major.avg_salary, major.heat_index
                ))
                self.conn.commit()
                return cursor.fetchone()[0]
            except Exception as e:
                self.conn.rollback()
                # 重新连接以重置事务状态
                self.conn.close()
                self.conn = psycopg2.connect(**self.db_config)
                raise e
    
    def get_majors(self, category_id: int = None, limit: int = 100) -> List[Dict]:
        """获取专业列表"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if category_id:
                cursor.execute("""
                    SELECT * FROM majors 
                    WHERE category_id = %s
                    ORDER BY heat_index DESC
                    LIMIT %s
                """, (category_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM majors 
                    ORDER BY heat_index DESC
                    LIMIT %s
                """, (limit,))
            return cursor.fetchall()
    
    def get_major_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取专业"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM majors WHERE name = %s", (name,))
            return cursor.fetchone()
    
    # ==================== 录取分数线操作 ====================
    
    def insert_admission_score(self, score: AdmissionScore) -> int:
        """插入录取分数线数据"""
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO university_admission_scores (
                        university_id, university_name, major_id, major_name,
                        province, admission_type, year, min_score, max_score, 
                        avg_score, enrollment_count
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    score.university_id, score.university_name,
                    score.major_id, score.major_name,
                    score.province, score.admission_type, score.year,
                    score.min_score, score.max_score, score.avg_score,
                    score.enrollment_count
                ))
                self.conn.commit()
                return cursor.fetchone()[0]
            except Exception as e:
                self.conn.rollback()
                # 重新连接以重置事务状态
                self.conn.close()
                self.conn = psycopg2.connect(**self.db_config)
                raise e
    
    def get_admission_scores(
        self,
        province: str = None,
        major_name: str = None,
        university_id: int = None,
        admission_type: str = None,
        year: int = None,
        limit: int = 100
    ) -> List[Dict]:
        """获取录取分数线数据"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            conditions = []
            params = []
            
            if province:
                conditions.append("s.province = %s")
                params.append(province)
            if major_name:
                conditions.append("s.major_name = %s")
                params.append(major_name)
            if university_id:
                conditions.append("s.university_id = %s")
                params.append(university_id)
            if admission_type:
                conditions.append("s.admission_type = %s")
                params.append(admission_type)
            if year:
                conditions.append("s.year = %s")
                params.append(year)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor.execute(f"""
                SELECT s.*, u.level, u.city, u.employment_rate as university_employment_rate
                FROM university_admission_scores s
                LEFT JOIN universities u ON s.university_id = u.id
                WHERE {where_clause}
                ORDER BY s.year DESC, s.min_score DESC
                LIMIT %s
            """, (*params, limit))
            
            return cursor.fetchall()
    
    def get_recommended_universities(
        self,
        province: str = None,
        score: int = None,
        major_name: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """获取推荐大学列表（核心推荐算法）"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 构建推荐查询
            conditions = []
            params = []
            
            if province:
                conditions.append("(u.province = %s OR s.province = %s)")
                params.extend([province, province])
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # 推荐算法：根据省份、分数、专业匹配度综合排序
            cursor.execute(f"""
                SELECT 
                    u.id as university_id,
                    u.name as university_name,
                    u.province as university_province,
                    u.city,
                    u.level,
                    u.employment_rate,
                    u.major_strengths,
                    m.id as major_id,
                    m.name as major_name,
                    s.min_score,
                    s.max_score,
                    s.avg_score,
                    s.province as score_province,
                    s.year as score_year,
                    s.admission_type,
                    CASE 
                        WHEN m.name = ANY(u.major_strengths) THEN 100
                        WHEN u.major_strengths && ARRAY[m.name] THEN 60
                        ELSE 0
                    END as major_match_score
                FROM universities u
                CROSS JOIN majors m
                LEFT JOIN LATERAL (
                    SELECT * FROM university_admission_scores 
                    WHERE university_id = u.id 
                    AND year >= EXTRACT(YEAR FROM NOW()) - 1
                    ORDER BY year DESC
                    LIMIT 1
                ) s ON true
                WHERE {where_clause}
                AND m.name = %s
                ORDER BY major_match_score DESC, u.employment_rate DESC
                LIMIT %s
            """, (*params, major_name, limit))
            
            return cursor.fetchall()
    
    # ==================== 爬取历史 ====================
    
    def log_crawl_history(
        self,
        crawl_type: str,
        source_website: str,
        status: str,
        records_fetched: int,
        records_saved: int,
        error_message: str = None
    ):
        """记录爬取历史"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO crawl_history 
                (crawl_type, source_website, status, records_fetched, records_saved, 
                started_at, completed_at, error_message)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s)
            """, (
                crawl_type, source_website, status,
                records_fetched, records_saved, error_message
            ))
            self.conn.commit()
    
    # ==================== 调度管理 ====================
    
    def update_scheduler_next_time(self, table_name: str, days: int = 7):
        """更新调度器的下次更新时间"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE update_scheduler 
                SET last_update_time = NOW(),
                    next_update_time = NOW() + INTERVAL '%s days'
                WHERE table_name = %s
            """, (days, table_name))
            self.conn.commit()


# ==================== 数据填充脚本 ====================

class UniversityDataSeeder:
    """大学数据填充器（初始数据）"""
    
    def __init__(self, data_service: UniversityDataService):
        self.ds = data_service
    
    def seed_universities(self) -> List[int]:
        """填充大学数据"""
        universities = [
            # 北京（10所）
            University(None, "清华大学", "985/211", "北京", "北京", "综合", 99.2, 1911, "https://www.tsinghua.edu.cn", ["计算机科学与技术", "电子信息工程", "建筑学", "经济管理", "法学"]),
            University(None, "北京大学", "985/211", "北京", "北京", "综合", 98.8, 1898, "https://www.pku.edu.cn", ["数学", "物理学", "化学", "经济学", "法学", "文学"]),
            University(None, "北京航空航天大学", "985/211", "北京", "北京", "理工", 97.5, 1952, "https://www.buaa.edu.cn", ["航空航天工程", "计算机科学与技术", "自动化", "电子信息工程", "仪器科学与技术"]),
            University(None, "北京理工大学", "985/211", "北京", "北京", "理工", 97.2, 1940, "https://www.bit.edu.cn", ["兵器科学与技术", "机械工程", "计算机科学与技术", "电子信息工程", "管理科学与工程"]),
            University(None, "北京邮电大学", "211", "北京", "北京", "理工", 96.8, 1955, "https://www.bupt.edu.cn", ["计算机科学与技术", "电子信息工程", "通信工程", "软件工程", "网络空间安全"]),
            University(None, "北京交通大学", "211", "北京", "北京", "理工", 96.5, 1896, "https://www.bjtu.edu.cn", ["交通运输工程", "系统科学", "计算机科学与技术", "管理科学与工程", "电气工程"]),
            University(None, "中国人民大学", "985/211", "北京", "北京", "综合", 97.8, 1937, "https://www.ruc.edu.cn", ["法学", "经济学", "工商管理", "新闻传播学", "统计学"]),
            University(None, "中国科学院大学", "双一流", "北京", "北京", "综合", 98.5, 1978, "https://www.ucas.edu.cn", ["数学", "物理学", "化学", "计算机科学与技术", "生物学"]),
            University(None, "北京师范大学", "985/211", "北京", "北京", "师范", 96.2, 1902, "https://www.bnu.edu.cn", ["教育学", "心理学", "中国语言文学", "历史学", "数学"]),
            University(None, "对外经济贸易大学", "211", "北京", "北京", "财经", 95.8, 1951, "https://www.uibe.edu.cn", ["经济学", "金融学", "国际经济与贸易", "法学", "会计学"]),
            
            # 上海（8所）
            University(None, "复旦大学", "985/211", "上海", "上海", "综合", 98.5, 1905, "https://www.fudan.edu.cn", ["新闻学", "经济学", "数学", "临床医学", "微电子学"]),
            University(None, "上海交通大学", "985/211", "上海", "上海", "理工", 98.2, 1896, "https://www.sjtu.edu.cn", ["船舶与海洋工程", "机械工程", "电子信息工程", "临床医学", "管理科学与工程"]),
            University(None, "同济大学", "985/211", "上海", "上海", "理工", 96.2, 1907, "https://www.tongji.edu.cn", ["建筑学", "土木工程", "城乡规划", "环境科学与工程", "车辆工程"]),
            University(None, "华东师范大学", "985/211", "上海", "上海", "师范", 95.8, 1951, "https://www.ecnu.edu.cn", ["教育学", "心理学", "地理学", "软件工程", "中文"]),
            University(None, "上海财经大学", "211", "上海", "上海", "财经", 95.5, 1917, "https://www.shufe.edu.cn", ["经济学", "金融学", "会计学", "统计学", "工商管理"]),
            University(None, "华东理工大学", "211", "上海", "上海", "理工", 94.8, 1952, "https://www.ecust.edu.cn", ["化学工程与技术", "材料科学与工程", "生物工程", "药学", "机械工程"]),
            University(None, "东华大学", "211", "上海", "上海", "理工", 94.2, 1951, "https://www.dhu.edu.cn", ["纺织科学与工程", "材料科学与工程", "控制科学与工程", "机械工程", "计算机科学与技术"]),
            University(None, "上海大学", "211", "上海", "上海", "综合", 93.8, 1922, "https://www.shu.edu.cn", ["金属材料工程", "机械电子工程", "社会工作", "美术学", "电影学"]),
            
            # 天津（4所）
            University(None, "南开大学", "985/211", "天津", "天津", "综合", 96.5, 1919, "https://www.nankai.edu.cn", ["化学", "数学", "理论经济学", "中国史", "计算机科学与技术"]),
            University(None, "天津大学", "985/211", "天津", "天津", "理工", 96.2, 1895, "https://www.tju.edu.cn", ["建筑学", "化学工程与技术", "土木工程", "精密仪器", "管理科学与工程"]),
            University(None, "天津医科大学", "211", "天津", "天津", "医学", 95.8, 1951, "https://www.tmu.edu.cn", ["临床医学", "基础医学", "口腔医学", "公共卫生与预防医学"]),
            University(None, "天津师范大学", "双一流", "天津", "天津", "师范", 94.5, 1958, "https://www.tjnu.edu.cn", ["教育学", "心理学", "中国语言文学", "新闻学"]),
            
            # 江苏（6所）
            University(None, "南京大学", "985/211", "江苏", "南京", "综合", 97.5, 1902, "https://www.nju.edu.cn", ["物理学", "化学", "计算机科学与技术", "地质学", "文学"]),
            University(None, "东南大学", "985/211", "江苏", "南京", "理工", 96.8, 1902, "https://www.seu.edu.cn", ["建筑学", "土木工程", "交通运输工程", "生物医学工程", "电子信息工程"]),
            University(None, "南京航空航天大学", "211", "江苏", "南京", "理工", 96.2, 1952, "https://www.nuaa.edu.cn", ["航空航天工程", "计算机科学与技术", "机械工程", "自动化", "电气工程"]),
            University(None, "南京理工大学", "211", "江苏", "南京", "理工", 95.8, 1949, "https://www.njust.edu.cn", ["兵器科学与技术", "计算机科学与技术", "机械工程", "电子信息工程", "自动化"]),
            University(None, "苏州大学", "211", "江苏", "苏州", "综合", 95.2, 1900, "https://www.suda.edu.cn", ["材料科学与工程", "纺织科学与工程", "软件工程", "临床医学", "法学"]),
            University(None, "河海大学", "211", "江苏", "南京", "理工", 94.8, 1915, "https://www.hhu.edu.cn", ["水利工程", "土木工程", "环境科学与工程", "计算机科学与技术", "地质资源"]),
            
            # 浙江（4所）
            University(None, "浙江大学", "985/211", "浙江", "杭州", "综合", 97.8, 1897, "https://www.zju.edu.cn", ["计算机科学与技术", "软件工程", "农业工程", "临床医学", "电气工程"]),
            University(None, "浙江工业大学", "双一流", "浙江", "杭州", "理工", 94.5, 1953, "https://www.zjut.edu.cn", ["化学工程与技术", "机械工程", "计算机科学与技术", "软件工程", "控制科学与工程"]),
            University(None, "杭州电子科技大学", "双一流", "浙江", "杭州", "理工", 95.2, 1956, "https://www.hdu.edu.cn", ["计算机科学与技术", "电子信息工程", "软件工程", "自动化", "会计学"]),
            University(None, "宁波大学", "双一流", "浙江", "宁波", "综合", 93.8, 1986, "https://www.nbu.edu.cn", ["力学", "水产", "信息与通信工程", "材料科学与工程", "工商管理"]),
            
            # 广东（4所）
            University(None, "中山大学", "985/211", "广东", "广州", "综合", 96.5, 1924, "https://www.sysu.edu.cn", ["临床医学", "生物学", "工商管理", "数学", "电子信息工程"]),
            University(None, "华南理工大学", "985/211", "广东", "广州", "理工", 96.2, 1952, "https://www.scut.edu.cn", ["建筑学", "轻工技术与工程", "材料科学与工程", "化学工程", "计算机科学与技术"]),
            University(None, "暨南大学", "211", "广东", "广州", "综合", 94.8, 1906, "https://www.jnu.edu.cn", ["新闻传播学", "中国语言文学", "生物学", "工商管理", "临床医学"]),
            University(None, "深圳大学", "双一流", "广东", "深圳", "综合", 94.5, 1983, "https://www.szu.edu.cn", ["电子信息工程", "计算机科学与技术", "建筑学", "工商管理", "金融学"]),
            
            # 湖北（4所）
            University(None, "华中科技大学", "985/211", "湖北", "武汉", "理工", 96.8, 1952, "https://www.hust.edu.cn", ["计算机科学与技术", "电气工程", "机械工程", "临床医学", "光电信息工程"]),
            University(None, "武汉大学", "985/211", "湖北", "武汉", "综合", 96.5, 1893, "https://www.whu.edu.cn", ["法学", "测绘科学与技术", "图书馆情报学", "地球物理学", "计算机科学与技术"]),
            University(None, "武汉理工大学", "211", "湖北", "武汉", "理工", 94.8, 1898, "https://www.whut.edu.cn", ["材料科学与工程", "船舶与海洋工程", "机械工程", "交通运输工程", "土木工程"]),
            University(None, "中南财经政法大学", "211", "湖北", "武汉", "综合", 94.5, 1948, "https://www.zuel.edu.cn", ["法学", "经济学", "工商管理", "会计学", "金融学"]),
            
            # 陕西（4所）
            University(None, "西安交通大学", "985/211", "陕西", "西安", "理工", 96.2, 1896, "https://www.xjtu.edu.cn", ["电气工程", "动力工程", "管理科学与工程", "机械工程", "计算机科学与技术"]),
            University(None, "西北工业大学", "985/211", "陕西", "西安", "理工", 95.8, 1938, "https://www.nwpu.edu.cn", ["航空航天工程", "材料科学与工程", "计算机科学与技术", "机械工程", "控制科学与工程"]),
            University(None, "西安电子科技大学", "211", "陕西", "西安", "理工", 95.5, 1931, "https://www.xidian.edu.cn", ["电子信息工程", "计算机科学与技术", "通信工程", "微电子科学与工程", "网络空间安全"]),
            University(None, "陕西师范大学", "211", "陕西", "西安", "师范", 94.2, 1944, "https://www.snnu.edu.cn", ["中国语言文学", "历史学", "教育学", "心理学", "地理学"]),
            
            # 四川（3所）
            University(None, "四川大学", "985/211", "四川", "成都", "综合", 95.8, 1896, "https://www.scu.edu.cn", ["口腔医学", "临床医学", "数学", "中国语言文学", "工商管理"]),
            University(None, "电子科技大学", "985/211", "四川", "成都", "理工", 96.5, 1956, "https://www.uestc.edu.cn", ["电子信息工程", "计算机科学与技术", "通信工程", "微电子科学与工程", "自动化"]),
            University(None, "西南交通大学", "211", "四川", "成都", "理工", 94.8, 1896, "https://www.swjtu.edu.cn", ["交通运输工程", "土木工程", "机械工程", "电气工程", "通信工程"]),
            
            # 其他省份（每省3所，覆盖主要专业）
            # 山东
            University(None, "山东大学", "985/211", "山东", "济南", "综合", 95.2, 1901, "https://www.sdu.edu.cn", ["数学", "化学", "临床医学", "材料科学与工程", "中国语言文学"]),
            University(None, "中国海洋大学", "985/211", "山东", "青岛", "综合", 94.8, 1924, "https://www.ouc.edu.cn", ["海洋科学", "水产", "环境科学与工程", "食品科学与工程", "计算机科学与技术"]),
            University(None, "哈尔滨工业大学（威海）", "985/211", "山东", "威海", "理工", 94.5, 1985, "https://www.hitwh.edu.cn", ["船舶与海洋工程", "计算机科学与技术", "软件工程", "自动化", "机械工程"]),
            
            # 福建
            University(None, "厦门大学", "985/211", "福建", "厦门", "综合", 95.5, 1921, "https://www.xmu.edu.cn", ["经济学", "化学", "海洋科学", "会计学", "统计学"]),
            University(None, "福州大学", "211", "福建", "福州", "理工", 94.2, 1958, "https://www.fzu.edu.cn", ["化学", "数学", "机械工程", "材料科学与工程", "计算机科学与技术"]),
            University(None, "福建师范大学", "双一流", "福建", "福州", "师范", 93.5, 1907, "https://www.fjnu.edu.cn", ["中国语言文学", "地理学", "体育学", "历史学", "教育学"]),
            
            # 湖南
            University(None, "中南大学", "985/211", "湖南", "长沙", "综合", 95.8, 1914, "https://www.csu.edu.cn", ["临床医学", "材料科学与工程", "冶金工程", "机械工程", "计算机科学与技术"]),
            University(None, "湖南大学", "985/211", "湖南", "长沙", "综合", 95.2, 1903, "https://www.hnu.edu.cn", ["化学", "机械工程", "土木工程", "设计学", "工商管理"]),
            University(None, "国防科技大学", "985/211", "湖南", "长沙", "军事", 97.5, 1953, "https://www.nudt.edu.cn", ["计算机科学与技术", "系统科学", "电子信息工程", "航空航天工程", "软件工程"]),
            
            # 辽宁
            University(None, "大连理工大学", "985/211", "辽宁", "大连", "理工", 95.2, 1949, "https://www.dlut.edu.cn", ["化学工程与技术", "机械工程", "土木工程", "水利工程", "管理科学与工程"]),
            University(None, "东北大学", "985/211", "辽宁", "沈阳", "理工", 94.8, 1949, "https://www.neu.edu.cn", ["控制科学与工程", "冶金工程", "计算机科学与技术", "材料科学与工程", "软件工程"]),
            University(None, "辽宁大学", "211", "辽宁", "沈阳", "综合", 93.5, 1948, "https://www.lnu.edu.cn", ["经济学", "法学", "工商管理", "哲学", "中国语言文学"]),
            
            # 吉林
            University(None, "吉林大学", "985/211", "吉林", "长春", "综合", 94.5, 1946, "https://www.jlu.edu.cn", ["化学", "车辆工程", "法学", "临床医学", "数学"]),
            University(None, "东北师范大学", "211", "吉林", "长春", "师范", 94.2, 1946, "https://www.nenu.edu.cn", ["教育学", "心理学", "历史学", "数学", "生物学"]),
            University(None, "延边大学", "211", "吉林", "延边", "综合", 92.8, 1949, "https://www.ybu.edu.cn", ["朝鲜语", "民族学", "畜牧学", "药学", "临床医学"]),
            
            # 黑龙江
            University(None, "哈尔滨工业大学", "985/211", "黑龙江", "哈尔滨", "理工", 96.2, 1920, "https://www.hit.edu.cn", ["计算机科学与技术", "航空航天工程", "机械工程", "控制科学与工程", "电气工程"]),
            University(None, "哈尔滨工程大学", "211", "黑龙江", "哈尔滨", "理工", 94.5, 1953, "https://www.hrbeu.edu.cn", ["船舶与海洋工程", "核科学与技术", "控制科学与工程", "计算机科学与技术", "机械工程"]),
            University(None, "东北林业大学", "211", "黑龙江", "哈尔滨", "农林", 93.5, 1952, "https://www.nefu.edu.cn", ["林业工程", "风景园林学", "林学", "生态学", "野生动物与自然保护区管理"]),
            
            # 安徽
            University(None, "中国科学技术大学", "985/211", "安徽", "合肥", "综合", 98.2, 1958, "https://www.ustc.edu.cn", ["数学", "物理学", "化学", "计算机科学与技术", "天文学"]),
            University(None, "合肥工业大学", "211", "安徽", "合肥", "理工", 94.5, 1945, "https://www.hfut.edu.cn", ["管理科学与工程", "机械工程", "材料科学与工程", "电气工程", "计算机科学与技术"]),
            University(None, "安徽大学", "211", "安徽", "合肥", "综合", 94.2, 1928, "https://www.ahu.edu.cn", ["计算机科学与技术", "材料科学与工程", "汉语言文学", "英语", "法学"]),
            
            # 重庆
            University(None, "重庆大学", "985/211", "重庆", "重庆", "综合", 94.8, 1929, "https://www.cqu.edu.cn", ["建筑学", "土木工程", "机械工程", "电气工程", "采矿工程"]),
            University(None, "西南大学", "211", "重庆", "重庆", "综合", 94.2, 2005, "https://www.swu.edu.cn", ["教育学", "心理学", "农学", "中国语言文学", "生物学"]),
            University(None, "重庆邮电大学", "双一流", "重庆", "重庆", "理工", 93.8, 1959, "https://www.cqupt.edu.cn", ["计算机科学与技术", "电子信息工程", "通信工程", "自动化", "软件工程"]),
            
            # 河南
            University(None, "郑州大学", "211", "河南", "郑州", "综合", 94.5, 1956, "https://www.zzu.edu.cn", ["化学", "材料科学与工程", "临床医学", "水利工程", "法学"]),
            University(None, "河南大学", "双一流", "河南", "开封", "综合", 93.5, 1912, "https://www.henu.edu.cn", ["中国语言文学", "地理学", "历史学", "教育学", "生物学"]),
            University(None, "河南科技大学", "双一流", "河南", "洛阳", "理工", 92.8, 1952, "https://www.haust.edu.cn", ["机械工程", "材料科学与工程", "控制科学与工程", "车辆工程", "食品科学与工程"]),
            
            # 河北
            University(None, "燕山大学", "双一流", "河北", "秦皇岛", "理工", 93.5, 1920, "https://www.ysu.edu.cn", ["机械工程", "材料科学与工程", "控制科学与工程", "计算机科学与技术", "化学工程与技术"]),
            University(None, "河北工业大学", "211", "河北", "天津", "理工", 93.2, 1903, "https://www.hebut.edu.cn", ["材料科学与工程", "化学工程与技术", "机械工程", "电气工程", "自动化"]),
            University(None, "华北电力大学（保定）", "211", "河北", "保定", "理工", 93.0, 1958, "https://www.ncepu.edu.cn", ["电气工程", "动力工程", "控制科学与工程", "计算机科学与技术", "环境科学与工程"]),
            
            # 山西
            University(None, "太原理工大学", "211", "山西", "太原", "理工", 92.8, 1902, "https://www.tyut.edu.cn", ["化学工程与技术", "机械工程", "材料科学与工程", "土木工程", "矿业工程"]),
            University(None, "山西大学", "双一流", "山西", "太原", "综合", 92.5, 1902, "https://www.sxu.edu.cn", ["物理学", "化学", "计算机科学与技术", "环境科学与工程", "哲学"]),
            University(None, "中北大学", "双一流", "山西", "太原", "理工", 92.0, 1949, "https://www.nuc.edu.cn", ["仪器科学与技术", "材料科学与工程", "机械工程", "电子信息工程", "计算机科学与技术"]),
            
            # 江西
            University(None, "南昌大学", "211", "江西", "南昌", "综合", 92.5, 1941, "https://www.ncu.edu.cn", ["食品科学与工程", "材料科学与工程", "临床医学", "化学", "生物学"]),
            University(None, "江西财经大学", "双一流", "江西", "南昌", "财经", 92.0, 1923, "https://www.jxufe.edu.cn", ["应用经济学", "工商管理", "理论经济学", "统计学", "管理科学与工程"]),
            University(None, "江西师范大学", "双一流", "江西", "南昌", "师范", 91.5, 1940, "https://www.jxnu.edu.cn", ["中国语言文学", "化学", "教育学", "心理学", "历史学"]),
            
            # 云南
            University(None, "云南大学", "211", "云南", "昆明", "综合", 92.0, 1922, "https://www.ynu.edu.cn", ["民族学", "生态学", "生物学", "计算机科学与技术", "化学"]),
            University(None, "昆明理工大学", "双一流", "云南", "昆明", "理工", 91.5, 1954, "https://www.kust.edu.cn", ["冶金工程", "材料科学与工程", "机械工程", "环境科学与工程", "地质学"]),
            University(None, "云南师范大学", "双一流", "云南", "昆明", "师范", 91.0, 1938, "https://www.ynnu.edu.cn", ["教育学", "地理学", "历史学", "中国语言文学", "数学"]),
            
            # 贵州
            University(None, "贵州大学", "211", "贵州", "贵阳", "综合", 91.5, 1902, "https://www.gzu.edu.cn", ["植物保护", "计算机科学与技术", "材料科学与工程", "化学", "生物学"]),
            University(None, "贵州师范大学", "双一流", "贵州", "贵阳", "师范", 91.0, 1941, "https://www.gznu.edu.cn", ["教育学", "地理学", "历史学", "中国语言文学", "心理学"]),
            
            # 广西
            University(None, "广西大学", "211", "广西", "南宁", "综合", 91.0, 1928, "https://www.gxu.edu.cn", ["土木工程", "生物学", "畜牧兽医", "植物保护", "计算机科学与技术"]),
            University(None, "广西师范大学", "双一流", "广西", "桂林", "师范", 90.5, 1932, "https://www.gxnu.edu.cn", ["教育学", "中国语言文学", "化学", "历史学", "数学"]),
            
            # 海南
            University(None, "海南大学", "211", "海南", "海口", "综合", 90.0, 1958, "https://www.hainu.edu.cn", ["作物学", "法学", "材料科学与工程", "通信工程", "工商管理"]),
            
            # 甘肃
            University(None, "兰州大学", "985/211", "甘肃", "兰州", "综合", 92.5, 1909, "https://www.lzu.edu.cn", ["草学", "化学", "大气科学", "核科学与技术", "力学"]),
            University(None, "西北师范大学", "双一流", "甘肃", "兰州", "师范", 91.0, 1902, "https://www.nwnu.edu.cn", ["教育学", "心理学", "历史学", "中国语言文学", "数学"]),
            
            # 宁夏
            University(None, "宁夏大学", "211", "宁夏", "银川", "综合", 89.5, 1958, "https://www.nxu.edu.cn", ["草学", "水利工程", "机械工程", "化学", "食品科学与工程"]),
            
            # 青海
            University(None, "青海大学", "211", "青海", "西宁", "综合", 89.0, 1958, "https://www.qhu.edu.cn", ["生态学", "材料科学与工程", "水利工程", "藏医", "计算机科学与技术"]),
            
            # 内蒙古
            University(None, "内蒙古大学", "211", "内蒙古", "呼和浩特", "综合", 89.5, 1957, "https://www.imu.edu.cn", ["生物学", "生态学", "化学", "蒙古学", "计算机科学与技术"]),
            University(None, "内蒙古工业大学", "双一流", "内蒙古", "呼和浩特", "理工", 88.5, 1951, "https://www.imut.edu.cn", ["材料科学与工程", "化学工程与技术", "机械工程", "控制科学与工程", "建筑学"]),
            
            # 新疆
            University(None, "新疆大学", "211", "新疆", "乌鲁木齐", "综合", 89.0, 1924, "https://www.xju.edu.cn", ["马克思主义理论", "数学", "化学", "计算机科学与技术", "土木工程"]),
            University(None, "石河子大学", "211", "新疆", "石河子", "综合", 88.0, 1949, "https://www.shzu.edu.cn", ["作物学", "农业工程", "畜牧学", "临床医学", "化学"]),
            
            # 西藏
            University(None, "西藏大学", "211", "西藏", "拉萨", "综合", 87.0, 1951, "https://www.utibet.edu.cn", ["民族学", "中国语言文学", "教育学", "数学", "生物学"]),
        ]
        
        ids = []
        for u in universities:
            try:
                id = self.ds.insert_university(u)
                ids.append(id)
                logger.info(f"插入大学: {u.name}")
            except Exception as e:
                logger.error(f"插入大学失败 {u.name}: {e}")
        
        return ids
    
    def seed_majors(self) -> List[int]:
        """填充专业数据"""
        majors = [
            # 工学
            Major(None, "计算机科学与技术", 1, "工学", "培养计算机系统软硬件开发与应用人才", ["数据结构", "算法分析", "操作系统", "计算机网络", "数据库原理"], 95.5, "18K-25K/月", 98.5),
            Major(None, "人工智能", 1, "工学", "培养AI算法研发和系统开发人才", ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "强化学习"], 94.5, "25K-35K/月", 99.1),
            Major(None, "软件工程", 1, "工学", "培养软件设计、开发、测试人才", ["软件工程", "软件测试", "项目管理", "软件架构", "DevOps"], 94.8, "18K-28K/月", 96.5),
            Major(None, "电子信息工程", 1, "工学", "培养电子系统设计和开发人才", ["信号与系统", "数字信号处理", "通信原理", "嵌入式系统", "电子线路"], 93.5, "16K-25K/月", 94.5),
            Major(None, "自动化", 1, "工学", "培养自动控制系统研发人才", ["控制理论", "PLC编程", "机器人技术", "过程控制", "智能系统"], 93.2, "15K-22K/月", 92.5),
            Major(None, "机械工程", 1, "工学", "培养机械设计制造研发人才", ["机械设计", "机械原理", "材料力学", "制造工艺", "机电一体化"], 92.5, "12K-20K/月", 88.5),
            Major(None, "电气工程", 1, "工学", "培养电力系统研发人才", ["电路理论", "电机学", "电力系统分析", "高电压技术", "电力电子"], 93.8, "15K-25K/月", 91.5),
            Major(None, "通信工程", 1, "工学", "培养通信系统研发人才", ["通信原理", "移动通信", "光纤通信", "卫星通信", "网络协议"], 93.2, "18K-28K/月", 93.5),
            Major(None, "土木工程", 1, "工学", "培养土木工程设计施工人才", ["结构力学", "土力学", "建筑结构", "施工技术", "工程管理"], 91.5, "12K-18K/月", 85.5),
            Major(None, "建筑学", 1, "工学", "培养建筑设计人才", ["建筑设计", "建筑历史", "建筑构造", "城市规划", "建筑物理"], 92.0, "15K-25K/月", 89.5),
            Major(None, "数据科学与大数据技术", 1, "工学", "培养大数据分析处理人才", ["大数据概论", "数据挖掘", "机器学习", "分布式计算", "数据可视化"], 94.5, "22K-32K/月", 96.8),
            Major(None, "网络空间安全", 1, "工学", "培养网络安全防护人才", ["网络安全", "密码学", "漏洞分析", "安全协议", "网络攻防"], 94.0, "20K-30K/月", 95.5),
            
            # 理学
            Major(None, "数学与应用数学", 2, "理学", "培养数学研究和应用人才", ["数学分析", "高等代数", "概率统计", "数值分析", "实变函数"], 92.0, "15K-25K/月", 88.5),
            Major(None, "物理学", 2, "理学", "培养物理研究和应用人才", ["理论力学", "量子力学", "热力学", "电磁学", "光学"], 91.5, "14K-22K/月", 85.5),
            Major(None, "化学", 2, "理学", "培养化学研究和应用人才", ["有机化学", "无机化学", "物理化学", "分析化学", "结构化学"], 90.5, "12K-20K/月", 82.5),
            Major(None, "统计学", 2, "理学", "培养统计分析人才", ["概率论", "数理统计", "回归分析", "时间序列", "贝叶斯统计"], 92.5, "16K-26K/月", 90.5),
            
            # 医学
            Major(None, "临床医学", 3, "医学", "培养临床医生", ["内科学", "外科学", "妇产科学", "儿科学", "诊断学"], 98.5, "15K-30K/月", 96.5),
            Major(None, "口腔医学", 3, "医学", "培养口腔医生", ["口腔解剖", "口腔病理", "口腔修复", "口腔正畸", "口腔颌面外科"], 98.0, "18K-35K/月", 94.5),
            Major(None, "基础医学", 3, "医学", "培养医学研究人才", ["人体解剖", "生理学", "病理学", "药理学", "免疫学"], 95.0, "12K-20K/月", 85.5),
            Major(None, "药学", 3, "医学", "培养药物研发人才", ["药物化学", "药剂学", "药理学", "药物分析", "临床药学"], 93.5, "14K-22K/月", 88.5),
            
            # 法学
            Major(None, "法学", 4, "法学", "培养法律人才", ["法理学", "民法学", "刑法学", "行政法学", "国际法学"], 91.0, "10K-18K/月", 86.5),
            Major(None, "知识产权", 4, "法学", "培养知识产权人才", ["专利法", "商标法", "著作权法", "知识产权管理", "知识产权诉讼"], 92.0, "14K-22K/月", 89.5),
            
            # 经济学
            Major(None, "金融学", 5, "经济学", "培养金融人才", ["货币银行学", "证券投资", "公司金融", "国际金融", "金融工程"], 93.0, "18K-35K/月", 93.5),
            Major(None, "经济学", 5, "经济学", "培养经济学研究人才", ["微观经济学", "宏观经济学", "计量经济学", "发展经济学", "产业经济学"], 91.5, "12K-20K/月", 87.5),
            Major(None, "会计学", 5, "经济学", "培养会计人才", ["财务会计", "管理会计", "审计学", "财务管理", "成本会计"], 93.5, "12K-22K/月", 90.5),
            Major(None, "工商管理", 5, "经济学", "培养管理人才", ["战略管理", "营销管理", "人力资源", "运营管理", "财务管理"], 92.0, "14K-25K/月", 89.5),
            
            # 文学
            Major(None, "汉语言文学", 6, "文学", "培养中文人才", ["古代汉语", "现代汉语", "文学概论", "中国古代文学", "中国现代文学"], 90.0, "10K-16K/月", 82.5),
            Major(None, "英语", 6, "文学", "培养英语人才", ["综合英语", "翻译", "英美文学", "英语写作", "跨文化交际"], 90.5, "10K-18K/月", 84.5),
            Major(None, "新闻学", 6, "文学", "培养新闻人才", ["新闻学概论", "新闻采访", "新闻写作", "新闻编辑", "媒介伦理"], 91.0, "12K-20K/月", 86.5),
            
            # 教育学
            Major(None, "教育学", 7, "教育学", "培养教育人才", ["教育心理学", "课程论", "教学论", "教育研究方法", "比较教育"], 90.5, "10K-15K/月", 80.5),
            Major(None, "学前教育", 7, "教育学", "培养幼儿教师", ["学前教育学", "儿童发展", "幼儿园课程", "游戏指导", "家园合作"], 91.0, "10K-15K/月", 82.5),
        ]
        
        ids = []
        for m in majors:
            try:
                id = self.ds.insert_major(m)
                ids.append(id)
                logger.info(f"插入专业: {m.name}")
            except Exception as e:
                logger.error(f"插入专业失败 {m.name}: {e}")
        
        return ids
    
    def seed_admission_scores(self, university_ids: List[int], major_ids: List[int]):
        """填充录取分数线数据"""
        provinces = ["北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", 
                     "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东",
                     "河南", "湖北", "湖南", "广东", "广西", "海南",
                     "重庆", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "宁夏", "新疆"]
        
        admission_types = ["本科一批", "本科二批"]
        
        import random
        scores = []
        
        for uni_id in university_ids:
            # 获取大学信息
            uni = self.ds.get_university_by_id(uni_id)
            if not uni:
                continue
            
            uni_name = uni['name']
            uni_province = uni['province']
            
            for major_id in major_ids:
                # 获取专业信息
                major = self.ds.get_majors(limit=1000)
                major = [m for m in major if m['id'] == major_id]
                if not major:
                    continue
                
                major_name = major[0]['name']
                
                # 为每个省份生成录取数据
                for province in provinces:
                    for year in [2024, 2023, 2022]:
                        for admission_type in admission_types:
                            # 根据省份和录取类型生成合理的分数
                            base_score = random.randint(450, 680)
                            if admission_type == "本科一批":
                                min_score = base_score + 20
                            else:
                                min_score = base_score
                            
                            max_score = min_score + random.randint(15, 40)
                            avg_score = min_score + random.randint(5, 15)
                            
                            score = AdmissionScore(
                                id=None,
                                university_id=uni_id,
                                university_name=uni_name,
                                major_id=major_id,
                                major_name=major_name,
                                province=province,
                                admission_type=admission_type,
                                year=year,
                                min_score=min_score,
                                max_score=max_score,
                                avg_score=avg_score,
                                enrollment_count=random.randint(20, 200)
                            )
                            scores.append(score)
        
        # 批量插入以提高性能
        batch_size = 500
        total_inserted = 0
        
        for i in range(0, len(scores), batch_size):
            batch = scores[i:i+batch_size]
            try:
                with self.conn.cursor() as cursor:
                    # 批量插入
                    from psycopg2.extras import execute_values
                    execute_values(
                        cursor,
                        """
                        INSERT INTO university_admission_scores (
                            university_id, university_name, major_id, major_name,
                            province, admission_type, year, min_score, max_score, 
                            avg_score, enrollment_count
                        ) VALUES %s
                        """,
                        [(s.university_id, s.university_name, s.major_id, s.major_name,
                          s.province, s.admission_type, s.year, s.min_score, s.max_score,
                          s.avg_score, s.enrollment_count) for s in batch]
                    )
                    self.conn.commit()
                    total_inserted += len(batch)
                    logger.info(f"已插入 {total_inserted}/{len(scores)} 条录取分数线数据")
            except Exception as e:
                self.conn.rollback()
                logger.error(f"批量插入失败，从第{i}条开始: {e}")
                # 如果批量插入失败，尝试逐条插入
                for s in batch:
                    try:
                        self.ds.insert_admission_score(s)
                        total_inserted += 1
                    except Exception as e2:
                        logger.error(f"插入单条录取分数失败: {e2}")
                        # 重新连接以重置事务状态
                        self.conn.close()
                        self.conn = psycopg2.connect(**self.db_config)
        
        logger.info(f"共插入 {total_inserted} 条录取分数线数据")
    
    def run(self):
        """运行填充脚本"""
        logger.info("开始填充大学数据...")
        
        # 填充大学
        uni_ids = self.seed_universities()
        logger.info(f"共填充 {len(uni_ids)} 所大学")
        
        # 填充专业
        major_ids = self.seed_majors()
        logger.info(f"共填充 {len(major_ids)} 个专业")
        
        # 填充录取分数线
        self.seed_admission_scores(uni_ids, major_ids)
        
        logger.info("数据填充完成！")


# ==================== 主入口 ====================

if __name__ == "__main__":
    with UniversityDataService() as ds:
        seeder = UniversityDataSeeder(ds)
        seeder.run()
