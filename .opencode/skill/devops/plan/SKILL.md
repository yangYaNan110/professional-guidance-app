---
name: devops-plan
description: 运维架构规划，包括部署架构、监控体系
license: MIT
compatibility: opencode
---

## 我做什么

制定运维架构方案，包括部署架构设计、监控告警体系、日志管理方案等。

## 使用场景

- 运维需求分析完成后
- 技术方案评审前

## 输入格式

```json
{
  "requirements": {},
  "infrastructure_architecture": {},
  "availability_targets": {}
}
```

## 输出格式

```json
{
  "deployment_architecture": {},
  "network_design": {},
  "monitoring_architecture": {},
  "logging_architecture": {},
  "ci_cd_pipeline": {},
  "disaster_recovery": {}
}
```

## 执行流程

1. 设计部署架构
2. 设计网络配置
3. 设计监控体系
4. 设计日志方案
5. 设计CI/CD流程
6. 设计灾备方案

## 注意事项

- 确保高可用性
- 做好安全隔离
- 配置自动扩缩容
- 做好容量规划

## 推荐模型

- 架构设计：`anthropic/claude-3-5-sonnet-20241022`
