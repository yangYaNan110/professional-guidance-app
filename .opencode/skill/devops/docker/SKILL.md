---
name: devops-docker
description: Docker容器化配置，包括Dockerfile和docker-compose
license: MIT
compatibility: opencode
---

## 我做什么

负责Docker容器化配置，包括各服务的Dockerfile编写、docker-compose配置优化。

## 使用场景

- 服务容器化配置
- 开发环境搭建
- 镜像优化

## 输入格式

```json
{
  "service": {
    "name": "服务名",
    "type": "frontend/backend/ai/data",
    "dependencies": [],
    "ports": []
  }
}
```

## 输出格式

```json
{
  "dockerfile": "",
  "docker_compose_updates": [],
  "env_templates": [],
  "optimization_suggestions": [],
  "health_checks": []
}
```

## 执行流程

1. 分析服务依赖
2. 编写Dockerfile
3. 更新docker-compose
4. 配置环境变量
5. 添加健康检查
6. 优化镜像大小

## 注意事项

- 减小镜像体积
- 做好分层构建
- 配置健康检查
- 敏感信息处理

## 推荐模型

- Docker配置：`anthropic/claude-3-5-sonnet-20241022`
