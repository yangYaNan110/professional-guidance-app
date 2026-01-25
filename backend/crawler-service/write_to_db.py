#!/usr/bin/env python3
"""
专业数据写入数据库脚本
"""

import asyncio
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseWriter:
    """数据库写入器"""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'employment',
            'user': 'postgres',
            'password': 'postgres'
        }
    
    def get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(**self.db_config)
    
    def insert_major_categories(self, categories):
        """插入专业分类数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for category in categories:
            try:
                query = """
                INSERT INTO major_categories 
                (name, code, parent_id, level, sort_order, description, source_url, source_website, crawled_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
                """
                
                cursor.execute(query, (
                    category['name'],
                    category['code'],
                    category.get('parent_id'),
                    1,  # 学科门类层级
                    category.get('sort_order', 0),
                    category.get('description', ''),
                    f"https://gaokao.chsi.com.cn/special/{category['code']}",  # 构造source_url
                    category.get('source', '阳光高考'),
                    datetime.now(),
                    datetime.now()
                ))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
                    logger.info(f"插入专业分类: {category['name']}")
                
            except Exception as e:
                logger.error(f"插入专业分类失败 {category['name']}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"成功插入 {inserted_count} 个专业分类")
        return inserted_count
    
    def insert_sample_majors(self):
        """插入示例专业数据"""
        sample_majors = [
            {
                'name': '计算机科学与技术',
                'code': '080901',
                'category_name': '工学',
                'description': '计算机科学与技术专业培养具有扎实的计算机科学基础知识，掌握计算机系统的分析、设计和开发方法的高级专门人才。',
                'training_objective': '培养能在科研、教育、企业、事业、技术和行政管理等部门从事计算机教学、科学研究和应用开发的高级专门人才。',
                'main_courses': ['数据结构', '算法分析与设计', '操作系统', '计算机网络', '数据库原理', '软件工程'],
                'employment_direction': '软件开发、网络安全、人工智能、数据分析、系统架构',
                'study_period': 4,
                'degree_awarded': '工学学士',
                'national_key_major': True,
                'discipline_level': '二级学科',
                'source_url': 'https://gaokao.chsi.com.cn/zyk/zybk/speciality?id=080901',
                'source_website': '阳光高考'
            },
            {
                'name': '电子信息工程',
                'code': '080701',
                'category_name': '工学',
                'description': '电子信息工程专业培养具备电子技术和信息系统的基础知识，能从事各类电子设备和信息系统的研究、设计、制造、应用和开发的高等工程技术人才。',
                'training_objective': '培养掌握信号的获取与处理、电子设备与信息系统等方面的专业知识，受到电子与信息工程实践的基本训练，具备设计、开发、应用和集成电子设备和信息系统的基本能力的高级工程技术人才。',
                'main_courses': ['电路原理', '模拟电子技术', '数字电子技术', '信号与系统', '通信原理', '电磁场理论'],
                'employment_direction': '通信设备制造、电子产品研发、电信运营、国防军工',
                'study_period': 4,
                'degree_awarded': '工学学士',
                'national_key_major': True,
                'discipline_level': '二级学科',
                'source_url': 'https://gaokao.chsi.com.cn/zyk/zybk/speciality?id=080701',
                'source_website': '阳光高考'
            },
            {
                'name': '金融学',
                'code': '020301K',
                'category_name': '经济学',
                'description': '金融学专业培养具备金融学方面的理论知识和业务技能，能在银行、证券、投资、保险及其他经济管理部门和企业从事相关工作的专门人才。',
                'training_objective': '培养能在银行、证券、投资、保险及其他经济管理部门和企业从事相关工作的高级专门人才。',
                'main_courses': ['政治经济学', '西方经济学', '财政学', '国际经济学', '货币银行学', '国际金融'],
                'employment_direction': '银行、证券公司、保险公司、投资基金、金融监管部门',
                'study_period': 4,
                'degree_awarded': '经济学学士',
                'national_key_major': True,
                'discipline_level': '二级学科',
                'source_url': 'https://gaokao.chsi.com.cn/zyk/zybk/speciality?id=020301K',
                'source_website': '阳光高考'
            },
            {
                'name': '临床医学',
                'code': '100201K',
                'category_name': '医学',
                'description': '临床医学专业培养具备基础医学、临床医学的基本理论和医疗预防的基本技能，能在医疗卫生单位、医学科研等部门从事医疗及预防、医学科研等方面工作的医学高级专门人才。',
                'training_objective': '培养具备基础医学、临床医学的基本理论和医疗预防的基本技能，能在医疗卫生单位、医学科研等部门从事医疗及预防、医学科研等方面工作的医学高级专门人才。',
                'main_courses': ['人体解剖学', '生理学', '病理学', '内科学', '外科学', '妇产科学'],
                'employment_direction': '各级医院、社区卫生服务中心、医学院校、医学科研机构',
                'study_period': 5,
                'degree_awarded': '医学学士',
                'national_key_major': True,
                'discipline_level': '二级学科',
                'source_url': 'https://gaokao.chsi.com.cn/zyk/zybk/speciality?id=100201K',
                'source_website': '阳光高考'
            },
            {
                'name': '法学',
                'code': '030101K',
                'category_name': '法学',
                'description': '法学专业培养系统掌握法学知识，熟悉我国法律和党的相关政策，能在国家机关、企事业单位和社会团体，特别是能在立法机关、行政机关、检察机关、审判机关、仲裁机构和法律服务机构从事法律工作的高级专门人才。',
                'training_objective': '培养系统掌握法学知识，熟悉我国法律和党的相关政策，能在国家机关、企事业单位和社会团体从事法律工作的高级专门人才。',
                'main_courses': ['法理学', '宪法学', '民法学', '刑法学', '行政法学', '经济法学'],
                'employment_direction': '法院、检察院、律师事务所、政府机关、企业法务',
                'study_period': 4,
                'degree_awarded': '法学学士',
                'national_key_major': True,
                'discipline_level': '一级学科',
                'source_url': 'https://gaokao.chsi.com.cn/zyk/zybk/speciality?id=030101K',
                'source_website': '阳光高考'
            }
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for major in sample_majors:
            try:
                # 先获取category_id
                cursor.execute(
                    "SELECT id FROM major_categories WHERE name = %s",
                    (major['category_name'],)
                )
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"未找到分类: {major['category_name']}")
                    continue
                
                category_id = result[0]
                
                query = """
                INSERT INTO majors 
                (name, code, category_id, description, training_objective, main_courses, 
                 employment_direction, study_period, degree_awarded, national_key_major, 
                 discipline_level, source_url, source_website, crawled_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
                """
                
                cursor.execute(query, (
                    major['name'],
                    major['code'],
                    category_id,
                    major['description'],
                    major['training_objective'],
                    major['main_courses'],
                    major['employment_direction'],
                    major['study_period'],
                    major['degree_awarded'],
                    major['national_key_major'],
                    major['discipline_level'],
                    major['source_url'],
                    major['source_website'],
                    datetime.now(),
                    datetime.now()
                ))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
                    logger.info(f"插入专业: {major['name']}")
                
            except Exception as e:
                logger.error(f"插入专业失败 {major['name']}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"成功插入 {inserted_count} 个专业")
        return inserted_count

async def main():
    """主函数"""
    try:
        writer = DatabaseWriter()
        
        # 获取爬取的分类数据
        from src.services.major_basic_crawler import MajorBasicCrawler
        
        config = {
            "data_sources": {
                "阳光高考": {
                    "base_url": "https://gaokao.chsi.com.cn",
                    "delay": 3,
                    "enabled": True
                }
            }
        }
        
        crawler = MajorBasicCrawler(config)
        categories = await crawler.crawl_major_categories()
        await crawler.cleanup()
        
        # 插入分类数据
        logger.info("开始插入专业分类数据...")
        categories_count = writer.insert_major_categories(categories)
        
        # 插入示例专业数据
        logger.info("开始插入示例专业数据...")
        majors_count = writer.insert_sample_majors()
        
        logger.info(f"数据插入完成: {categories_count} 个分类, {majors_count} 个专业")
        
    except Exception as e:
        logger.error(f"数据写入失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())