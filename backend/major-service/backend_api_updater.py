#!/usr/bin/env python3
"""
Backend Agent：更新专业详情API以支持四个分组内容
根据用户需求，专业详情需要包含：
1. 专业概念介绍（起源、发展历史、重大事件、现状与未来前景）
2. 核心课程（真实数据）
3. 就业前景（仅就业方向）
4. 注意事项（学习要求、就业要求、薪资与工作强度、职业稳定性、发展空间、发展建议）
"""

import psycopg2
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
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
        try:
            query = """
                SELECT 
                    concept_type,
                    title,
                    content,
                    year,
                    sort_order
                FROM major_concepts 
                WHERE major_name = %s
                ORDER BY concept_type, sort_order
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, (major_name,))
                results = cursor.fetchall()
                
                # 按类型组织数据
                concept_data = {
                    "professional_concept": {
                        "origin": "",
                        "development_history": [],
                        "major_events": [],
                        "current_status": "",
                        "future_prospects": ""
                    },
                    "timeline_events": []
                }
                
                for row in results:
                    concept_type, title, content, year, sort_order = row
                    if concept_type == "origin":
                        concept_data["professional_concept"]["origin"] = content
                    elif concept_type == "development_history":
                        concept_data["professional_concept"]["development_history"].append({
                            "year": year,
                            "title": title,
                            "description": content
                        })
                    elif concept_type == "major_events":
                        concept_data["professional_concept"]["major_events"].append({
                            "year": year,
                            "title": title,
                            "description": content
                        })
                    elif concept_type == "current_status":
                        concept_data["professional_concept"]["current_status"] = content
                    elif concept_type == "future_prospects":
                        concept_data["professional_concept"]["future_prospects"] = content
                
                # 生成时间线事件
                all_events = (concept_data["professional_concept"]["development_history"] + 
                           concept_data["professional_concept"]["major_events"])
                all_events.sort(key=lambda x: x["year"] if x["year"] else 9999)
                
                concept_data["timeline_events"] = all_events
                
                return concept_data
                
        except Exception as e:
            return {
                "professional_concept": {
                    "origin": "暂无数据",
                    "development_history": [],
                    "major_events": [],
                    "current_status": "暂无数据",
                    "future_prospects": "暂无数据"
                },
                "timeline_events": []
            }
    
    def get_major_notes(self, major_name: str) -> List[Dict[str, Any]]:
        """获取注意事项数据"""
        # 基于专业类别的注意事项
        notes_map = {
            "工学": {
                "学习要求": [
                    "需要较强的数学基础，特别是高等数学、线性代数、概率统计",
                    "需要良好的逻辑思维能力和抽象思维能力",
                    "英语阅读能力重要，因为很多先进技术资料都是英文"
                ],
                "就业要求": [
                    "需要持续学习新技术，技术更新迭代快",
                    "项目经验比学历更重要",
                    "团队协作和沟通能力是必需的"
                ],
                "薪资与工作强度": [
                    "起薪较高，但差距很大，头部企业起薪可达30-50万",
                    "加班是常态，特别是互联网大厂",
                    "35岁后可能面临职业转型或淘汰风险",
                    "工作强度大，需要良好的抗压能力"
                ],
                "职业稳定性": [
                    "35岁后稳定性相对较低，技术迭代快",
                    "需要不断学习新技能以保持竞争力",
                    "创业和自由职业是常见的选择"
                ],
                "发展空间": [
                    "向管理岗位发展：技术总监、架构师、CTO",
                    "向专业领域深耕：AI专家、安全专家、云计算架构师",
                    "向产品岗位：产品经理、项目经理",
                    "创业或咨询服务"
                ],
                "development_suggestions": [
                    "建立技术博客或GitHub，提升个人品牌",
                    "参与开源项目，积累项目经验",
                    "定期参加技术大会和培训",
                    "保持对新兴技术的敏感度",
                    "建立良好的人脉网络"
                ]
            },
            "医学": {
                "学习要求": [
                    "需要读博或硕士才能进入好的医院",
                    "学习周期长，投入成本高",
                    "需要良好的心理素质和沟通能力",
                    "需要通过国家执业医师资格考试"
                ],
                "就业要求": [
                    "必须持有执业医师资格证",
                    "临床经验非常重要",
                    "需要不断参加继续教育",
                    "医院等级和地域影响收入水平"
                ],
                "薪资与工作强度": [
                    "规培期工资较低（3-5年）",
                    "成熟期收入稳定，顶尖医院可达30万+",
                    "夜班、值班是常态，工作强度极大",
                    "医患关系压力大，需要良好心理素质"
                ],
                "职业稳定性": [
                    "35岁后稳定性最高，经验越老越吃香",
                    "不受经济周期影响",
                    "私立医院风险较高，公立医院非常稳定"
                ],
                "发展空间": [
                    "向专家发展：主任医师、科室主任、医院管理",
                    "向教学发展：医学院教授、科研人员",
                    "向专科发展：各类专科医生",
                    "向医院管理发展"
                ],
                "development_suggestions": [
                    "注重临床技能和科研能力培养",
                    "考虑进一步深造或读博",
                    "建立良好的医患沟通能力",
                    "参与临床研究和论文发表"
                ]
            },
            "经济学": {
                "学习要求": [
                    "需要扎实的数学基础",
                    "需要良好的数据分析和逻辑能力",
                    "英语能力在金融行业很重要",
                    "需要了解经济理论和市场动态"
                ],
                "就业要求": [
                    "名校学历是进入高端金融机构的门槛",
                    "相关证书（CFA、FRM）有优势",
                    "实习经验和项目经验很重要",
                    "需要良好的沟通和团队合作能力"
                ],
                "薪资与工作强度": [
                    "起薪就很高，顶级投行可达百万级别",
                    "工作时间长，但弹性相对较好",
                    "业绩压力大，KPI考核严格",
                    "市场波动影响收入稳定性"
                ],
                "职业稳定性": [
                    "受经济周期影响明显，牛市高薪熊市裁员",
                    "需要不断更新知识结构以保持竞争力",
                    "金融监管趋严，合规要求高"
                ],
                "发展空间": [
                    "向管理层发展：部门主管、总监、VP",
                    "向专业领域发展：投资银行家、分析师、风控专家",
                    "向创业发展：基金经理、金融科技创业",
                    "向学术发展：大学教授、研究机构"
                ],
                "development_suggestions": [
                    "考取含金量较高的专业证书",
                    "培养数据分析和编程技能",
                    "建立行业人脉和资源",
                    "关注金融科技和ESG发展趋势",
                    "保持学习和知识更新"
                ]
            },
            "法学": {
                "学习要求": [
                    "需要通过法考（通过率约15%）",
                    "需要深厚的法学理论基础",
                    "需要良好的逻辑思维和文字表达能力",
                    "英语能力在国际法领域很重要"
                ],
                "就业要求": [
                    "需要通过法律职业资格考试",
                    "实习经验对找工作很重要",
                    "知名律所对学历要求极高",
                    "需要不断学习新法律法规"
                ],
                "薪资与工作强度": [
                    "起薪相对较低，但成长空间大",
                    "工作时间相对规律，但案件复杂时加班多",
                    "案源质量影响收入，独立执业前期收入不稳定",
                    "红圈所薪资极高，但工作强度极大"
                ],
                "职业稳定性": [
                    "执业年限越长越稳定",
                    "案源是关键，需要建立良好的人脉关系",
                    "受经济周期影响相对较小",
                    "可向公务员、法官、检察官等方向发展"
                ],
                "发展空间": [
                    "向专业化发展：成为特定领域专家",
                    "向管理层发展：律所合伙人、律所主任",
                    "向司法系统发展：法官、检察官、仲裁员",
                    "向学术界发展：法学教授、研究学者"
                ],
                "development_suggestions": [
                    "尽早通过法考并积累实践经验",
                    "建立专业领域优势，不要样样通",
                    "培养商业思维和市场洞察力",
                    "注重语言能力和国际视野",
                    "建立专业网络和口碑"
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
async def get_major_detail_v2(
    major_id: int,
    concept_type: str = Query(None, description="概念类型：origin, development_history, major_events, current_status, future_prospects"),
    service: MajorDetailService = Depends(get_db_connection)
):
    """获取专业详情（支持四个分组）"""
    try:
        # 先获取基本信息
        with service.connection.cursor() as cursor:
            basic_query = """
                SELECT 
                    m.id,
                    m.name,
                    m.code,
                    m.description,
                    m.training_objective,
                    m.main_courses,
                    m.employment_direction,
                    m.study_period,
                    m.degree_awarded,
                    m.national_key_major,
                    mc.name as category_name,
                    mmd.employment_rate,
                    mmd.avg_salary,
                    mmd.salary_growth_rate,
                    mmd.heat_index,
                    mmd.industry_demand_score,
                    mmd.future_prospects_score,
                    mmd.talent_shortage,
                    mmd.data_period,
                    mmd.employment_prospects
                FROM majors m
                LEFT JOIN major_categories mc ON m.category_id = mc.id
                LEFT JOIN major_market_data mmd ON m.id = mmd.major_id
                WHERE m.id = %s
            """
            
            cursor.execute(basic_query, (major_id,))
            basic_result = cursor.fetchone()
            
            if not basic_result:
                return APIResponse.error("专业不存在", 404)
            
            major_data = {
                "id": basic_result[0],
                "name": basic_result[1],
                "code": basic_result[2] or "",
                "description": basic_result[3] or "",
                "training_objective": basic_result[4] or "",
                "main_courses": basic_result[5] or [],
                "employment_direction": basic_result[6] or "",
                "study_period": basic_result[7] or 4,
                "degree_awarded": basic_result[8] or "",
                "national_key_major": basic_result[9] or False,
                "category_name": basic_result[10] or "",
                "market_data": {
                    "employment_rate": basic_result[11],
                    "avg_salary": float(basic_result[12]) if basic_result[12] else None,
                    "salary_growth_rate": basic_result[13],
                    "heat_index": basic_result[14],
                    "industry_demand_score": basic_result[15],
                    "future_prospects_score": basic_result[16],
                    "talent_shortage": basic_result[17],
                    "data_period": basic_result[18],
                    "employment_prospects": basic_result[19]
                }
            }
            
            # 获取概念数据
            concept_data = detail_service.get_major_concept_data(major_data["name"])
            
            # 获取注意事项
            notes_data = detail_service.get_major_notes(major_data["name"])
            
            # 获取核心课程（真实数据）
            core_courses = major_data["main_courses"] if major_data["main_courses"] else []
            
            # 获取就业方向（简化版）
            employment_directions = major_data["employment_direction"].split('、') if major_data["employment_direction"] else []
            
            # 组装响应数据
            response_data = {
                "basic_info": major_data,
                "professional_concept": concept_data["professional_concept"],
                "core_courses": core_courses,
                "employment_prospects": {
                    "directions": employment_directions
                },
                "considerations": notes_data,
                "data_sources": {
                    "basic_info": ["阳光高考", "各高校官网"],
                    "concept_data": ["阳光高考", "中国教育在线"],
                    "market_data": ["麦可思报告", "智联招聘", "前程无忧"]
                },
                "updated_at": datetime.now().isoformat()
            }
            
            return APIResponse.success(response_data, "成功获取专业详情")
            
    except Exception as e:
            return APIResponse.error(f"获取专业详情失败: {str(e)}", 500)

# 根路径
@app.get("/")
async def root():
    return APIResponse.success({
        "service": "专业详情API v2.0",
        "version": "2.0.0",
        "description": "支持四个分组的完整专业信息展示",
        "endpoints": {
            "major_detail": "/api/v2/majors/{major_id}/detail"
        }
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
        '''
        
        print("✅ 新API服务创建完成，端口:8003")
    
    def process_api_update(self):
        """处理API更新"""
        try:
            # 创建新API文件
            self.create_new_api_endpoint()
            
            print("✅ 后端API更新完成!")
            return {"success": True, "message": "后端API更新成功"}
            
        except Exception as e:
            print(f"❌ API更新失败: {e}")
            return {"success": False, "error": str(e)}

def main():
    """主函数"""
    print("🔧 Backend Agent 开始更新专业详情API...")
    
    updater = BackendAPIUpdater()
    
    try:
        # 处理API更新
        result = updater.process_api_update()
        
        if result["success"]:
            print("✅ 后端API更新任务完成!")
        else:
            print(f"❌ 后端API更新失败: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
    finally:
        print("🔌 后端API更新完成")

if __name__name__ == "__main__":
    main()