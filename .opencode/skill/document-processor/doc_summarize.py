#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-summarize Skill - 文档智能总结

功能：
1. 对爬取的文档进行智能总结
2. 提取关键信息和知识点
3. 生成结构化的总结内容
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


class SummaryType(Enum):
    """总结类型"""
    BRIEF = "brief"           # 简要总结
    DETAILED = "detailed"     # 详细总结
    KEY_POINTS = "key_points" # 关键点提取
    COMPARISON = "comparison" # 对比分析
    TIMELINE = "timeline"     # 时间线梳理


@dataclass
class DocumentSummary:
    """文档总结结果"""
    summary_type: SummaryType
    summary: str
    key_points: List[str]
    keywords: List[str]
    statistics: Dict[str, Any]
    generated_at: datetime
    confidence: float


class DocumentSummarizer:
    """文档智能总结器"""
    
    # 领域特定的关键词模式
    DOMAIN_PATTERNS = {
        "专业": {
            "origin": ["起源", "诞生", "形成", "历史渊源"],
            "development": ["发展历程", "演变", "发展过程", "发展历史"],
            "current_status": ["现状", "当前", "目前情况", "现在"],
            "trends": ["趋势", "发展方向", "未来", "发展趋势"]
        },
        "行业": {
            "market_size": ["市场规模", "市场容量", "市场价值"],
            "growth_rate": ["增长率", "增速", "增长趋势"],
            "key_players": ["主要企业", "头部公司", "龙头企业"],
            "outlook": ["前景", "展望", "预测", "趋势"]
        },
        "职业": {
            "salary": ["薪资", "收入", "工资", "薪酬"],
            "demand": ["需求", "需求量", "就业需求"],
            "development": ["发展", "晋升", "职业发展"],
            "requirements": ["要求", "任职资格", "技能要求"]
        }
    }
    
    def __init__(self):
        pass
    
    def summarize(
        self,
        content: str,
        summary_type: SummaryType = SummaryType.DETAILED,
        domain: Optional[str] = None
    ) -> DocumentSummary:
        """
        对文档进行总结
        
        Args:
            content: 文档内容
            summary_type: 总结类型
            domain: 领域（专业/行业/职业）
            
        Returns:
            DocumentSummary: 总结结果
        """
        # 提取关键词
        keywords = self._extract_keywords(content)
        
        # 提取关键点
        key_points = self._extract_key_points(content, domain)
        
        # 生成总结
        if summary_type == SummaryType.BRIEF:
            summary = self._generate_brief_summary(content, key_points)
        elif summary_type == SummaryType.KEY_POINTS:
            summary = self._generate_key_points_summary(key_points)
        else:
            summary = self._generate_detailed_summary(content, key_points, domain)
        
        # 计算统计信息
        statistics = self._calculate_statistics(content, keywords, key_points)
        
        # 计算置信度
        confidence = self._calculate_confidence(content, key_points, keywords)
        
        return DocumentSummary(
            summary_type=summary_type,
            summary=summary,
            key_points=key_points,
            keywords=keywords,
            statistics=statistics,
            generated_at=datetime.now(),
            confidence=confidence
        )
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 使用简单的TF-IDF-like算法
        words = re.findall(r'[\u4e00-\u9fff]{2,}', content)
        
        # 词频统计
        word_freq = {}
        stop_words = {"的", "是", "在", "和", "了", "有", "对", "为", "与", "这", "那", "之"}
        
        for word in words:
            if word not in stop_words and len(word) >= 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前20个关键词
        return [word for word, freq in sorted_words[:20]]
    
    def _extract_key_points(self, content: str, domain: Optional[str] = None) -> List[str]:
        """提取关键点"""
        key_points = []
        
        # 尝试使用领域模式
        if domain and domain in self.DOMAIN_PATTERNS:
            patterns = self.DOMAIN_PATTERNS[domain]
            
            for section, keywords in patterns.items():
                for keyword in keywords:
                    if keyword in content:
                        # 提取包含关键词的段落
                        matches = self._extract_section(content, keyword)
                        key_points.extend(matches)
        
        # 如果没有找到领域特定内容，使用通用提取
        if not key_points:
            key_points = self._extract_paragraphs(content)
        
        # 去重和清理
        key_points = list(set(key_points))
        key_points = [p.strip() for p in key_points if len(p.strip()) >= 20]
        
        return key_points[:10]  # 最多返回10个关键点
    
    def _extract_section(self, content: str, keyword: str) -> List[str]:
        """提取包含关键词的段落"""
        sections = []
        
        # 找到关键词位置
        pattern = rf'.{{0,50}}{re.escape(keyword)}.{{0,150}}'
        matches = re.findall(pattern, content)
        
        for match in matches:
            # 清理并添加到列表
            section = match.strip()
            if len(section) >= 20:
                sections.append(section)
        
        return sections
    
    def _extract_paragraphs(self, content: str) -> List[str]:
        """提取段落"""
        # 按句子分割
        sentences = re.split(r'[。！？]', content)
        
        # 选择有意义的句子
        meaningful = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= 30 and not sentence.startswith("http"):
                meaningful.append(sentence)
        
        return meaningful[:10]
    
    def _generate_brief_summary(self, content: str, key_points: List[str]) -> str:
        """生成简要总结"""
        # 取前3个关键点
        summary_points = key_points[:3]
        
        if summary_points:
            return "；".join(summary_points)
        
        # 如果没有关键点，取前100字
        return content[:100] + "..."
    
    def _generate_key_points_summary(self, key_points: List[str]) -> str:
        """生成关键点总结"""
        if not key_points:
            return "暂无相关信息"
        
        lines = []
        for i, point in enumerate(key_points[:5], 1):
            # 截取关键句
            sentence = point[:100] + "..." if len(point) > 100 else point
            lines.append(f"{i}. {sentence}")
        
        return "\n".join(lines)
    
    def _generate_detailed_summary(
        self,
        content: str,
        key_points: List[str],
        domain: Optional[str] = None
    ) -> str:
        """生成详细总结"""
        sections = []
        
        # 溯源
        origin_content = self._find_section_content(content, ["起源", "历史", "由来"])
        if origin_content:
            sections.append(f"【溯源】\n{origin_content}")
        
        # 发展
        development_content = self._find_section_content(content, ["发展", "演变", "历程"])
        if development_content:
            sections.append(f"【发展】\n{development_content}")
        
        # 现状
        current_content = self._find_section_content(content, ["现状", "当前", "目前"])
        if current_content:
            sections.append(f"【现状】\n{current_content}")
        
        # 趋势
        trends_content = self._find_section_content(content, ["趋势", "未来", "发展"])
        if trends_content:
            sections.append(f"【趋势】\n{trends_content}")
        
        if sections:
            return "\n\n".join(sections)
        
        # 如果没有找到特定章节，返回关键点
        return self._generate_brief_summary(content, key_points)
    
    def _find_section_content(self, content: str, keywords: List[str]) -> str:
        """查找包含关键词的段落"""
        for keyword in keywords:
            pattern = rf'{re.escape(keyword)}[^\n。！？]{{0,100}}'
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        
        return ""
    
    def _calculate_statistics(
        self,
        content: str,
        keywords: List[str],
        key_points: List[str]
    ) -> Dict[str, Any]:
        """计算统计信息"""
        # 字符数
        char_count = len(content)
        
        # 词数
        word_count = len(re.findall(r'[\u4e00-\u9fff]+', content))
        
        # 句子数
        sentence_count = len(re.split(r'[。！？]', content))
        
        # 段落数
        paragraph_count = len(content.split('\n'))
        
        return {
            "char_count": char_count,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "keyword_count": len(keywords),
            "key_point_count": len(key_points)
        }
    
    def _calculate_confidence(
        self,
        content: str,
        key_points: List[str],
        keywords: List[str]
    ) -> float:
        """计算置信度"""
        confidence = 0.5
        
        # 内容长度适中
        if 500 <= len(content) <= 10000:
            confidence += 0.2
        elif len(content) < 500:
            confidence -= 0.1
        
        # 有关键点
        if len(key_points) >= 3:
            confidence += 0.15
        elif len(key_points) == 0:
            confidence -= 0.2
        
        # 有关键词
        if len(keywords) >= 10:
            confidence += 0.15
        
        return min(max(confidence, 0), 1)


# 便捷函数
def summarize_document(
    content: str,
    summary_type: SummaryType = SummaryType.DETAILED,
    domain: Optional[str] = None
) -> DocumentSummary:
    """
    对文档进行总结
    
    Args:
        content: 文档内容
        summary_type: 总结类型
        domain: 领域
        
    Returns:
        DocumentSummary: 总结结果
    """
    summarizer = DocumentSummarizer()
    return summarizer.summarize(content, summary_type, domain)


if __name__ == "__main__":
    # 测试
    test_content = """
    社会学是一门研究社会关系、社会结构和社会变迁的学科。其起源可以追溯到19世纪中叶，当时孔德、涂尔干等学者开始系统地研究社会现象。
    
    在发展过程中，社会学经历了从经典社会学到现代社会学的演变。20世纪初，社会学传入中国，经过本土化发展，形成了具有中国特色的社会学理论体系。
    
    当前，社会学在中国的发展势头良好。随着社会治理现代化的推进，社会学人才需求旺盛。毕业生可在政府部门、研究机构、企业等从事相关工作。
    
    未来，社会学的发展趋势主要包括：数字社会学、人口老龄化研究、城乡发展等方向。同时，社会工作、社会政策等领域的人才需求也在增加。
    """
    
    summary = summarize_document(test_content, SummaryType.DETAILED, "专业")
    
    print(f"总结类型: {summary.summary_type.value}")
    print(f"\n总结内容:\n{summary.summary}")
    print(f"\n关键点 ({len(summary.key_points)}个):")
    for i, point in enumerate(summary.key_points[:5], 1):
        print(f"  {i}. {point[:80]}...")
    print(f"\n关键词: {summary.keywords[:10]}")
    print(f"\n统计信息: {summary.statistics}")
    print(f"置信度: {summary.confidence:.2f}")
