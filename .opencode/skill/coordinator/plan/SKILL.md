---
name: coordinator-plan
description: 制定项目整体开发计划，包括阶段划分、Agent分工、里程碑
license: MIT
compatibility: opencode
---

## 我做什么

根据需求分析结果，制定完整的专业选择指导应用开发计划，包括开发阶段划分、Agent任务分配、里程碑设定和依赖关系管理。

## 使用场景

- 需求分析完成后制定计划
- 项目进度调整时更新计划
- 新增功能时重新规划

## 输入格式

```json
{
  "requirements": {},
  "complexity_assessment": {},
  "task_breakdown": [],
  "project_context": {
    "timeline": "16周",
    "team_size": 6,
    "technologies": []
  }
}
```

## 输出格式

```json
{
  "development_phases": [
    {
      "phase": 1,
      "name": "基础设施",
      "duration": "2周",
      "tasks": [],
      "deliverables": [],
      "dependencies": []
    }
  ],
  "agent_assignments": {
    "frontend": [],
    "backend": [],
    "ai-ml": [],
    "data": [],
    "devops": []
  },
  "milestones": [
    {
      "name": "基础设施就绪",
      "week": 2,
      "deliverables": []
    }
  ],
  "skill_schedule": [],
  "risk_mitigation": []
}
```

## 执行流程

1. 根据需求确定开发阶段（5阶段16周）
2. 划分每个阶段的任务
3. 分配任务给对应Agent（Frontend/Backend/AI/ML/Data/DevOps）
4. 设定里程碑和交付物（高考季前上线）
5. 规划Skill执行顺序
6. 制定风险缓解策略

## 注意事项

- 考虑任务之间的依赖关系
- 合理安排并行和串行任务
- 预留缓冲时间应对风险（数据爬取延迟）
- 确保里程碑可测量（高考季前完成）

## 推荐模型

- 规划决策：`anthropic/claude-sonnet-4-20250514`
