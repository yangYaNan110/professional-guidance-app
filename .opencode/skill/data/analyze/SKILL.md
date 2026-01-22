---
name: data-analyze
description: 分析数据需求和技术需求
license: MIT
compatibility: opencode
---

## 我做什么

分析数据采集、处理、分析的需求，评估数据质量要求和合规风险。

## 使用场景

- 项目启动时数据需求分析
- 新增数据功能时评估

## 输入格式

```json
{
  "data_sources": [],
  "data_requirements": [],
  "quality_requirements": {},
  "compliance_requirements": []
}
```

## 输出格式

```json
{
  "data_sources_identified": [],
  "data_quality_requirements": {},
  "processing_pipeline": {},
  "storage_requirements": {},
  "compliance_checklist": [],
  "risk_assessment": {}
}
```

## 执行流程

1. 识别数据来源
2. 评估数据质量要求
3. 设计处理流程
4. 评估存储需求
5. 检查合规要求
6. 评估风险

## 注意事项

- 遵守数据爬取法规
- 保护用户隐私
- 确保数据时效性
- 评估存储成本

## 推荐模型

- 数据分析：`anthropic/claude-3-5-sonnet-20241022`
