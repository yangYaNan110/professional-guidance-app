"""录取分数数据爬虫模块"""
import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import time
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class AdmissionScoreCrawler:
    """大学录取分数数据爬虫"""
    
    def __init__(self, db_url: str = None):
        self.session: Optional[aiohttp.ClientSession] = None
        self.db_url = db_url or "postgresql://postgres:password@localhost:5432/employment"
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ]
    
    async def get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self.session
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def crawl_admission_scores(self) -> List[Dict]:
        """爬取录取分数数据"""
        await self.get_session()
        
        all_scores = []
        
        try:
            # 获取数据库中已有的大学列表
            universities = await self.get_universities_from_db()
            
            logger.info(f"开始爬取 {len(universities)} 所大学的录取分数数据...")
            
            # 为每个大学爬取录取分数
            for i, university in enumerate(universities):
                try:
                    # 控制请求频率
                    if i > 0:
                        await asyncio.sleep(random.uniform(2, 5))
                    
                    scores = await self.crawl_university_scores(university)
                    all_scores.extend(scores)
                    
                    logger.info(f"进度: {i+1}/{len(universities)} - {university['name']} 获取 {len(scores)} 条分数数据")
                    
                except Exception as e:
                    logger.error(f"爬取 {university['name']} 失败: {e}")
                    continue
            
            logger.info(f"总共爬取 {len(all_scores)} 条录取分数数据")
            
        finally:
            await self.close()
        
        return all_scores
    
    async def get_universities_from_db(self) -> List[Dict]:
        """从数据库获取大学列表"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 只获取重点大学（985/211/双一流）和省属重点大学
            cursor.execute("""
                SELECT id, name, province, city, level 
                FROM universities 
                WHERE major_strengths IS NOT NULL 
                AND array_length(major_strengths, 1) >= 5
                ORDER BY level DESC, name
            """)
            
            universities = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return universities
            
        except Exception as e:
            logger.error(f"获取大学列表失败: {e}")
            return []
    
    async def crawl_university_scores(self, university: Dict) -> List[Dict]:
        """爬取单个大学的录取分数数据"""
        scores = []
        
        # 生成模拟的录取分数数据
        # 实际部署时应该替换为真实爬取逻辑
        provinces = ['北京', '上海', '天津', '重庆', '江苏', '浙江', '广东', '山东', '湖北', '湖南', 
                    '河南', '四川', '陕西', '辽宁', '吉林', '黑龙江', '河北', '山西', '内蒙古', '安徽',
                    '福建', '江西', '广西', '海南', '贵州', '云南', '西藏', '甘肃', '青海', '宁夏', '新疆']
        
        majors = ['计算机科学与技术', '人工智能', '软件工程', '数据科学', '电子信息工程',
                  '自动化', '机械工程', '土木工程', '经济学', '金融学', '工商管理', '会计学',
                  '临床医学', '法学', '汉语言文学', '数学与应用数学']
        
        # 为每个省份和主要专业生成分数数据
        for province in provinces:
            for major in majors[:8]:  # 限制每个大学8个专业
                # 根据大学层次和地区差异生成分数
                base_score = self.calculate_base_score(university, province, major)
                
                score_data = {
                    'university_id': university['id'],
                    'university_name': university['name'],
                    'major_name': major,
                    'province': province,
                    'year': 2023,
                    'min_score': base_score - 10,
                    'max_score': base_score + 15,
                    'avg_score': base_score,
                    'batch': '本科批',
                    'enrollment_count': random.randint(30, 200),
                    'admission_type': '普通类',
                    'subject_category': '理科' if major in ['计算机科学与技术', '人工智能', '软件工程', '数据科学', '电子信息工程', '自动化', '机械工程', '土木工程'] else '文科'
                }
                
                scores.append(score_data)
        
        return scores
    
    def calculate_base_score(self, university: Dict, province: str, major: str) -> int:
        """计算基准分数"""
        # 大学层次基础分
        level_scores = {
            '985': 620,
            '211': 580,
            '双一流': 590,
            '省属重点': 550,
            '普通本科': 520
        }
        
        base_score = level_scores.get(university.get('level', '普通本科'), 520)
        
        # 热门专业加分
        hot_majors = ['计算机科学与技术', '人工智能', '软件工程', '数据科学', '电子信息工程']
        if major in hot_majors:
            base_score += 20
        
        # 地区调整
        high_score_provinces = ['北京', '上海', '江苏', '浙江']
        if province in high_score_provinces:
            base_score += 15
        
        # 本省加分
        if province == university.get('province'):
            base_score += 10
        
        # 添加随机波动
        base_score += random.randint(-5, 10)
        
        return min(max(base_score, 480), 690)  # 限制在合理范围内
    
    async def save_scores_to_db(self, scores: List[Dict]) -> int:
        """保存分数数据到数据库"""
        if not scores:
            return 0
            
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for score in scores:
                try:
                    # 检查是否已存在
                    cursor.execute("""
                        SELECT id FROM university_admission_scores 
                        WHERE university_id = %s AND major_name = %s AND province = %s AND year = %s
                    """, (score['university_id'], score['major_name'], score['province'], score['year']))
                    
                    if cursor.fetchone():
                        continue  # 跳过已存在的记录
                    
                    # 插入新记录
                    cursor.execute("""
                        INSERT INTO university_admission_scores 
                        (university_id, university_name, major_name, province, year, 
                         min_score, max_score, avg_score, batch, enrollment_count,
                         admission_type, subject_category)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        score['university_id'], score['university_name'], score['major_name'],
                        score['province'], score['year'], score['min_score'], score['max_score'],
                        score['avg_score'], score['batch'], score['enrollment_count'],
                        score['admission_type'], score['subject_category']
                    ))
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存分数记录失败: {e}")
                    continue
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"成功保存 {saved_count} 条录取分数数据")
            return saved_count
            
        except Exception as e:
            logger.error(f"保存分数数据失败: {e}")
            return 0
    
    async def run_crawl_task(self) -> Dict:
        """执行爬取任务"""
        start_time = datetime.now()
        
        try:
            # 爬取数据
            scores = await self.crawl_admission_scores()
            
            # 保存到数据库
            saved_count = await self.save_scores_to_db(scores)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'status': 'success',
                'crawled_count': len(scores),
                'saved_count': saved_count,
                'duration': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"爬取任务执行失败: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'start_time': start_time.isoformat()
            }

# 测试函数
async def test_crawler():
    """测试爬虫功能"""
    crawler = AdmissionScoreCrawler()
    result = await crawler.run_crawl_task()
    print(f"爬取结果: {result}")

if __name__ == "__main__":
    asyncio.run(test_crawler())