# 查询优化技能

## 描述
分析查询性能瓶颈，设计索引策略，优化SQL语句，提供查询优化建议和执行计划分析。

## 触发词
优化查询、优化SQL、优化索引、慢查询、分析执行计划

## 核心能力
1. **慢查询分析**：识别和分类慢查询
2. **执行计划分析**：解析EXPLAIN输出，识别性能瓶颈
3. **索引设计**：设计合适的单列索引和复合索引
4. **查询重写**：优化SQL语句结构
5. **分区策略**：设计表分区策略
6. **缓存策略**：设计查询缓存和结果缓存
7. **优化报告**：生成详细的优化建议报告

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| sql_query | string | 是 | 需要优化的SQL查询 |
| table_info | object | 是 | 表结构信息 |
| explain_result | string | 否 | EXPLAIN输出结果 |
| current_indexes | array | 否 | 当前已有的索引 |
| performance_requirements | object | 否 | 性能要求（QPS、延迟等） |

## 输出格式

```json
{
  "analysis": {
    "bottlenecks": ["string"],
    "full_table_scan": boolean,
    "missing_indexes": ["string"],
    "inefficient_joins": ["string"],
    "sort_operations": ["string"]
  },
  "recommendations": [
    {
      "type": "index|rewrite|partition|cache",
      "description": "string",
      "sql_before": "string",
      "sql_after": "string",
      "expected_improvement": "string"
    }
  ],
  "index_suggestions": [
    {
      "table": "string",
      "columns": ["string"],
      "type": "btree|hash|gist|gin",
      "unique": boolean,
      "reason": "string"
    }
  ],
  "optimized_query": "string",
  "performance_estimate": {
    "before_ms": "number",
    "after_ms": "number",
    "improvement_factor": "number"
  }
}
```

## 使用示例

```
输入：
{
  "sql_query": "SELECT * FROM orders WHERE status = 'completed' AND created_at > '2024-01-01' ORDER BY created_at DESC LIMIT 100",
  "table_info": {"orders": {"columns": [...]}},
  "current_indexes": ["PRIMARY KEY (id)"]
}

输出：
{
  "analysis": {
    "bottlenecks": ["缺少status字段索引", "全表扫描"],
    "missing_indexes": ["idx_orders_status", "idx_orders_status_created_at"]
  },
  "recommendations": [
    {
      "type": "index",
      "description": "添加复合索引",
      "sql_after": "CREATE INDEX idx_orders_status_created_at ON orders(status, created_at DESC)",
      "expected_improvement": "查询时间从2s降至50ms"
    }
  ]
}
```

## 与其他Skill的配合
- 接收 `db-expert-design` 的输出，了解表结构
- 输出优化建议供 `db-expert-design` 添加索引
