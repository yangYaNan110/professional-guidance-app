---
name: devops-ci
description: CI/CD流水线配置，包括自动化测试、构建、部署
license: MIT
compatibility: opencode
---

## 我做什么

负责CI/CD流水线配置，包括代码检查、自动化测试、构建部署等流程。

## 使用场景

- CI/CD流程配置
- 自动化测试配置
- 自动化部署配置

## 输入格式

```json
{
  "pipeline_config": {
    "trigger": "push/pull_request",
    "stages": [],
    "tests": [],
    "deploy_targets": []
  }
}
```

## 输出格式

```json
{
  "ci_pipeline": "",
  "cd_pipeline": "",
  "test_config": [],
  "notification_config": {},
  "rollback_strategy": {}
}
```

## 执行流程

1. 配置代码检查
2. 配置单元测试
3. 配置集成测试
4. 配置构建流程
5. 配置部署流程
6. 配置回滚策略

## 注意事项

- 确保测试覆盖率
- 优化构建速度
- 配置依赖缓存
- 做好权限控制

## 推荐模型

- CI/CD配置：`anthropic/claude-3-5-sonnet-20241022`
