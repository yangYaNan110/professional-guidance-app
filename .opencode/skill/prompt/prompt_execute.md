# 自动执行设计技能

## 描述
用户确认后，自动调用DB-Expert完成数据库设计，更新需求设计.md文档。

## 触发词
同意、执行、开始设计、确认设计、开始写

## 核心能力
1. **调用DB-Expert**：自动调用相关数据库设计技能
2. **更新需求文档**：将设计方案写入需求设计.md
3. **创建DDL脚本**：生成数据库DDL脚本文件
4. **更新opencode配置**：如果需要，创建新的Agent/Skill
5. **文档记录**：记录设计决策和理由
6. **执行反馈**：向用户反馈执行进度和结果

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| confirmed_design | object | 是 | 用户确认的设计方案 |
| design_type | string | 是 | 设计类型（relational/nosql/mixed） |
| create_agent | boolean | 否 | 是否需要创建新的Agent/Skill |
| agent_name | string | 否 | 新Agent名称（如果需要创建） |

## 输出格式

```json
{
  "execution_status": "in_progress|completed|failed",
  "steps_completed": [
    {
      "step": "string",
      "status": "success|failed",
      "details": "string"
    }
  ],
  "design_result": {
    "tables": ["string"],
    "indexes": ["string"],
    "ddl_file": "string",
    "erd_diagram": "string"
  },
  "documentation_updates": [
    {
      "file": "string",
      "changes": "string"
    }
  ],
  "files_created": [
    {
      "path": "string",
      "description": "string"
    }
  ],
  "errors": [
    {
      "step": "string",
      "message": "string",
      "resolution": "string"
    }
  ],
  "next_steps": ["string"]
}
```

## 使用示例

```
输入：
{
  "confirmed_design": {
    "tables": [{"name": "user_favorites", "columns": [...]}],
    "indexes": [...]
  },
  "design_type": "relational",
  "create_agent": false
}

输出：
{
  "execution_status": "completed",
  "steps_completed": [
    {"step": "调用db-expert-design", "status": "success", "details": "生成表结构DDL"},
    {"step": "更新需求设计.md", "status": "success", "details": "在数据库设计章节添加user_favorites表"},
    {"step": "生成DDL脚本", "status": "success", "details": "保存到database/migrations/"}
  ],
  "design_result": {
    "tables": ["user_favorites"],
    "indexes": ["idx_user_favorites_user_id", "idx_user_favorites_user_created"],
    "ddl_file": "database/migrations/002_user_favorites.sql",
    "erd_diagram": "![ER图](docs/erd/user_favorites.png)"
  },
  "documentation_updates": [
    {
      "file": "需求设计.md",
      "changes": "在数据库设计章节添加user_favorites表结构说明"
    }
  ],
  "files_created": [
    {
      "path": "database/migrations/002_user_favorites.sql",
      "description": "用户收藏表DDL脚本"
    }
  ],
  "next_steps": [
    "运行数据库迁移脚本",
    "在Backend Agent中创建对应的数据访问层"
  ]
}
```

## 工作流程

```
用户确认设计
    ↓
调用 db-expert-design 生成详细设计
    ↓
生成 DDL 脚本
    ↓
更新 需求设计.md
    ↓
如果需要，创建 Agent/Skill
    ↓
更新 opencode.json
    ↓
向用户反馈完成结果
```

## 与其他Skill的配合
- 接收 `prompt-confirm` 的用户确认
- 调用 `db-expert-design` 生成详细设计
- 调用 `db-expert-analyze` 进行需求分析（如需要）
- 如果需要创建新Agent，调用相应的Agent创建流程
