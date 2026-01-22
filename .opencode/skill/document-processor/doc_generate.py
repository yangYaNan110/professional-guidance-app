#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-generate Skill - 专业介绍生成

功能：
1. 根据爬取和总结的内容生成专业介绍
2. 输出结构化的专业介绍文档
3. 支持多种输出格式
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class ContentSection(Enum):
    """内容章节"""
    ORIGIN = "origin"           # 溯源
    DEVELOPMENT = "development" # 发展
    CURRENT_STATUS = "current"  # 现状
    TRENDS = "trends"           # 趋势
    COURSES = "courses"         # 核心课程
    CAREER = "career"           # 就业方向
    RELATED_MAJORS = "related"  # 相关专业


@dataclass
class MajorIntroduction:
    """专业介绍"""
    name: str
    category: str
    origin: str
    development: str
    current_status: str
    trends: str
    core_courses: List[str] = field(default_factory=list)
    career_prospects: str = ""
    related_majors: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentGenerator:
    """内容生成器"""
    
    # 专业类别的默认课程
    DEFAULT_COURSES = {
        "工学": ["高等数学", "线性代数", "概率论与数理统计", "大学物理", "计算机基础", "专业核心课"],
        "理学": ["高等数学", "线性代数", "概率论与数理统计", "大学物理", "专业基础课"],
        "医学": ["人体解剖学", "生理学", "生物化学", "病理学", "药理学", "临床医学"],
        "法学": ["法理学", "宪法学", "民法学", "刑法学", "行政法学", "国际法学"],
        "经济学": ["微观经济学", "宏观经济学", "计量经济学", "货币银行学", "财政学"],
        "文学": ["现代汉语", "古代汉语", "文学概论", "写作", "外国文学", "中国文学"],
        "教育学": ["教育学原理", "教育心理学", "课程与教学论", "教育研究方法"],
        "农学": ["植物学", "动物学", "遗传学", "生物化学", "农学概论"],
        "历史学": ["中国史", "世界史", "史学概论", "历史文献学", "考古学"]
    }
    
    def __init__(self):
        pass
    
    def generate_major_intro(
        self,
        major_name: str,
        category: str,
        summarized_content: Dict[str, Any],
        related_majors: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> MajorIntroduction:
        """
        生成专业介绍
        
        Args:
            major_name: 专业名称
            category: 专业类别
            summarized_content: 总结的内容字典
            related_majors: 相关专业列表
            options: 生成选项
            
        Returns:
            MajorIntroduction: 生成的专业介绍
        """
        options = options or {}
        
        # 提取各部分内容
        origin = summarized_content.get("origin", "") or self._generate_origin(major_name, category)
        development = summarized_content.get("development", "") or self._generate_development(major_name, category)
        current_status = summarized_content.get("current_status", "") or self._generate_current_status(major_name, category)
        trends = summarized_content.get("trends", "") or self._generate_trends(major_name, category)
        career_prospects = summarized_content.get("career", "") or self._generate_career(major_name, category)
        
        # 获取核心课程
        core_courses = summarized_content.get("courses", []) or self._get_default_courses(category)
        
        # 获取相关专业
        if related_majors is None:
            related_majors = self._get_related_majors(category, major_name)
        
        # 构建专业介绍
        intro = MajorIntroduction(
            name=major_name,
            category=category,
            origin=origin,
            development=development,
            current_status=current_status,
            trends=trends,
            core_courses=core_courses,
            career_prospects=career_prospects,
            related_majors=related_majors,
            sources=summarized_content.get("sources", []),
            metadata={
                "language": options.get("language", "zh-CN"),
                "format": options.get("format", "structured")
            }
        )
        
        return intro
    
    def _generate_origin(self, major_name: str, category: str) -> str:
        """生成溯源内容"""
        templates = {
            "工学": f"{major_name}是{category}的重要分支，随着工业革命和技术发展而逐步形成。",
            "理学": f"{major_name}是基础科学的重要组成部分，研究{major_name}的基本理论和规律。",
            "医学": f"{major_name}是人类对抗疾病、维护健康的重要学科，历史可追溯至古代。",
            "法学": f"{major_name}是研究法律规范及其适用规律的学科，是社会科学的重要分支。",
            "经济学": f"{major_name}是研究经济活动规律的学科，是社会科学的核心领域之一。",
            "文学": f"{major_name}是研究语言文字及其应用的学科，是人文科学的重要组成部分。",
            "教育学": f"{major_name}是研究教育规律和方法的学科，对人才培养具有重要意义。",
            "农学": f"{major_name}是研究农业生产和农业科学的学科，对国家粮食安全至关重要。",
            "历史学": f"{major_name}是研究人类历史发展规律的学科，是人文科学的基础学科。"
        }
        
        return templates.get(category, f"{major_name}是{category}的重要专业之一，具有悠久的历史背景。")
    
    def _generate_development(self, major_name: str, category: str) -> str:
        """生成发展内容"""
        return f"{major_name}经历了从萌芽到成熟的发展历程。随着科技进步和社会需求变化，{major_name}的研究范围和应用领域不断扩大。当前，{major_name}已成为{category}领域不可或缺的重要组成部分。"
    
    def _generate_current_status(self, major_name: str, category: str) -> str:
        """生成现状内容"""
        return f"当前，{major_name}在中国的发展态势良好。随着相关产业的快速发展，{major_name}人才需求旺盛。该专业的就业前景广阔，薪资水平相对较高。"
    
    def _generate_trends(self, major_name: str, category: str) -> str:
        """生成趋势内容"""
        trends_templates = {
            "工学": "智能制造、工业互联网等新技术推动{topic}快速发展。",
            "理学": "学科交叉融合趋势明显，{topic}与其他学科的结合日益紧密。",
            "医学": "精准医学、智慧医疗是{topic}的重要发展方向。",
            "法学": "数字法学、涉外法治等新兴领域为{topic}带来新机遇。",
            "经济学": "数字经济、绿色金融正在重塑{topic}的发展格局。",
            "文学": "新媒体、数字传播为{topic}带来新的研究视角和应用场景。",
            "教育学": "教育信息化、终身学习推动{topic}不断创新发展。",
            "农学": "智慧农业、绿色农业是{topic}的重要发展方向。",
            "历史学": "数字人文、公众史学研究为{topic}带来新的发展机遇。"
        }
        
        template = trends_templates.get(category, "跨学科融合是{topic}未来发展的重要趋势。")
        return template.format(topic=major_name)
    
    def _generate_career(self, major_name: str, category: str) -> str:
        """生成职业前景内容"""
        return f"{major_name}专业毕业生就业面广泛，可在相关企业、事业单位、科研院所等从事研究、开发、管理等工作。随着经验积累，职业发展空间广阔。"
    
    def _get_default_courses(self, category: str) -> List[str]:
        """获取默认课程列表"""
        return self.DEFAULT_COURSES.get(category, ["专业基础课", "专业核心课", "专业选修课"])
    
    def _get_related_majors(self, category: str, major_name: str) -> List[str]:
        """获取相关专业列表"""
        related_map = {
            "工学": ["计算机科学与技术", "软件工程", "电子信息工程", "机械工程"],
            "理学": ["数学", "物理学", "化学", "统计学"],
            "医学": ["临床医学", "口腔医学", "护理学", "药学"],
            "法学": ["法学", "社会学", "政治学与行政学", "知识产权"],
            "经济学": ["金融学", "经济学", "工商管理", "会计学"],
            "文学": ["汉语言文学", "英语", "新闻学", "传播学"],
            "教育学": ["教育学", "学前教育", "体育教育", "心理学"],
            "农学": ["农学", "动物医学", "园林", "食品科学"],
            "历史学": ["历史学", "考古学", "博物馆学", "世界史"]
        }
        
        related = related_map.get(category, [])
        # 移除自身
        related = [r for r in related if r != major_name]
        
        return related
    
    def to_dict(self, intro: MajorIntroduction) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": intro.name,
            "category": intro.category,
            "origin": intro.origin,
            "development": intro.development,
            "current_status": intro.current_status,
            "trends": intro.trends,
            "core_courses": intro.core_courses,
            "career_prospects": intro.career_prospects,
            "related_majors": intro.related_majors,
            "sources": intro.sources,
            "generated_at": intro.generated_at.isoformat(),
            "metadata": intro.metadata
        }
    
    def to_markdown(self, intro: MajorIntroduction) -> str:
        """转换为Markdown格式"""
        lines = []
        
        lines.append(f"# {intro.name}")
        lines.append(f"\n**类别**: {intro.category}")
        lines.append(f"\n## 溯源\n\n{intro.origin}")
        lines.append(f"\n## 发展\n\n{intro.development}")
        lines.append(f"\n## 现状\n\n{intro.current_status}")
        lines.append(f"\n## 趋势\n\n{intro.trends}")
        
        if intro.core_courses:
            lines.append(f"\n## 核心课程\n\n")
            for course in intro.core_courses:
                lines.append(f"- {course}")
        
        lines.append(f"\n## 职业前景\n\n{intro.career_prospects}")
        
        if intro.related_majors:
            lines.append(f"\n## 相关专业\n\n")
            for major in intro.related_majors:
                lines.append(f"- {major}")
        
        lines.append(f"\n---\n*Generated at {intro.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(lines)


# 便捷函数
def generate_major_introduction(
    major_name: str,
    category: str,
    summarized_content: Dict[str, Any],
    related_majors: Optional[List[str]] = None,
    output_format: str = "dict"
) -> Any:
    """
    生成专业介绍
    
    Args:
        major_name: 专业名称
        category: 专业类别
        summarized_content: 总结的内容字典
        related_majors: 相关专业列表
        output_format: 输出格式（dict/markdown）
        
    Returns:
        生成的专业介绍
    """
    generator = ContentGenerator()
    
    intro = generator.generate_major_intro(
        major_name=major_name,
        category=category,
        summarized_content=summarized_content,
        related_majors=related_majors
    )
    
    if output_format == "markdown":
        return generator.to_markdown(intro)
    
    return generator.to_dict(intro)


if __name__ == "__main__":
    # 测试
    content = {
        "origin": "社会学起源于19世纪中叶，孔德、涂尔干等学者开始系统研究社会现象。",
        "development": "社会学经历了经典时期、现代时期的发展，理论体系不断完善。",
        "current_status": "当前社会学在中国发展良好，社会治理现代化需求旺盛。",
        "trends": "数字社会学、人口老龄化研究是重要发展方向。",
        "sources": [
            {"title": "百度百科", "url": "https://baike.baidu.com/item/社会学", "reliability": 0.9}
        ]
    }
    
    intro = generate_major_introduction(
        major_name="社会学",
        category="法学",
        summarized_content=content
    )
    
    print(json.dumps(intro, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 50)
    print(generate_major_introduction(
        major_name="社会学",
        category="法学",
        summarized_content=content,
        output_format="markdown"
    ))
