# doc-analyze Skill - 文档智能分析

## 功能描述

对文档进行深度分析，提取文档结构、关键实体、主题信息和语义特征，支持多种分析维度和输出格式。

## 核心能力

1. 分析文档结构和层次关系
2. 提取关键实体（人名、地名、机构名、时间等）
3. 识别文档主题和关键词
4. 分析文档语义和情感倾向
5. 提取文档之间的关联关系
6. 生成文档结构化表示

---

## 分析维度

| 分析类型 | 说明 | 适用场景 |
|---------|------|---------|
| `STRUCTURE` | 分析文档层次结构和章节关系 | 论文、报告分析 |
| `ENTITY` | 提取文档中的命名实体 | 信息抽取、知识图谱 |
| `TOPIC` | 识别文档主题和关键词 | 主题建模、文档分类 |
| `SENTIMENT` | 分析文档情感倾向 | 舆情分析、评论分析 |
| `RELATION` | 提取实体之间的关系 | 知识抽取、关系推理 |
| `FULL` | 完整分析（包含所有维度） | 综合文档分析 |

---

## 文档类型支持

| 文档类型 | 特点 |
|---------|------|
| `ACADEMIC` | 学术论文，支持引用分析 |
| `REPORT` | 分析报告，支持数据提取 |
| `NEWS` | 新闻资讯，支持时效性分析 |
| `LEGAL` | 法律文档，支持条款解析 |
| `TECHNICAL` | 技术文档，支持代码注释 |
| `GENERAL` | 通用文档 |

---

## 实体提取规范

### 1. 实体类型

| 实体类型 | 说明 | 示例 |
|---------|------|------|
| `PERSON` | 人名 | 张三、李教授 |
| `LOCATION` | 地名 | 北京、硅谷 |
| `ORGANIZATION` | 机构名 | 清华大学、Google |
| `TIME` | 时间 | 2024年、3年前 |
| `PRODUCT` | 产品名 | GPT-4、iPhone |
| `CONCEPT` | 概念名 | 人工智能、区块链 |
| `EVENT` | 事件名 | 冬奥会、双十一 |

### 2. 实体标注要求

- ✅ **准确标注**：确保实体边界准确，不遗漏不冗余
- ✅ **类型一致**：同一实体在不同上下文保持类型一致
- ✅ **消歧处理**：同名实体通过上下文区分

---

## 主题识别规范

### 1. 关键词提取

- ✅ 提取**3-10个核心关键词**
- ✅ 关键词要能**准确反映文档主题**
- ✅ 包含**高频词**和**重要概念**

### 2. 主题建模

- ✅ 自动识别文档所属主题类别
- ✅ 计算主题相关度概率分布
- ✅ 支持多主题文档识别

---

## 文档结构分析

### 1. 层次结构

- ✅ 识别文档的标题层级（H1-H6）
- ✅ 建立章节之间的父子关系
- ✅ 提取每个章节的核心内容

### 2. 逻辑关系

- ✅ 识别因果关系、递进关系、并列关系
- ✅ 标注关键论点和论据
- ✅ 提取文档的核心结论

---

## 输出格式

### 完整分析结果

```json
{
  "document_id": "doc_123456",
  "document_type": "ACADEMIC",
  "structure": {
    "title": "文档标题",
    "sections": [
      {
        "level": 1,
        "title": "第一章 引言",
        "content_summary": "本章介绍了研究背景...",
        "subsections": []
      }
    ]
  },
  "entities": [
    {
      "text": "张三",
      "type": "PERSON",
      "position": {"start": 100, "end": 102},
      "frequency": 5
    }
  ],
  "keywords": ["人工智能", "深度学习", "神经网络"],
  "topics": [
    {"topic": "机器学习", "probability": 0.85},
    {"topic": "计算机视觉", "probability": 0.65}
  ],
  "sentiment": {
    "overall": "positive",
    "score": 0.75
  },
  "relations": [
    {
      "subject": "张三",
      "predicate": "提出",
      "object": "新算法"
    }
  ],
  "summary": "本文主要介绍了..."
}
```

### 实体提取结果

```json
{
  "entities": [
    {
      "text": "OpenAI",
      "type": "ORGANIZATION",
      "mentions": [
        {"position": {"start": 50, "end": 55}, "context": "OpenAI发布..."}
      ]
    }
  ],
  "statistics": {
    "total_entities": 45,
    "by_type": {
      "PERSON": 12,
      "ORGANIZATION": 15,
      "LOCATION": 8,
      "TIME": 10
    }
  }
}
```

---

## 使用示例

```python
from doc_analyze import DocumentAnalyzer, AnalysisType, DocumentType

analyzer = DocumentAnalyzer()

# 完整分析
result = analyzer.analyze(
    content=document_text,
    document_type=DocumentType.ACADEMIC,
    analysis_type=AnalysisType.FULL
)

print(result.structure)
print(result.entities)
print(result.keywords)

# 只提取实体
entity_result = analyzer.analyze(
    content=document_text,
    analysis_type=AnalysisType.ENTITY
)

print(entity_result.entities)
```

---

## 与其他Skill的配合

- **doc-crawler**：先使用文档爬取Skill获取文档内容
- **doc-summarize**：分析结果可进一步使用文档总结Skill生成摘要
- **doc-generate**：分析结果可作为文档生成的输入
