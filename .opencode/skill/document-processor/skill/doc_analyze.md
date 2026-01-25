# doc-analyze Skill - 文档智能分析

## 功能描述

对专业相关文档进行深度分析，提取关键信息、结构化内容和知识点。

## 触发词

分析、理解、提取、研究、解析

## 核心能力

1. 文档结构分析
2. 实体提取（人名、时间、事件）
3. 主题识别和分类
4. 关系抽取和知识图谱构建

---

## 分析维度

| 分析维度 | 说明 | 输出 |
|---------|------|------|
| 结构分析 | 识别标题、段落、列表 | 文档结构树 |
| 实体识别 | 提取人名、时间、地点 | 实体列表 |
| 主题分类 | 判断文档主题类别 | 分类标签 |
| 关键信息 | 提取核心观点和数据 | 关键点列表 |
| 情感分析 | 判断内容情感倾向 | 情感分数 |

---

## 专业文档分析要点

### 时间线分析

| 分析项 | 说明 |
|-------|------|
| 起源时间 | 专业诞生的时间和背景 |
| 发展阶段 | 关键发展阶段划分 |
| 重要节点 | 重大突破或转折点 |
| 当前状态 | 行业发展现状 |
| 未来趋势 | 预测发展方向 |

### 关键信息提取

| 信息类型 | 提取内容 |
|---------|---------|
| 人物 | 创始人、重要学者、代表人物 |
| 事件 | 重要会议、突破、争议 |
| 数据 | 市场规模、就业率、薪资 |
| 机构 | 重要组织、公司、研究机构 |

---

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| content | string | 是 | 文档内容 |
| major_name | string | 否 | 专业名称（用于上下文） |
| analysis_type | string | 否 | 分析类型（full/quick/custom） |

---

## 输出格式

```json
{
  "success": true,
  "structure": {
    "headings": ["起源", "发展", "现状", "未来"],
    "paragraphs_count": 15,
    "lists": []
  },
  "entities": {
    "people": ["约翰·麦卡锡", "图灵"],
    "dates": ["1956年", "2012年"],
    "places": ["美国", "英国"]
  },
  "topics": ["人工智能", "机器学习", "深度学习"],
  "key_info": [
    "1956年达特茅斯会议标志AI诞生",
    "2012年深度学习突破"
  ],
  "sentiment": {
    "score": 0.8,
    "label": "positive"
  },
  "timeline": {
    "origin": {"time": "1956年", "event": "达特茅斯会议"},
    "development": ["两次AI寒冬", "2012年深度学习突破"],
    "current": "大模型时代",
    "future": "通用人工智能"
  }
}
```

---

## 使用示例

```python
from doc_analyze import DocumentAnalyzer

analyzer = DocumentAnalyzer()

# 分析专业介绍文档
result = analyzer.analyze(
    content=document_text,
    major_name="人工智能",
    analysis_type="full"
)

print(result.success)
print(result.entities)
print(result.timeline)
```

---

## 与其他Skill的配合

- **doc-crawler**：分析爬取的原始内容
- **doc-summarize**：分析结果可作为总结的基础
- **doc-generate**：分析结果可用于内容生成
