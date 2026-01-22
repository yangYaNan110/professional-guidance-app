---
name: backend-gateway
description: API网关开发，包括路由、认证、限流
license: MIT
compatibility: opencode
---

## 我做什么

负责API网关的开发，包括请求路由、身份认证、访问授权、流量限制、服务熔断等功能。

## 使用场景

- 网关服务开发
- 认证授权实现
- 限流熔断配置

## 输入格式

```json
{
  "routing_rules": [],
  "authentication_required": [],
  "rate_limit_config": {},
  "circuit_breaker_config": {}
}
```

## 输出格式

```json
{
  "files_created": [],
  "gateway_config": {},
  "auth_middleware": [],
  "rate_limit_rules": [],
  "circuit_breaker_config": {},
  "tests_written": []
}
```

## 执行流程

1. 设计网关架构
2. 实现路由分发
3. 实现认证中间件
4. 实现授权逻辑
5. 配置限流规则
6. 配置熔断策略
7. 编写测试用例

## 注意事项

- 确保网关高可用
- 做好日志记录
- 合理配置限流阈值
- 定期更新认证策略

## 推荐模型

- 网关设计：`anthropic/claude-3-5-sonnet-20241022`
