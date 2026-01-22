---
name: ai-plan
description: AI能力整体规划，包括模型选型、架构设计
license: MIT
compatibility: opencode
---

## 我做什么

制定AI能力技术方案，包括模型选型、服务架构、提示工程设计等。

## 使用场景

- AI需求分析完成后
- 技术方案评审前

## 输入格式

```json
{
  "requirements": {},
  "model_requirements": {},
  "performance_metrics": {}
}
```

## 输出格式

```json
{
  "model_selection": {
    "chat_model": "",
    "asr_model": "",
    "tts_model": "",
    "vector_store": ""
  },
  "service_architecture": {},
  "prompt_engineering_design": {},
  "data_pipeline": {},
  "evaluation_strategy": {},
  "deployment_strategy": {}
}
```

## 执行流程

1. 选择对话模型
2. 选择语音模型
3. 设计向量检索方案
4. 设计提示工程
5. 设计数据流程
6. 规划评估策略

## 注意事项

- 平衡成本和效果
- 考虑响应延迟
- 预留模型更新接口
- 设计fallback策略

## 推荐模型

- 架构设计：`anthropic/claude-opus-4-20240307`
