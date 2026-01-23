"""
爬虫数据模块数据库模型
数据库版本: 1.0.0
日期: 2026-01-23
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# =====================================================
# 枚举类型定义
# =====================================================

class UniversityLevel(str, Enum):
    """大学层次"""
    C985 = "985"
    C211 = "211"
    DOUBLE_FIRST_CLASS = "双一流"
    PROVINCIAL_KEY = "省属重点"
    ORDINARY = "普通"


class UniversityType(str, Enum):
    """大学类型"""
    COMPREHENSIVE = "综合"
    SCIENCE_ENGINEERING = "理工"
    NORMAL = "师范"
    MEDICAL = "医药"
    AGRICULTURE = "农林"
    FINANCE = "财经"
    LAW = "政法"
    LANGUAGE = "语言"
    ART = "艺术"
    SPORTS = "体育"
    ETHNIC = "民族"


class AdmissionBatch(str, Enum):
    """录取批次"""
    FIRST_BATCH = "本科一批"
    SECOND_BATCH = "本科二批"
    ADVANCE_BATCH = "本科提前批"
    SPECIAL_BATCH = "专科批"


class CrawlStatus(str, Enum):
    """爬取任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class CrawlTaskType(str, Enum):
    """爬取任务类型"""
    MAJOR = "major"
    UNIVERSITY = "university"
    VIDEO = "video"
    TREND = "trend"


class VideoPlatform(str, Enum):
    """视频平台"""
    BILIBILI = "B站"
    YOUTUBE = "YouTube"


# =====================================================
# Pydantic 模型定义（用于API请求/响应）
# =====================================================

class MajorCategoryBase(BaseModel):
    """学科分类基础模型"""
    code: Optional[str] = Field(None, description="学科代码")
    name: str = Field(..., description="学科名称")
    parent_id: Optional[int] = Field(None, description="父级ID")
    sort_order: int = Field(0, description="排序")


class MajorCategory(MajorCategoryBase):
    """学科分类完整模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MajorBase(BaseModel):
    """专业基础模型"""
    name: str = Field(..., description="专业名称")
    category_id: int = Field(..., description="学科门类ID")
    category_name: Optional[str] = Field(None, description="学科门类名称")
    description: Optional[str] = Field(None, description="专业描述")
    core_courses: Optional[List[str]] = Field(default_factory=list, description="核心课程")
    employment_rate: Optional[float] = Field(None, ge=0, le=100, description="就业率")
    avg_salary: Optional[str] = Field(None, description="平均薪资")
    heat_index: Optional[float] = Field(None, ge=0, le=100, description="热度指数")


class Major(MajorBase):
    """专业完整模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MajorMarketDataBase(BaseModel):
    """专业行情数据基础模型"""
    title: str = Field(..., description="数据标题")
    major_name: Optional[str] = Field(None, description="专业名称")
    category: Optional[str] = Field(None, description="学科门类")
    source_url: Optional[str] = Field(None, description="来源URL")
    source_website: Optional[str] = Field(None, description="来源网站")
    employment_rate: Optional[float] = Field(None, ge=0, le=100, description="就业率")
    avg_salary: Optional[str] = Field(None, description="平均薪资")
    admission_score: Optional[float] = Field(None, description="录取分数线")
    heat_index: Optional[float] = Field(None, ge=0, le=100, description="热度指数")
    trend_data: Optional[dict] = Field(None, description="趋势数据")
    description: Optional[str] = Field(None, description="详细描述")
    courses: Optional[List[str]] = Field(default_factory=list, description="核心课程")
    career_prospects: Optional[str] = Field(None, description="就业前景")


class MajorMarketData(MajorMarketDataBase):
    """专业行情数据完整模型"""
    id: int
    crawled_at: datetime
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UniversityBase(BaseModel):
    """大学基础模型"""
    name: str = Field(..., description="大学名称")
    level: Optional[UniversityLevel] = Field(None, description="985/211/双一流")
    province: str = Field(..., description="所在省份")
    city: Optional[str] = Field(None, description="所在城市")
    employment_rate: Optional[float] = Field(None, ge=0, le=100, description="就业率")
    type: Optional[UniversityType] = Field(None, description="大学类型")
    location: Optional[str] = Field(None, description="详细地址")
    founded_year: Optional[int] = Field(None, ge=1800, le=2026, description="建校年份")
    website: Optional[str] = Field(None, description="官网地址")
    major_strengths: Optional[List[str]] = Field(default_factory=list, description="王牌专业")


class University(UniversityBase):
    """大学完整模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdmissionScoreBase(BaseModel):
    """录取分数基础模型"""
    university_id: int = Field(..., description="大学ID")
    university_name: Optional[str] = Field(None, description="大学名称")
    major_id: Optional[int] = Field(None, description="专业ID")
    major_name: Optional[str] = Field(None, description="专业名称")
    year: int = Field(..., ge=2000, le=2030, description="年份")
    min_score: float = Field(..., ge=0, le=750, description="最低录取分")
    max_score: Optional[float] = Field(None, ge=0, le=750, description="最高录取分")
    avg_score: Optional[float] = Field(None, ge=0, le=750, description="平均录取分")
    province: str = Field(..., description="招生省份")
    batch: Optional[AdmissionBatch] = Field(None, description="录取批次")
    enrollment_count: Optional[int] = Field(None, ge=0, description="录取人数")


class AdmissionScore(AdmissionScoreBase):
    """录取分数完整模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndustryTrendBase(BaseModel):
    """行业趋势基础模型"""
    industry_name: str = Field(..., description="行业名称")
    trend_data: dict = Field(..., description="趋势数据")
    policy_change: Optional[str] = Field(None, description="政策变化")
    salary_change: Optional[str] = Field(None, description="薪资变化")
    source: Optional[str] = Field(None, description="数据来源")
    source_url: Optional[str] = Field(None, description="原文链接")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    heat_index: Optional[float] = Field(None, ge=0, le=100, description="热度指数")


class IndustryTrend(IndustryTrendBase):
    """行业趋势完整模型"""
    id: int
    crawled_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoContentBase(BaseModel):
    """视频内容基础模型"""
    title: str = Field(..., description="视频标题")
    description: Optional[str] = Field(None, description="视频描述")
    url: str = Field(..., description="视频URL")
    cover_url: Optional[str] = Field(None, description="封面图URL")
    duration: Optional[int] = Field(None, ge=0, description="视频时长（秒）")
    view_count: Optional[int] = Field(default=0, ge=0, description="播放量")
    author: Optional[str] = Field(None, description="作者")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    platform: VideoPlatform = Field(..., description="平台")
    related_major: Optional[str] = Field(None, description="相关专业")
    keywords: Optional[List[str]] = Field(default_factory=list, description="关键词标签")
    heat_index: Optional[float] = Field(None, ge=0, le=100, description="热度指数")


class VideoContent(VideoContentBase):
    """视频内容完整模型"""
    id: int
    crawled_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrawlHistoryBase(BaseModel):
    """爬取历史基础模型"""
    task_id: str = Field(..., description="任务ID")
    task_type: CrawlTaskType = Field(..., description="任务类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    status: CrawlStatus = Field(..., description="状态")
    crawled_count: Optional[int] = Field(default=0, ge=0, description="爬取数量")
    success_count: Optional[int] = Field(default=0, ge=0, description="成功数量")
    failed_count: Optional[int] = Field(default=0, ge=0, description="失败数量")
    error_message: Optional[str] = Field(None, description="错误信息")


class CrawlHistory(CrawlHistoryBase):
    """爬取历史完整模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CrawlQuotaBase(BaseModel):
    """爬取配额基础模型"""
    category: str = Field(..., description="学科类别")
    quota: int = Field(..., ge=0, description="配额数量")
    priority: int = Field(..., ge=0, le=10, description="优先级")
    used_count: Optional[int] = Field(default=0, ge=0, description="已使用数量")
    last_reset_time: Optional[datetime] = Field(None, description="上次重置时间")


class CrawlQuota(CrawlQuotaBase):
    """爬取配额完整模型"""
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# 请求/响应模型
# =====================================================

class MajorListResponse(BaseModel):
    """专业列表响应"""
    data: List[Major]
    total: int
    page: int
    page_size: int


class MajorMarketDataListResponse(BaseModel):
    """专业行情数据列表响应"""
    data: List[MajorMarketData]
    total: int
    page: int
    page_size: int


class UniversityListResponse(BaseModel):
    """大学列表响应"""
    data: List[University]
    total: int
    page: int
    page_size: int


class AdmissionScoreListResponse(BaseModel):
    """录取分数列表响应"""
    data: List[AdmissionScore]
    total: int
    page: int
    page_size: int


class IndustryTrendListResponse(BaseModel):
    """行业趋势列表响应"""
    data: List[IndustryTrend]
    total: int
    page: int
    page_size: int


class VideoContentListResponse(BaseModel):
    """视频内容列表响应"""
    data: List[VideoContent]
    total: int
    page: int
    page_size: int


class CrawlHistoryListResponse(BaseModel):
    """爬取历史列表响应"""
    data: List[CrawlHistory]
    total: int
    page: int
    page_size: int


class CrawlQuotaListResponse(BaseModel):
    """爬取配额列表响应"""
    data: List[CrawlQuota]
    total: int
