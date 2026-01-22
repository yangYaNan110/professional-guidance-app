"""共享数据类型定义"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 用户相关
class UserBase(BaseModel):
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    education: Optional[str] = None
    major: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 0
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    preferred_locations: List[str] = []
    preferred_industries: List[str] = []
    career_goals: Optional[str] = None

# 对话相关
class Message(BaseModel):
    id: str
    role: str
    content: str
    audio_url: Optional[str] = None
    emotion: Optional[str] = None
    created_at: datetime

class Conversation(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    reply: Message
    suggestions: List[str] = []

# 职位相关
class JobBase(BaseModel):
    title: str
    company: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    industry: str
    skills: List[str] = []

class JobResponse(JobBase):
    id: str
    salary_avg: Optional[int] = None
    source: str
    crawled_at: datetime

    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    user_id: str
    limit: int = 10

class RecommendationResponse(BaseModel):
    job: JobResponse
    score: float
    reason: str

# 分析相关
class SalaryTrend(BaseModel):
    months: List[str]
    data: List[float]

class IndustryComparison(BaseModel):
    industries: List[str]
    salaries: List[int]

class AnalyticsResponse(BaseModel):
    salary_trend: SalaryTrend
    industry_comparison: IndustryComparison
    skill_demand: dict

# 通用响应
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
