---
name: backend-api
description: RESTful API和WebSocket开发
license: MIT
compatibility: opencode
---

## 我做什么

负责后端API接口开发，包括RESTful API和WebSocket实时通信接口。

## 使用场景

- API接口开发
- WebSocket服务开发
- 接口文档编写

## 输入格式

```json
{
  "endpoint": "API端点描述",
  "method": "GET/POST/PUT/DELETE",
  "request_format": {},
  "response_format": {},
  "business_logic": ""
}
```

## 输出格式

```json
{
  "files_created": [],
  "files_modified": [],
  "api_endpoints": [],
  "websocket_events": [],
  "tests_written": [],
  "api_docs_updated": []
}
```

## 执行流程

1. 设计API接口
2. 实现路由和控制器
3. 实现业务逻辑
4. 实现数据验证
5. 添加错误处理
6. 编写测试用例
7. 生成API文档

## 注意事项

- 遵循RESTful规范
- 做好版本控制
- 实现认证授权
- 做好限流保护

## 推荐模型

- 代码生成：`anthropic/claude-3-5-sonnet-20241022`
