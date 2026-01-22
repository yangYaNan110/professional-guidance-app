#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-analyze Skill - 文档需求分析和意图理解

功能：
1. 解析用户输入，提取关键信息
2. 理解用户查询意图
3. 确定任务类型和参数
4. 输出结构化的需求分析结果
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import re


class TaskType(Enum):
    """任务类型枚举"""
    MAJOR_INTRO = "major_intro"           # 专业介绍
    INDUSTRY_ANALYSIS = "industry_analysis"  # 行业分析
    CAREER_PROSPECTS = "career_prospects"    # 职业前景
    UNIVERSITY_INFO = "university_info"      # 院校信息
    TREND_ANALYSIS = "trend_analysis"        # 趋势分析
    GENERAL_QUERY = "general_query"          # 通用查询


@dataclass
class ParsedQuery:
    """解析后的查询结构"""
    task_type: TaskType
    main_query: str
    category: Optional[str]
    province: Optional[str]
    score: Optional[int]
    year: Optional[int]
    keywords: List[str]
    intent: str
    confidence: float


class DocumentAnalyzer:
    """文档需求分析器"""
    
    # 专业类别映射
    MAJOR_CATEGORIES = {
        "工学": ["计算机科学与技术", "人工智能", "软件工程", "电子信息工程", "机械工程"],
        "理学": ["数学", "物理学", "化学", "统计学"],
        "医学": ["临床医学", "口腔医学", "护理学", "药学"],
        "法学": ["法学", "社会学", "社会工作", "政治学与行政学"],
        "经济学": ["金融学", "经济学", "工商管理", "会计学"],
        "文学": ["汉语言文学", "英语", "新闻学", "传播学"],
        "教育学": ["教育学", "学前教育", "体育教育"],
        "农学": ["农学", "动物医学", "园林"],
        "历史学": ["历史学", "考古学", "博物馆学"]
    }
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        TaskType.MAJOR_INTRO: ["专业", "介绍", "是什么", "学什么", "专业介绍"],
        TaskType.INDUSTRY_ANALYSIS: ["行业", "产业", "市场", "行业分析"],
        TaskType.CAREER_PROSPECTS: ["就业", "职业", "前景", "工作", "薪资"],
        TaskType.UNIVERSITY_INFO: ["大学", "院校", "学校", "录取"],
        TaskType.TREND_ANALYSIS: ["趋势", "发展", "未来", "前景"]
    }
    
    def __init__(self):
        self.known_provinces = self._load_provinces()
    
    def _load_provinces(self) -> List[str]:
        """加载省份列表"""
        return [
            "北京", "天津", "河北", "山西", "内蒙古",
            "辽宁", "吉林", "黑龙江", "上海", "江苏",
            "浙江", "安徽", "福建", "江西", "山东",
            "河南", "湖北", "湖南", "广东", "广西",
            "海南", "重庆", "四川", "贵州", "云南",
            "陕西", "甘肃", "青海", "宁夏", "新疆"
        ]
    
    def analyze(self, query: str, context: Optional[Dict[str, Any]] = None) -> ParsedQuery:
        """
        分析用户查询
        
        Args:
            query: 用户查询文本
            context: 上下文信息（可选）
            
        Returns:
            ParsedQuery: 解析后的查询结构
        """
        # 提取省份
        province = self._extract_province(query)
        
        # 提取分数
        score = self._extract_score(query)
        
        # 提取年份
        year = self._extract_year(query)
        
        # 确定任务类型
        task_type = self._determine_task_type(query)
        
        # 提取主要查询词
        main_query = self._extract_main_query(query, task_type)
        
        # 提取类别
        category = self._extract_category(main_query)
        
        # 提取关键词
        keywords = self._extract_keywords(main_query)
        
        # 确定意图
        intent = self._determine_intent(query, task_type)
        
        # 计算置信度
        confidence = self._calculate_confidence(task_type, main_query, keywords)
        
        return ParsedQuery(
            task_type=task_type,
            main_query=main_query,
            category=category,
            province=province,
            score=score,
            year=year,
            keywords=keywords,
            intent=intent,
            confidence=confidence
        )
    
    def _extract_province(self, query: str) -> Optional[str]:
        """提取省份信息"""
        for province in self.known_provinces:
            if province in query:
                return province
        return None
    
    def _extract_score(self, query: str) -> Optional[int]:
        """提取分数信息"""
        # 匹配 "XX分" 或 "分数XX"
        patterns = [
            r'(\d{3,4})\s*分',
            r'分数[：:\s]*(\d{3,4})',
            r'预估[：:\s]*(\d{3,4})',
            r'考[了\s]*(\d{3,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                score = int(match.group(1))
                if 0 <= score <= 750:  # 合理分数范围
                    return score
        return None
    
    def _extract_year(self, query: str) -> Optional[int]:
        """提取年份信息"""
        patterns = [
            r'(\d{4})\s*年',
            r'20[2-9]\d'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                year = int(match.group(1))
                if 2020 <= year <= 2030:
                    return year
        return None
    
    def _determine_task_type(self, query: str) -> TaskType:
        """确定任务类型"""
        query_lower = query.lower()
        
        for task_type, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    return task_type
        
        # 默认返回通用查询
        return TaskType.GENERAL_QUERY
    
    def _extract_main_query(self, query: str, task_type: TaskType) -> str:
        """提取主要查询词"""
        # 移除常见的提问词和修饰词
        stop_words = [
            "是什么", "怎么样", "好不好", "介绍一下",
            "帮我查一下", "我想了解", "请问", "能告诉我",
            "的", "关于", "有关"
        ]
        
        main_query = query
        for word in stop_words:
            main_query = main_query.replace(word, "")
        
        # 清理多余空格
        main_query = " ".join(main_query.split())
        
        return main_query.strip()
    
    def _extract_category(self, query: str) -> Optional[str]:
        """提取专业类别"""
        for category, majors in self.MAJOR_CATEGORIES.items():
            for major in majors:
                if major in query:
                    return category
        return None
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取关键词"""
        # 使用简单的分词逻辑
        keywords = []
        
        # 提取长度大于2的词语
        words = re.findall(r'[\u4e00-\u9fff]{2,}', query)
        keywords.extend(words)
        
        # 去重
        keywords = list(set(keywords))
        
        return keywords
    
    def _determine_intent(self, query: str, task_type: TaskType) -> str:
        """确定用户意图"""
        intent_templates = {
            TaskType.MAJOR_INTRO: "了解{query}专业的详细信息",
            TaskType.INDUSTRY_ANALYSIS: "分析{query}行业的发展现状和趋势",
            TaskType.CAREER_PROSPECTS: "了解{query}职业的就业前景和薪资",
            TaskType.UNIVERSITY_INFO: "查询{query}院校的相关信息",
            TaskType.TREND_ANALYSIS: "分析{query}的发展趋势",
            TaskType.GENERAL_QUERY: "查询{query}相关信息"
        }
        
        template = intent_templates.get(task_type, intent_templates[TaskType.GENERAL_QUERY])
        return template.replace("{query}", query[:20])
    
    def _calculate_confidence(self, task_type: TaskType, main_query: str, keywords: List[str]) -> float:
        """计算分析置信度"""
        confidence = 0.5  # 基础置信度
        
        # 任务类型明确
        if task_type != TaskType.GENERAL_QUERY:
            confidence += 0.2
        
        # 有足够关键词
        if len(keywords) >= 2:
            confidence += 0.15
        elif len(keywords) >= 1:
            confidence += 0.1
        
        # 查询长度适中
        if 5 <= len(main_query) <= 30:
            confidence += 0.15
        
        return min(confidence, 1.0)


# 便捷函数
def analyze_query(query: str, context: Optional[Dict[str, Any]] = None) -> ParsedQuery:
    """
    分析用户查询
    
    Args:
        query: 用户查询文本
        context: 上下文信息（可选）
        
    Returns:
        ParsedQuery: 解析后的查询结构
    """
    analyzer = DocumentAnalyzer()
    return analyzer.analyze(query, context)


if __name__ == "__main__":
    # 测试
    analyzer = DocumentAnalyzer()
    
    test_queries = [
        "社会学专业介绍",
        "计算机专业学什么，好不好就业",
        "山西考生580分能上什么大学",
        "金融行业未来发展趋势",
        "临床医学职业前景和薪资"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = analyzer.analyze(query)
        print(f"  任务类型: {result.task_type.value}")
        print(f"  主要查询: {result.main_query}")
        print(f"  类别: {result.category}")
        print(f"  省份: {result.province}")
        print(f"  分数: {result.score}")
        print(f"  关键词: {result.keywords}")
        print(f"  意图: {result.intent}")
        print(f"  置信度: {result.confidence:.2f}")
