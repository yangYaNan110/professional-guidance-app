---
name: frontend-miniprogram
description: 微信小程序开发
license: MIT
compatibility: opencode
---

## 我做什么

负责专业选择指导应用微信小程序的开发，实现轻量化的移动端体验。

## 使用场景

- 小程序功能开发
- 适配微信生态

## 输入格式

```json
{
  "feature": "功能描述",
  "requirements": [],
  "wechat_api_usage": []
}
```

## 输出格式

```json
{
  "files_created": [],
  "files_modified": [],
  "pages_defined": [],
  "components_defined": [],
  "api_integrations": []
}
```

## 执行流程

1. 分析小程序需求
2. 设计页面结构
3. 实现页面逻辑
4. 集成微信API
5. 处理数据接口
6. 优化性能（分包加载）

## 注意事项

- 遵循小程序开发规范
- 控制包大小（2MB限制）
- 优化启动速度
- 处理登录鉴权（微信登录）

## 推荐模型

- 代码生成：`anthropic/claude-3-5-sonnet-20241022`
