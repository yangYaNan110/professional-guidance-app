# doc-generate Skill - 文档智能生成

## 功能描述

根据主题、摘要或参考资料生成结构化、专业化的文档内容，支持多种文档类型和格式输出。

## 核心能力

1. 根据主题生成文档大纲
2. 基于摘要生成完整文档
3. 扩展文档内容
4. 生成多种格式文档
5. 保持文档风格一致性
6. 支持文档模板定制

---

## 文档类型支持

| 文档类型 | 说明 | 特点 |
|---------|------|------|
| `REPORT` | 分析报告 | 数据支撑、逻辑清晰 |
| `ARTICLE` | 文章 | 叙事性强、可读性高 |
| `PROPOSAL` | 提案 | 结构化、说服力强 |
| `MANUAL` | 手册 | 步骤详细、操作性强 |
| `ACADEMIC` | 学术文档 | 严谨规范、引用规范 |
| `BRIEFING` | 简报 | 简洁明了、重点突出 |
| `PRESENTATION` | 演示文稿 | 结构化、视觉化 |
| `OUTLINE` | 大纲 | 层次分明、要点突出 |

---

## 文档生成规范

### 1. 内容生成要求

- ✅ **主题明确**：紧扣输入主题，不偏离
- ✅ **结构清晰**：层次分明，逻辑连贯
- ✅ **内容充实**：有深度、有细节
- ✅ **语言规范**：语法正确，用词准确
- ✅ **风格一致**：保持文档整体风格统一

### 2. 文档结构

| 部分 | 说明 | 要求 |
|-----|------|------|
| 标题 | 文档标题 | 准确、简洁、有吸引力 |
| 摘要 | 内容概述 | 100-300字，概括核心内容 |
| 引言 | 背景介绍 | 引入话题，说明重要性 |
| 主体 | 核心内容 | 详细展开，逻辑清晰 |
| 结论 | 总结归纳 | 提炼要点，展望未来 |
| 附录 | 补充资料 | 参考资料，数据支撑 |

### 3. 内容深度

| 类型 | 字数范围 | 适用场景 |
|-----|---------|---------|
| `BRIEF` | 500-1000字 | 简要介绍、快速浏览 |
| `STANDARD` | 2000-5000字 | 标准文档、深度分析 |
| `COMPREHENSIVE` | 5000-10000字 | 完整报告、详细研究 |
| `EXTENDED` | 10000+字 | 专著、白皮书 |

---

## 生成模式

### 1. 大纲生成模式

```
生成流程：
1. 分析输入主题
2. 确定文档类型和结构
3. 生成多级标题
4. 为每个标题生成要点
5. 输出结构化大纲
```

### 2. 全文生成模式

```
生成流程：
1. 解析大纲结构
2. 逐章节生成内容
3. 保持章节连贯性
4. 添加过渡段落
5. 生成引言和结论
```

### 3. 扩展生成模式

```
生成流程：
1. 分析原文主题
2. 确定扩展方向
3. 补充相关内容
4. 深化原有观点
5. 保持原风格一致
```

---

## 专业文档生成规范

### 1. 学术文档

- ✅ 遵循学术写作规范
- ✅ 包含文献引用（占位符）
- ✅ 论证逻辑严谨
- ✅ 术语使用准确

### 2. 技术文档

- ✅ 技术细节准确
- ✅ 包含代码示例
- ✅ 步骤清晰可操作
- ✅ 版本和术语一致

### 3. 商业文档

- ✅ 数据支撑观点
- ✅ 逻辑清晰有说服力
- ✅ 格式规范专业
- ✅ 符合商业写作习惯

---

## 输出格式

### 文档生成结果

```json
{
  "document_id": "doc_gen_789",
  "title": "人工智能发展趋势分析",
  "document_type": "REPORT",
  "content": "# 人工智能发展趋势分析\n\n## 摘要\n...",
  "structure": {
    "title": "人工智能发展趋势分析",
    "outline": [
      {
        "level": 1,
        "title": "摘要",
        "content": "本文分析了..."
      },
      {
        "level": 1,
        "title": "引言",
        "content": "随着技术的快速发展..."
      }
    ]
  },
  "metadata": {
    "author": "AI Generator",
    "generated_at": "2024-01-16T10:00:00Z",
    "word_count": 3500,
    "section_count": 8
  }
}
```

### 大纲生成结果

```json
{
  "outline_id": "outline_456",
  "title": "主题：大语言模型应用",
  "document_type": "ARTICLE",
  "outline": [
    {
      "level": 1,
      "title": "引言",
      "key_points": ["背景介绍", "大语言模型定义", "本文目的"]
    },
    {
      "level": 1,
      "title": "技术原理",
      "key_points": ["Transformer架构", "预训练过程", "微调方法"]
    }
  ],
  "suggested_length": "STANDARD"
}
```

---

## 使用示例

```python
from doc_generate import DocumentGenerator, DocumentType, ContentDepth

generator = DocumentGenerator()

# 根据主题生成文档
result = generator.generate(
    topic="人工智能在医疗领域的应用",
    document_type=DocumentType.REPORT,
    depth=ContentDepth.COMPREHENSIVE,
    options={
        "include_abstract": True,
        "include_references": True,
        "style": "formal"
    }
)

print(result.title)
print(result.content)
print(result.structure)

# 生成大纲
outline = generator.generate_outline(
    topic="大语言模型发展趋势",
    document_type=DocumentType.ARTICLE,
    depth=ContentDepth.STANDARD,
    sections_count=5
)

print(outline.outline)

# 扩展现有内容
expanded = generator.expand(
    content="现有段落内容...",
    target_length=2000,
    style="professional"
)

print(expanded.content)
```

---

## 与其他Skill的配合

- **doc-crawler**：生成文档可使用文档爬取Skill获取参考资料
- **doc-analyze**：生成文档可进一步使用文档分析Skill验证质量
- **doc-summarize**：长文档可使用文档总结Skill生成摘要
