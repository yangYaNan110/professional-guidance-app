---
name: backend-plan
description: 后端整体规划，包括技术选型、架构设计、目录结构
license: MIT
compatibility: opencode
---

## 我做什么

制定后端技术方案，包括微服务架构设计、数据库设计、API设计等。

## 使用场景

- 后端需求分析完成后
- 技术方案评审前

## 输入格式

```json
{
  "requirements": {},
  "service_architecture": {},
  "performance_benchmarks": {}
}
```

## 输出格式

```json
{
  "tech_stack": {
    "frameworks": [],
    "databases": [],
    "caching": "",
    "messaging": ""
  },
  "service_design": {},
  "database_schema": {},
  "api_design": {
    "restful": [],
    "websocket": []
  },
  "directory_structure": {},
  "security_design": {},
  "deployment_architecture": {}
}
```

## 执行流程

1. 选择技术栈
2. 设计微服务架构
3. 设计数据库模型
4. 设计API接口
5. 设计安全策略
6. 规划目录结构

## 注意事项

- 确保API设计一致性
- 做好错误处理设计
- 考虑日志和监控
- 预留扩展接口

## 推荐模型

- 架构设计：`anthropic/claude-3-5-sonnet-20241022`
