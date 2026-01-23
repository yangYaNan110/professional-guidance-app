# 数据库结构设计技能

## 描述
根据需求分析结果，设计关系型数据库的表结构、字段定义、索引策略、外键关系和约束条件。

## 触发词
设计表、设计数据库、设计结构、设计Schema、创建表

## 核心能力
1. **表结构设计**：根据实体设计满足3NF的表结构
2. **字段定义**：选择合适的数据类型，设置字段长度和精度
3. **主键设计**：设计主键策略（自增、UUID、业务键）
4. **索引设计**：设计单列索引、复合索引、唯一索引
5. **外键关系**：设计表之间的关联关系
6. **约束设计**：设计CHECK约束、DEFAULT值
7. **DDL生成**：生成PostgreSQL/MySQL的DDL语句
8. **ER图生成**：生成实体关系图

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| entities | array | 是 | 实体列表，来自db-expert-analyze |
| relationships | array | 是 | 关系列表，来自db-expert-analyze |
| database_type | string | 否 | 数据库类型（postgresql/mysql），默认postgresql |
| table_prefix | string | 否 | 表前缀，如"app_" |

## 输出格式

```json
{
  "tables": [
    {
      "name": "string",
      "comment": "string",
      "columns": [
        {
          "name": "string",
          "type": "string",
          "nullable": boolean,
          "default": "string",
          "primary_key": boolean,
          "unique": boolean,
          "comment": "string"
        }
      ],
      "primary_key": ["string"],
      "indexes": [
        {
          "columns": ["string"],
          "type": "btree|hash|gist",
          "unique": boolean,
          "comment": "string"
        }
      ],
      "foreign_keys": [
        {
          "columns": ["string"],
          "references_table": "string",
          "references_columns": ["string"],
          "on_delete": "cascade|set null|restrict"
        }
      ]
    }
  ],
  "erd_diagram": "mermaid格式的ER图",
  "ddl_statements": "string",
  "design_notes": "string"
}
```

## 使用示例

```
输入：
{
  "entities": [{"name": "用户", "attributes": [...]}],
  "relationships": [{"from": "用户", "to": "角色", "type": "many-to-many"}],
  "database_type": "postgresql"
}

输出：
{
  "tables": [
    {
      "name": "app_users",
      "comment": "用户表",
      "columns": [
        {"name": "id", "type": "BIGSERIAL", "primary_key": true},
        {"name": "username", "type": "VARCHAR(50)", "nullable": false, "unique": true},
        {"name": "email", "type": "VARCHAR(255)", "nullable": false, "unique": true}
      ]
    }
  ],
  "ddl_statements": "CREATE TABLE app_users (...)"
}
```

## 与其他Skill的配合
- 接收 `db-expert-analyze` 的输出
- 输出给 `db-expert-optimize` 进行索引优化
- 输出给 `db-expert-migrate` 生成迁移脚本
