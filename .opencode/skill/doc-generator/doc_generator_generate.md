# 文档生成技能

## 描述
用户确认后，生成结构化的Markdown文档并保存到doc目录。

## 触发词
生成文档、确认生成、开始生成、写入文件

## 核心能力
1. **结构生成**：生成结构化的Markdown文档
2. **DDL整合**：将DDL脚本整合到文档中
3. **ER图整合**：将Mermaid图表整合到文档中
4. **文件写入**：将文档保存到doc目录
5. **版本管理**：记录文档版本和生成时间
6. **执行反馈**：向用户反馈生成结果

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| confirmed_design | object | 是 | 用户确认的设计方案 |
| document_title | string | 是 | 文档标题 |
| document_type | string | 是 | 文档类型（如"爬虫数据分析"） |
| output_path | string | 否 | 输出路径（默认doc/） |

## 输出格式

```json
{
  "execution_status": "in_progress|completed|failed",
  "document_info": {
    "title": "string",
    "file_path": "string",
    "version": "string",
    "created_at": "string"
  },
  "sections": [
    {
      "name": "string",
      "content": "string",
      "tables_included": "number",
      "ddl_included": boolean
    }
  ],
  "files_created": [
    {
      "path": "string",
      "description": "string",
      "size": "number"
    }
  ],
  "statistics": {
    "total_tables": "number",
    "total_indexes": "number",
    "total_ddl_lines": "number"
  },
  "next_steps": ["string"]
}
```

## 使用示例

```
输入：
{
  "confirmed_design": {
    "tables": [...],
    "ddl_statements": "..."
  },
  "document_title": "爬虫数据分析与数据模型设计",
  "document_type": "爬虫数据分析",
  "output_path": "doc/"
}

输出：
{
  "execution_status": "completed",
  "document_info": {
    "title": "爬虫数据分析与数据模型设计",
    "file_path": "doc/爬虫数据分析.md",
    "version": "1.0.0",
    "created_at": "2026-01-23 10:30:00"
  },
  "sections": [
    {"name": "一、模块分析", "content": "...", "tables_included": 0},
    {"name": "二、数据模型设计", "content": "...", "tables_included": 5, "ddl_included": true},
    {"name": "三、DDL脚本", "content": "...", "tables_included": 0}
  ],
  "files_created": [
    {
      "path": "doc/爬虫数据分析.md",
      "description": "爬虫数据分析与数据模型设计文档",
      "size": 15000
    }
  ],
  "statistics": {
    "total_tables": 5,
    "total_indexes": 12,
    "total_ddl_lines": 200
  },
  "next_steps": [
    "运行DDL脚本创建数据库表",
    "在Backend Agent中创建对应的数据访问层"
  ]
}
```

## 文档结构模板

```markdown
# {文档标题}

## 一、项目概述

## 二、模块分析

### 2.1 模块名称
- **描述**：...
- **数据类型**：...
- **数据来源**：...
- **更新频率**：...
- **数据量级**：...

## 三、数据模型设计

### 3.1 表结构设计

#### 表名：xxx

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 主键 |
| ... | ... | ... | ... |

### 3.2 索引设计

| 表名 | 索引字段 | 索引类型 | 说明 |
|-----|---------|---------|------|
| xxx | user_id | btree | 按用户查询 |

### 3.3 ER关系图

```mermaid
erDiagram
  users ||--o{ favorites : has
  ...
```

## 四、DDL脚本

```sql
CREATE TABLE ...
```

## 五、数据字典

## 六、后续建议
```

## 与其他Skill的配合
- 接收 `doc-generator-confirm` 的用户确认
- 生成完成后，向用户反馈结果
