---
name: ai-chat
description: 对话引擎开发，包括意图识别、情感分析、多轮对话
license: MIT
compatibility: opencode
---

## 我做什么

负责对话引擎的开发，包括意图识别、情感分析、上下文管理、回复生成等核心功能。

## 使用场景

- 对话功能开发
- 意图识别实现
- 情感分析集成

## 输入格式

```json
{
  "dialogue_scenario": "对话场景描述",
  "intents": [],
  "response_requirements": {},
  "context_management": {}
}
```

## 输出格式

```json
{
  "files_created": [],
  "intent_classifier": {},
  "sentiment_analyzer": {},
  "dialogue_manager": {},
  "response_generator": {},
  "context_store": {},
  "tests_written": []
}
```

## 执行流程

1. 设计意图分类体系
2. 实现意图识别模型
3. 实现情感分析
4. 实现对话管理器
5. 实现回复生成
6. 实现上下文存储
7. 编写测试用例

## 注意事项

- 优化对话流畅度
- 处理歧义意图
- 实现情感共鸣
- 做好fallback策略

## 推荐模型

- 对话系统：`anthropic/claude-opus-4-20240307`
