---
name: ai-analyze
description: 分析AI功能需求和技术需求
license: MIT
compatibility: opencode
---

## 我做什么

分析AI相关功能需求，评估模型选择和性能要求，识别AI特有的风险和伦理问题。

## 使用场景

- 项目启动时AI需求分析
- 新增AI功能时评估

## 输入格式

```json
{
  "requirements": [],
  "ai_features": [],
  "performance_requirements": {},
  "ethical_considerations": []
}
```

## 输出格式

```json
{
  "ai_functional_requirements": [],
  "model_requirements": {},
  "performance_metrics": {},
  "data_requirements": [],
  "ethical_risks": [],
  "model_selection_recommendation": {},
  "cost_estimation": {}
}
```

## 执行流程

1. 分析AI功能需求
2. 评估模型需求
3. 确定性能指标
4. 评估数据需求
5. 识别伦理风险
6. 推荐模型方案

## 注意事项

- 评估模型成本
- 考虑响应延迟
- 评估数据隐私
- 确保输出安全性

## 推荐模型

- AI分析：`anthropic/claude-opus-4-20240307`
