# 数据迁移技能

## 描述
设计数据库迁移方案，编写迁移脚本，制定回滚策略，支持数据库版本管理和渐进式迁移。

## 触发词
数据迁移、数据库迁移、版本管理、回滚策略、迁移脚本

## 核心能力
1. **迁移方案设计**：设计数据迁移策略（全量/增量/双写）
2. **迁移脚本编写**：编写Alembic/Flyway迁移脚本
3. **数据转换**：设计数据清洗和转换规则
4. **回滚策略**：制定回滚方案，确保数据安全
5. **一致性保证**：设计数据一致性校验方案
6. **零停机迁移**：设计不停机迁移方案
7. **迁移测试**：设计迁移测试用例

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| source_schema | object | 是 | 源数据库结构 |
| target_schema | object | 是 | 目标数据库结构 |
| migration_type | string | 是 | 迁移类型（full-sync|incremental|zero-downtime） |
| data_volume | string | 是 | 数据量级 |
| downtime_allowed | boolean | 否 | 是否允许停机 |
| special_requirements | array | 否 | 特殊需求（加密、脱敏等） |

## 输出格式

```json
{
  "migration_plan": {
    "strategy": "string",
    "phases": [
      {
        "phase": "number",
        "description": "string",
        "actions": ["string"],
        "duration": "string",
        "rollback_action": "string"
      }
    ],
    "risk_assessment": {
      "risk_level": "low|medium|high",
      "mitigation": ["string"]
    }
  },
  "migration_scripts": [
    {
      "filename": "string",
      "description": "string",
      "sql_up": "string",
      "sql_down": "string"
    }
  ],
  "data_transformation": [
    {
      "source_field": "string",
      "target_field": "string",
      "transform_rule": "string"
    }
  ],
  "rollback_plan": {
    "trigger_conditions": ["string"],
    "steps": ["string"],
    "data_recovery": "string"
  },
  "validation": {
    "pre_migration_checks": ["string"],
    "post_migration_checks": ["string"],
    "consistency_verification": "string"
  },
  "timeline": {
    "estimated_duration": "string",
    "milestones": [
      {"time": "string", "checkpoint": "string"}
    ]
  }
}
```

## 使用示例

```
输入：
{
  "source_schema": {"tables": [...]},
  "target_schema": {"tables": [...]},
  "migration_type": "zero-downtime",
  "data_volume": "100万用户",
  "downtime_allowed": false
}

输出：
{
  "migration_plan": {
    "strategy": "双写+渐进式迁移",
    "phases": [
      {
        "phase": 1,
        "description": "创建新表结构",
        "sql_up": "CREATE TABLE users_v2 (...)",
        "duration": "10min"
      },
      {
        "phase": 2,
        "description": "双写阶段",
        "duration": "7天"
      }
    ]
  },
  "rollback_plan": {
    "trigger_conditions": ["错误率>1%", "数据不一致"],
    "steps": ["停止双写", "回写历史数据"]
  }
}
```

## 与其他Skill的配合
- 接收 `db-expert-design` 的输出，作为目标结构
- 与 `db-expert-optimize` 配合，优化迁移过程中的查询性能
