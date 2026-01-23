# 智能建模建议技能

## 描述
根据识别的场景，生成详细的数据建模设计构思，包括表结构、索引、缓存策略等。

## 触发词
设计构思、设计方案、我的建议是、建议这样设计

## 核心能力
1. **表结构设计**：设计满足3NF的表结构
2. **索引设计**：设计单列索引和复合索引
3. **缓存策略**：设计Redis缓存方案
4. **搜索策略**：设计Elasticsearch索引
5. **可选方案**：提供多种设计方案供选择
6. **优劣分析**：分析各方案的优缺点

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| entities | array | 是 | 识别的实体列表 |
| modeling_type | string | 是 | 建模类型 |
| existing_schema | object | 否 | 现有数据库结构 |
| performance_requirements | object | 否 | 性能要求 |

## 输出格式

```json
{
  "design_summary": "string",
  "tables": [
    {
      "name": "string",
      "description": "string",
      "columns": [
        {
          "name": "string",
          "type": "string",
          "constraints": ["string"],
          "description": "string"
        }
      ],
      "indexes": [
        {
          "columns": ["string"],
          "type": "string",
          "reason": "string"
        }
      ],
      "relationships": [
        {
          "to": "string",
          "type": "string",
          "description": "string"
        }
      ]
    }
  ],
  "cache_design": {
    "keys": [
      {
        "key": "string",
        "type": "string",
        "ttl": "number",
        "description": "string"
      }
    ]
  },
  "alternative_options": [
    {
      "name": "string",
      "pros": ["string"],
      "cons": ["string"],
      "recommendation": "string"
    }
  ],
  "questions": [
    {
      "question": "string",
      "impact": "string"
    }
  ]
}
```

## 使用示例

```
输入：
{
  "entities": [{"name": "用户收藏", "fields": ["用户ID", "专业ID", "收藏时间"]}],
  "modeling_type": "relational",
  "performance_requirements": {"qps": 1000}
}

输出：
{
  "design_summary": "设计一张用户收藏表，记录用户收藏的专业",
  "tables": [
    {
      "name": "user_favorites",
      "description": "用户收藏表",
      "columns": [
        {"name": "id", "type": "BIGSERIAL", "constraints": ["PRIMARY KEY"]},
        {"name": "user_id", "type": "BIGINT", "constraints": ["NOT NULL", "REFERENCES users(id)"]},
        {"name": "major_id", "type": "BIGINT", "constraints": ["NOT NULL", "REFERENCES majors(id)"]},
        {"name": "created_at", "type": "TIMESTAMP", "constraints": ["NOT NULL", "DEFAULT NOW()"]}
      ],
      "indexes": [
        {"columns": ["user_id"], "type": "btree", "reason": "按用户查询收藏列表"},
        {"columns": ["user_id", "created_at DESC"], "type": "btree", "reason": "按用户和时间排序"},
        {"columns": ["major_id"], "type": "btree", "reason": "统计热门专业"}
      ],
      "relationships": [
        {"to": "users", "type": "many-to-one", "description": "每个收藏属于一个用户"},
        {"to": "majors", "type": "many-to-one", "description": "每个收藏关联一个专业"}
      ]
    }
  ],
  "alternative_options": [
    {
      "name": "使用关联表",
      "pros": ["结构清晰", "易于扩展"],
      "cons": ["需要额外JOIN查询"],
      "recommendation": "推荐，适合未来可能增加收藏属性"
    }
  ],
  "questions": [
    {
      "question": "是否需要记录取消收藏的时间？",
      "impact": "如果需要，需要增加deleted_at字段"
    }
  ]
}
```

## 与其他Skill的配合
- 接收 `prompt-identify` 的输出
- 输出给 `prompt-confirm` 向用户确认
