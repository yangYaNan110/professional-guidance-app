# 数据模型设计技能

## 描述
根据分析结果，为各业务设计合适的数据表结构、索引策略和存储方案。

## 触发词
设计数据模型、设计表结构、设计数据库、设计存储方案

## 核心能力
1. **表结构设计**：为每个业务设计满足3NF的表结构
2. **索引设计**：设计单列索引和复合索引
3. **关联设计**：设计表之间的关联关系
4. **存储方案**：确定使用关系型还是NoSQL存储
5. **DDL生成**：生成PostgreSQL/MySQL的DDL语句
6. **ER图生成**：生成实体关系图（Mermaid格式）

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| module_analysis | object | 是 | 来自doc-generator-analyze的分析结果 |
| database_type | string | 否 | 数据库类型（默认postgresql） |
| table_prefix | string | 否 | 表前缀（默认"app_"） |

## 输出格式

```json
{
  "tables": [
    {
      "module": "string",
      "name": "string",
      "description": "string",
      "storage_type": "relational|nosql|cache",
      "columns": [
        {
          "name": "string",
          "type": "string",
          "constraints": ["string"],
          "description": "string",
          "indexed": boolean
        }
      ],
      "indexes": [
        {
          "columns": ["string"],
          "type": "string",
          "unique": boolean,
          "reason": "string"
        }
      ],
      "relationships": [
        {
          "to_table": "string",
          "type": "one-to-one|one-to-many|many-to-many",
          "foreign_key": "string"
        }
      ]
    }
  ],
  "erd_diagram": "string",
  "ddl_statements": "string",
  "design_notes": ["string"]
}
```

## 使用示例

```
输入：
{
  "module_analysis": {
    "modules": [
      {
        "name": "专业行情数据",
        "data_types": ["就业率", "平均薪资", "热度指数"]
      }
    ]
  },
  "database_type": "postgresql",
  "table_prefix": "app_"
}

输出：
{
  "tables": [
    {
      "module": "专业行情数据",
      "name": "app_major_market_data",
      "description": "专业行情数据表",
      "storage_type": "relational",
      "columns": [
        {"name": "id", "type": "BIGSERIAL", "constraints": ["PRIMARY KEY"]},
        {"name": "major_name", "type": "VARCHAR(200)", "constraints": ["NOT NULL"]},
        {"name": "category", "type": "VARCHAR(100)", "constraints": []},
        {"name": "employment_rate", "type": "DECIMAL(5,2)", "constraints": []},
        {"name": "avg_salary", "type": "VARCHAR(100)", "constraints": []},
        {"name": "heat_index", "type": "DECIMAL(5,2)", "constraints": []},
        {"name": "source_url", "type": "VARCHAR(1000)", "constraints": ["UNIQUE"]},
        {"name": "crawled_at", "type": "TIMESTAMP", "constraints": ["DEFAULT NOW()"]}
      ],
      "indexes": [
        {"columns": ["major_name"], "type": "btree", "reason": "按专业名称查询"},
        {"columns": ["category"], "type": "btree", "reason": "按学科门类筛选"},
        {"columns": ["crawled_at DESC"], "type": "btree", "reason": "按时间排序"}
      ]
    }
  ],
  "erd_diagram": "```mermaid\\nerDiagram\\n  app_major_market_data {\\n    BIGSERIAL id PK\\n    VARCHAR major_name\\n    VARCHAR category\\n  }\\n```",
  "ddl_statements": "CREATE TABLE app_major_market_data (...)"
}
```

## 与其他Agent的配合

**可调用DB-Expert Agent**：
- 用于复杂表结构设计
- 用于索引优化分析
- 用于查询性能评估
- 用于NoSQL数据模型设计

**调用方式**：
```python
# 使用Task工具调用DB-Expert
task(
  subagent_type="db-expert",
  command="design_table",
  prompt="请为以下业务设计数据表：\n业务：专业行情数据\n需要存储：专业名称、学科门类、就业率、薪资、热度和URL\n请生成完整的表结构和DDL"
)
```

## 与其他Skill的配合
- 接收 `doc-generator-analyze` 的分析结果
- 输出给 `doc-generator-confirm` 向用户确认
