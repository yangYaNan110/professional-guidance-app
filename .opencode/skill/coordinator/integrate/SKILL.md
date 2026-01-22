---
name: coordinator-integrate
description: 整合各Agent的工作成果，确保代码质量和一致性
license: MIT
compatibility: opencode
---

## 我做什么

整合各Agent提交的代码和文档，进行代码审查，确保整体项目的一致性和质量，生成可部署的最终产物。

## 使用场景

- 各Agent完成阶段任务后
- 代码合并前进行审查
- 项目发布前最终整合

## 输入格式

```json
{
  "agent_outputs": [
    {
      "agent": "frontend",
      "status": "completed",
      "files_created": [],
      "files_modified": [],
      "summary": ""
    }
  ],
  "integration_type": "phase/complete"
}
```

## 输出格式

```json
{
  "integration_status": "success/partial/failed",
  "files_integrated": [],
  "conflicts_resolved": [],
  "code_quality_report": {
    "issues_found": [],
    "issues_fixed": [],
    "coverage": 0
  },
  "consistency_checks": [],
  "next_steps": [],
  "deployment_package": {
    "ready": true,
    "artifacts": []
  }
}
```

## 执行流程

1. 收集各Agent的输出
2. 检查代码冲突和重复
3. 执行代码质量检查
4. 修复发现的问题
5. 更新依赖和配置
6. 生成部署包

## 注意事项

- 确保代码风格一致性
- 检查接口兼容性（API规范）
- 验证功能完整性（语音对话、专业推荐）
- 记录发现的问题

## 推荐模型

- 代码审查：`anthropic/claude-sonnet-4-20250514`
