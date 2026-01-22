---
name: data-analytics
description: 数据分析开发，包括趋势分析、洞察生成
license: MIT
compatibility: opencode
---

## 我做什么

负责数据分析模块的开发，包括就业趋势分析、薪资分析、行业洞察生成等。

## 使用场景

- 数据分析功能开发
- 新分析指标添加
- 分析报告生成

## 输入格式

```json
{
  "analysis_type": "趋势/对比/关联",
  "data_scope": {},
  "metrics": [],
  "output_format": "图表/报告/API"
}
```

## 输出格式

```json
{
  "files_created": [],
  "analytics_modules": [],
  "metrics_calculators": [],
  "insight_generators": [],
  "report_templates": [],
  "api_endpoints": [],
  "tests_written": []
}
```

## 执行流程

1. 设计分析指标
2. 实现计算逻辑
3. 实现洞察生成
4. 实现报告模板
5. 提供API接口
6. 编写测试用例

## 注意事项

- 确保计算准确性
- 优化计算性能
- 处理异常数据
- 保护敏感信息

## 推荐模型

- 数据分析：`anthropic/claude-3-5-sonnet-20241022`
