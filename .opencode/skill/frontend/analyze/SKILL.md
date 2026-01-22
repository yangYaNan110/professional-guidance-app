---
name: frontend-analyze
description: 分析前端功能需求和技术需求
license: MIT
compatibility: opencode
---

## 我做什么

分析前端的功能需求和技术需求，评估实现复杂度，识别前端特有的风险和依赖。

## 使用场景

- 项目启动时前端需求分析
- 新增功能时前端评估

## 输入格式

```json
{
  "requirements": [],
  "platforms": ["web", "ios", "android", "miniprogram"],
  "features": []
}
```

## 输出格式

```json
{
  "functional_requirements": [],
  "technical_requirements": [],
  "component_analysis": [],
  "state_management_needs": [],
  "api_dependencies": [],
  "complexity_assessment": "high/medium/low",
  "risks": [],
  "tech_stack_recommendation": {}
}
```

## 执行流程

1. 分析功能需求（语音交互、专业展示、图表可视化）
2. 识别UI组件需求（语音按钮、图表组件、专业卡片）
3. 评估状态管理复杂度（用户档案、对话历史）
4. 识别API依赖（语音服务、推荐服务）
5. 评估跨平台兼容性（Web/移动端/小程序）
6. 产出技术建议

## 注意事项

- 考虑多端适配需求
- 评估语音交互的特殊需求（Web Speech API）
- 关注性能要求（图表渲染、语音流）
- 考虑无障碍需求（字体大小、语音播放）

## 推荐模型

- 前端分析：`anthropic/claude-3-5-sonnet-20241022`
