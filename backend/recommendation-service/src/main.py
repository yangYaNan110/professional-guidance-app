"""推荐服务主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="推荐服务",
    description="就业指导应用 - 岗位推荐服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    salary_min: int
    salary_max: int
    skills: List[str]
    industry: str

class RecommendationRequest(BaseModel):
    user_id: str
    limit: int = 10

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "recommendation-service"}

@app.post("/api/v1/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """获取岗位推荐"""
    return {
        "recommendations": [
            {
                "job": {
                    "id": "job_1",
                    "title": "高级Python开发工程师",
                    "company": "某科技公司",
                    "location": "北京",
                    "salary_min": 20000,
                    "salary_max": 35000,
                    "skills": ["Python", "FastAPI", "PostgreSQL"],
                    "industry": "互联网"
                },
                "score": 0.95,
                "reason": "与您的技能和工作经验高度匹配"
            }
        ],
        "total": 1
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
