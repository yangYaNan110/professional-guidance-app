---
name: frontend-plan
description: 前端整体规划，包括技术选型、架构设计、目录结构
license: MIT
compatibility: opencode
---

## 我做什么

制定前端技术方案，包括框架选型、组件架构、状态管理、目录结构等设计工作。

## 使用场景

- 前端需求分析完成后
- 技术方案评审前

## 输入格式

```json
{
  "requirements": {},
  "technical_requirements": {},
  "platforms": []
}
```

## 输出格式

```json
{
  "tech_stack": {
    "web": {},
    "mobile": {},
    "miniprogram": {}
  },
  "architecture": {
    "components": [],
    "state_management": "",
    "routing": ""
  },
  "directory_structure": {},
  "coding_standards": [],
  "dependencies": [],
  "compatibility_strategy": {}
}
```

## 执行流程

1. 评估各平台技术选型
2. 设计组件架构（语音交互、专业卡片、图表）
3. 选择状态管理方案（Zustand）
4. 规划目录结构
5. 定义编码规范
6. 制定兼容性策略（多端适配）

## 注意事项

- 确保多端代码复用性
- 统一UI组件风格（专业选择主题）
- 规划好语音交互模块
- 考虑离线支持（学生档案缓存）

## 推荐模型

- 架构设计：`anthropic/claude-3-5-sonnet-20241022`
