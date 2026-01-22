---
name: data-plan
description: 数据架构规划，包括存储设计、处理流程
license: MIT
compatibility: opencode
---

## 我做什么

制定数据架构方案，包括数据存储设计、处理流程、数据仓库等。

## 使用场景

- 数据需求分析完成后
- 技术方案评审前

## 输入格式

```json
{
  "requirements": {},
  "processing_pipeline": {},
  "storage_requirements": {}
}
```

## 输出格式

```json
{
  "storage_architecture": {},
  "data_models": {},
  "processing_pipeline": {},
  "etl_processes": [],
  "data_quality_checks": [],
  "backup_strategy": {}
}
```

## 执行流程

1. 设计存储架构
2. 设计数据模型
3. 设计处理流程
4. 设计ETL流程
5. 设计质量检查
6. 设计备份策略

## 注意事项

- 优化查询性能
- 做好数据分区
- 设计索引策略
- 预留扩展空间

## 推荐模型

- 架构设计：`anthropic/claude-3-5-sonnet-20241022`
