"""分析服务主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import uvicorn

app = FastAPI(
    title="分析服务",
    description="就业指导应用 - 数据分析服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics-service"}

@app.get("/api/v1/analytics/salary-trend")
async def get_salary_trend(industry: str = None):
    """获取薪资趋势数据"""
    return {
        "trend": {
            "labels": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06"],
            "data": [15000, 15500, 15800, 16000, 16200, 16500]
        }
    }

@app.get("/api/v1/analytics/industry-comparison")
async def get_industry_comparison():
    """获取行业薪资对比"""
    return {
        "comparison": {
            "labels": ["互联网", "金融", "教育", "医疗", "制造"],
            "data": [18000, 22000, 15000, 17000, 14000]
        }
    }

@app.get("/api/v1/analytics/skill-demand")
async def get_skill_demand():
    """获取技能需求分布"""
    return {
        "demand": {
            "labels": ["Python", "JavaScript", "Java", "Go", "Rust"],
            "data": [85, 80, 75, 60, 45]
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
