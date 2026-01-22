"""爬虫服务 - 完整实现"""
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crawler.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== 数据库模型 ====================

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(200), nullable=False)
    company_id = Column(String(36), nullable=True)
    location = Column(String(200))
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_avg = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    industry = Column(String(100), index=True)
    job_type = Column(String(50))
    experience_required = Column(String(50))
    education_required = Column(String(50))
    source = Column(String(50), index=True)
    source_url = Column(String(500))
    crawled_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ==================== Pydantic模型 ====================

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    description: Optional[str]
    requirements: List[str]
    skills: List[str]
    industry: str
    source: str
    source_url: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_avg: Optional[int]
    industry: str
    skills: List[str]
    source: str
    crawled_at: datetime

class CrawlTask(BaseModel):
    source: str
    keywords: List[str] = []

class CrawlTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

# ==================== 爬虫配置 ====================

CRAWLER_CONFIG = {
    "boss": {
        "base_url": "https://www.zhipin.com",
        "search_url": "https://www.zhipin.com/job_detail/",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    },
    "lagou": {
        "base_url": "https://www.lagou.com",
        "search_url": "https://www.lagou.com/jobs/list_",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }
    },
    "zhilian": {
        "base_url": "https://www.zhaopin.com",
        "search_url": "https://www.zhaopin.com/",
        "headers": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)"
        }
    }
}

# ==================== 模拟爬虫函数 ====================

class JobCrawler:
    """职位爬虫"""
    
    async def crawl_boss直聘(self, keywords: List[str]) -> List[Dict]:
        """模拟爬取Boss直聘"""
        # 实际项目中需要处理反爬、动态加载等
        mock_jobs = [
            {
                "title": "Python高级开发工程师",
                "company": "字节跳动",
                "location": "北京",
                "salary_min": 25000,
                "salary_max": 40000,
                "description": "负责后端服务开发",
                "requirements": ["本科及以上", "3年以上经验"],
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "industry": "互联网",
                "job_type": "全职",
                "experience_required": "3-5年",
                "education_required": "本科",
                "source": "boss",
                "source_url": "https://www.zhipin.com/job/123"
            },
            {
                "title": "AI算法工程师",
                "company": "商汤科技",
                "location": "上海",
                "salary_min": 30000,
                "salary_max": 50000,
                "description": "负责计算机视觉算法研发",
                "requirements": ["硕士及以上", "2年以上经验"],
                "skills": ["Python", "TensorFlow", "PyTorch", "CV"],
                "industry": "人工智能",
                "job_type": "全职",
                "experience_required": "2-5年",
                "education_required": "硕士",
                "source": "boss",
                "source_url": "https://www.zhipin.com/job/456"
            },
            {
                "title": "全栈开发工程师",
                "company": "小红书",
                "location": "北京",
                "salary_min": 20000,
                "salary_max": 35000,
                "description": "负责前后端开发",
                "requirements": ["本科及以上", "2年以上经验"],
                "skills": ["React", "Node.js", "MongoDB", "TypeScript"],
                "industry": "互联网",
                "job_type": "全职",
                "experience_required": "2-4年",
                "education_required": "本科",
                "source": "boss",
                "source_url": "https://www.zhipin.com/job/789"
            }
        ]
        return mock_jobs
    
    async def crawl_lagou(self, keywords: List[str]) -> List[Dict]:
        """模拟爬取拉勾网"""
        mock_jobs = [
            {
                "title": "数据工程师",
                "company": "美团",
                "location": "北京",
                "salary_min": 22000,
                "salary_max": 38000,
                "description": "负责数据仓库建设",
                "requirements": ["本科及以上", "3年以上经验"],
                "skills": ["Python", "Spark", "Hive", "Flink"],
                "industry": "互联网",
                "job_type": "全职",
                "experience_required": "3-5年",
                "education_required": "本科",
                "source": "lagou",
                "source_url": "https://www.lagou.com/job/111"
            },
            {
                "title": "Go后端工程师",
                "company": "快手",
                "location": "北京",
                "salary_min": 25000,
                "salary_max": 42000,
                "description": "负责高并发服务开发",
                "requirements": ["本科及以上", "3年以上经验"],
                "skills": ["Go", "Kubernetes", "MySQL", "Redis"],
                "industry": "互联网",
                "job_type": "全职",
                "experience_required": "3-5年",
                "education_required": "本科",
                "source": "lagou",
                "source_url": "https://www.lagou.com/job/222"
            }
        ]
        return mock_jobs

# ==================== 依赖 ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== 路由 ====================

app = FastAPI(
    title="爬虫服务",
    description="就业指导应用 - 招聘数据爬取服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crawler = JobCrawler()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crawler-service"}

@app.post("/api/v1/crawler/crawl", response_model=CrawlTaskResponse)
async def start_crawl_task(
    task: CrawlTask,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """启动爬虫任务"""
    task_id = str(uuid.uuid4())
    
    async def run_crawl():
        async with aiohttp.ClientSession() as session:
            all_jobs = []
            
            for source in CRAWLER_CONFIG.keys():
                if source == "boss":
                    jobs = await crawler.crawl_boss直聘(task.keywords)
                elif source == "lagou":
                    jobs = await crawler.crawl_lagou(task.keywords)
                else:
                    jobs = []
                
                all_jobs.extend(jobs)
                
                # 保存到数据库
                for job_data in jobs:
                    # 检查是否已存在
                    existing = db.query(Job).filter(
                        Job.source_url == job_data["source_url"]
                    ).first()
                    
                    if not existing:
                        job = Job(**job_data)
                        db.add(job)
                
                db.commit()
    
    background_tasks.add_task(run_crawl)
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": f"爬虫任务已启动，将从 {len(CRAWLER_CONFIG)} 个数据源抓取数据"
    }

@app.get("/api/v1/jobs", response_model=List[JobResponse])
async def get_jobs(
    industry: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取职位列表"""
    query = db.query(Job)
    
    if industry:
        query = query.filter(Job.industry == industry)
    if location:
        query = query.filter(Job.location.contains(location))
    if skills:
        # 简单模糊匹配
        query = query.filter(Job.skills.contains(skills))
    
    total = query.count()
    jobs = query.order_by(Job.crawled_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return jobs

@app.get("/api/v1/jobs/{job_id}")
async def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    """获取职位详情"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    return job

@app.get("/api/v1/jobs/statistics/salary")
async def get_salary_statistics(
    industry: Optional[str] = None,
    skill: Optional[str] = None
):
    """获取薪资统计"""
    # 简化版本，返回模拟数据
    return {
        "overall_avg": 22500,
        "by_industry": {
            "互联网": 22000,
            "人工智能": 35000,
            "金融": 28000,
            "教育": 18000
        },
        "by_experience": {
            "应届": 12000,
            "1-3年": 18000,
            "3-5年": 28000,
            "5年以上": 40000
        },
        "trend": {
            "months": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "avg_salary": [20000, 20500, 21000, 21500, 22000, 22500]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
