#!/usr/bin/env python3
"""
专业详情API服务 - 支持四个分组内容
根据用户需求，专业详情需要包含：
1. 专业概念介绍（起源、发展历史、重大事件、现状与未来前景）
2. 核心课程（真实数据）
3. 就业前景（仅就业方向）
4. 注意事项（学习要求、就业要求、薪资与工作强度、职业稳定性、发展空间、发展建议）
"""

import psycopg2
import os
from typing import Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 数据库连接配置
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'employment'),
        user='postgres',
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )

# 创建FastAPI应用
app = FastAPI(
    title="专业详情API v2.0",
    description="支持四个分组的完整专业信息展示",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MajorDetailService:
    def __init__(self):
        self.connection = get_db_connection()
    
    def get_major_concept_data(self, major_name: str) -> Dict[str, Any]:
        """获取专业概念数据"""
        concepts = {
            "origin": [],
            "development_history": [],
            "major_events": [],
            "current_status": [],
            "future_prospects": []
        }
        
        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT concept_type, title, content, year
                FROM major_concepts 
                WHERE major_name = %s
                ORDER BY concept_type, sort_order, year
                """
                cursor.execute(query, (major_name,))
                results = cursor.fetchall()
                
                for concept_type, title, content, year in results:
                    if concept_type in concepts:
                        concepts[concept_type].append({
                            "title": title,
                            "content": content,
                            "year": year
                        })
                
        except Exception as e:
            print(f"获取概念数据失败: {e}")
        
        return concepts
    
    def get_major_basic_info(self, major_id: int) -> Dict[str, Any]:
        """获取专业基本信息"""
        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT m.id, m.name, mc.name as category_name, 
                       COALESCE(mmd.heat_index, 85.0) as heat_index, 
                       COALESCE(mmd.employment_rate, 90.0) as employment_rate, 
                       COALESCE(mmd.avg_salary::text, '暂无数据') as avg_salary, 
                       m.description, m.employment_direction, m.main_courses,
                       COALESCE(mmd.employment_prospects, m.description) as career_prospects
                FROM majors m
                LEFT JOIN major_categories mc ON m.category_id = mc.id
                LEFT JOIN major_market_data mmd ON m.id = mmd.major_id
                WHERE m.id = %s
                """
                cursor.execute(query, (major_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "id": result[0],
                        "name": result[1],
                        "category_name": result[2] or "工学",
                        "heat_index": float(result[3]) if result[3] else 85.0,
                        "employment_rate": float(result[4]) if result[4] else 90.0,
                        "avg_salary": result[5] or "暂无数据",
                        "description": result[6] or "",
                        "career_prospects": result[9] or "",
                        "courses": result[8] or [],
                        "employment_directions": (result[7] or "").split("、") if result[7] else []
                    }
        except Exception as e:
            print(f"获取基本信息失败: {e}")
        
        return {}
    
    def get_major_notes(self, major_name: str) -> Dict[str, Any]:
        """获取注意事项数据"""
        # 基于专业类别的注意事项
        notes_map = {
            "工学": {
                "learning_requirements": [
                    "需要较强的数学基础，特别是高等数学、线性代数、概率统计",
                    "需要良好的逻辑思维能力和抽象思维能力",
                    "英语阅读能力重要，很多先进技术资料都是英文"
                ],
                "employment_requirements": [
                    "需要持续学习新技术，技术更新迭代快",
                    "项目经验比学历更重要",
                    "团队协作和沟通能力是必需的"
                ],
                "salary_workload": [
                    "起薪较高，头部企业起薪可达30-50万",
                    "加班是常态，互联网大厂工作强度大",
                    "35岁后可能面临职业转型风险"
                ],
                "career_stability": [
                    "35岁后稳定性相对较低，技术迭代快",
                    "需要不断学习新技能以保持竞争力",
                    "创业和自由职业是常见选择"
                ],
                "development_space": [
                    "向管理岗位发展：技术总监、架构师、CTO",
                    "向专业领域深耕：AI专家、安全专家",
                    "向产品岗位：产品经理、项目经理"
                ],
                "development_suggestions": [
                    "建立技术博客或GitHub，提升个人品牌",
                    "参与开源项目，积累项目经验",
                    "定期参加技术大会和培训"
                ]
            },
            "医学": {
                "learning_requirements": [
                    "需要读博或硕士才能进入好医院",
                    "学习周期长，投入成本高",
                    "需要良好的心理素质和沟通能力"
                ],
                "employment_requirements": [
                    "必须持有执业医师资格证",
                    "临床经验非常重要",
                    "医院等级和地域影响收入水平"
                ],
                "salary_workload": [
                    "规培期工资较低（3-5年）",
                    "成熟期收入稳定，顶尖医院可达30万+"
                ],
                "career_stability": [
                    "35岁后稳定性最高，经验越老越吃香",
                    "不受经济周期影响"
                ],
                "development_space": [
                    "向专家发展：主任医师、科室主任、医院管理",
                    "向教学发展：医学院教授、科研人员"
                ],
                "development_suggestions": [
                    "注重临床技能和科研能力培养",
                    "考虑进一步深造或读博",
                    "建立良好的医患沟通能力"
                ]
            },
            "经济学": {
                "learning_requirements": [
                    "需要扎实的数学基础，特别是统计学和计量经济学",
                    "需要良好的数据分析和逻辑思维能力",
                    "关注宏观经济政策和市场动态"
                ],
                "employment_requirements": [
                    "头部机构要求名校背景，硕士起步",
                    "需要相关的实习经验和证书（CFA、CPA等）",
                    "人脉资源和沟通能力很重要"
                ],
                "salary_workload": [
                    "起薪高，头部机构可达20-40万",
                    "工作压力大，业绩导向明显",
                    "受经济周期影响较大"
                ],
                "career_stability": [
                    "行业周期性明显，牛市高薪熊市裁员",
                    "需要不断适应市场变化",
                    "资深人才相对稳定"
                ],
                "development_space": [
                    "向投资银行、基金、券商等金融机构发展",
                    "向企业财务部门发展：CFO、财务总监",
                    "向咨询公司、监管部门发展"
                ],
                "development_suggestions": [
                    "尽早规划职业方向，确定目标领域",
                    "积累实习经验和专业证书",
                    "建立行业人脉网络"
                ]
            },
            "法学": {
                "learning_requirements": [
                    "需要通过法律职业资格考试（法考）",
                    "需要扎实的法律基础和逻辑思维能力",
                    "需要良好的文书写作和口头表达能力"
                ],
                "employment_requirements": [
                    "法考通过率约15%，需要充分准备",
                    "红圈所对学历要求极高，通常需要名校背景",
                    "实习经验和人脉资源很重要"
                ],
                "salary_workload": [
                    "起薪差异大，红圈所可达20-30万，普通律所5-10万",
                    "工作强度大，需要经常加班和处理复杂案件",
                    "独立执业后收入不稳定，取决于案源"
                ],
                "career_stability": [
                    "案源是关键，独立执业前期收入不稳定",
                    "随着经验积累，稳定性逐渐提高",
                    "可以转向企业法务、公务员等稳定岗位"
                ],
                "development_space": [
                    "向合伙人发展：律所合伙人、高级律师",
                    "向专业化发展：知识产权、金融法等专业领域",
                    "向企业法务、公司法务总监发展"
                ],
                "development_suggestions": [
                    "尽早通过法考并积累实践经验",
                    "建立专业领域优势",
                    "注重人脉积累和个人品牌建设"
                ]
            }
        }
        
        return notes_map.get(self._get_major_category(major_name), notes_map["工学"])
    
    def _get_major_category(self, major_name: str) -> str:
        """获取专业大类"""
        category_mapping = {
            "计算机科学与技术": "工学",
            "电子信息工程": "工学", 
            "软件工程": "工学",
            "金融学": "经济学",
            "临床医学": "医学",
            "法学": "法学"
        }
        return category_mapping.get(major_name, "工学")

# API响应模型
class APIResponse:
    @staticmethod
    def success(data: Any, message: str = "操作成功") -> Dict[str, Any]:
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, code: int = 500) -> Dict[str, Any]:
        return {
            "success": False,
            "error": message,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }

# 创建服务实例
detail_service = MajorDetailService()

# 获取专业详情API（v2.0）
@app.get("/api/v2/majors/{major_id}/detail")
async def get_major_detail_v2(major_id: int):
    try:
        # 获取专业基本信息
        basic_info = detail_service.get_major_basic_info(major_id)
        if not basic_info:
            raise HTTPException(status_code=404, detail="专业不存在")
        
        # 获取专业概念数据
        major_concepts = detail_service.get_major_concept_data(basic_info["name"])
        
        # 获取注意事项数据
        warnings = detail_service.get_major_notes(basic_info["name"])
        
        # 构建完整的专业详情数据
        detail_data = {
            **basic_info,
            "major_concepts": major_concepts,
            "core_courses": basic_info["courses"],
            "employment_directions": basic_info["employment_directions"],
            "warnings": warnings
        }
        
        return APIResponse.success(detail_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取专业详情失败: {e}")
        return APIResponse.error("服务器内部错误", 500)

# 健康检查
@app.get("/health")
async def health_check():
    return APIResponse.success({"status": "healthy"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")