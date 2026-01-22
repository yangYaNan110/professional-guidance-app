---
name: coordinator-analyze
description: 分析项目需求和任务，识别核心功能和关键路径
license: MIT
compatibility: opencode
---

## 我做什么

分析专业选择指导应用的项目需求，识别核心功能和关键路径，评估项目复杂度和风险，为后续任务分配提供依据。

## 使用场景

- 项目启动时进行需求分析
- 需求变更时重新评估
- 任务拆分前的前置分析

## 输入格式

```json
{
  "project_description": "项目描述文本（专业选择指导）",
  "requirements": ["需求1", "需求2", "需求3"],
  "context": {
    "existing_artifacts": [],
    "constraints": []
  }
}
```

## 输出格式

```json
{
  "functional_requirements": [],
  "technical_requirements": [],
  "core_features": [],
  "key_paths": [],
  "complexity_assessment": {
    "overall": "high/medium/low",
    "risks": [],
    "dependencies": []
  },
  "task_breakdown_suggestion": []
}
```

## 执行流程

1. 阅读和分析项目描述（专业选择指导）
2. 识别核心功能模块（语音交互、专业信息爬取、推荐分析等）
3. 评估技术复杂度（AI对话、语音处理、大数据）
4. 识别关键路径和依赖
5. 评估潜在风险（高考季高并发、数据时效性）
6. 产出任务拆分建议

## 注意事项

- 关注核心功能，区分优先级（语音交互、推荐算法）
- 识别技术风险和业务风险（学生隐私、数据准确）
- 评估团队能力和时间约束（16周）
- 识别外部依赖和集成点（OpenAI、阳光高考等）

## 推荐模型

- 需求分析：`anthropic/claude-sonnet-4-20250514`
