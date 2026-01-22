---
name: backend-analyze
description: 分析后端功能需求和技术需求
license: MIT
compatibility: opencode
---

## 我做什么

分析后端的功能需求和技术需求，评估性能要求和扩展性需求，识别后端特有的风险。

## 使用场景

- 项目启动时后端需求分析
- 新增服务时后端评估

## 输入格式

```json
{
  "requirements": [],
  "services_needed": [],
  "performance_requirements": {},
  "security_requirements": []
}
```

## 输出格式

```json
{
  "functional_requirements": [],
  "technical_requirements": [],
  "service_architecture": {},
  "database_requirements": [],
  "api_design_needs": [],
  "performance_benchmarks": {},
  "security_considerations": [],
  "complexity_assessment": ""
}
```

## 执行流程

1. 分析功能需求
2. 评估性能要求
3. 设计服务划分
4. 评估数据库需求
5. 识别安全需求
6. 产出技术建议

## 注意事项

- 考虑微服务拆分合理性
- 评估数据一致性要求
- 识别第三方服务依赖
- 考虑扩展性需求

## 推荐模型

- 后端分析：`anthropic/claude-3-5-sonnet-20241022`
