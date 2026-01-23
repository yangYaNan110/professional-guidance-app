# NoSQL数据模型设计技能

## 描述
设计Redis缓存模型、Elasticsearch索引结构、MongoDB文档模型等非关系型数据库的数据模型。

## 触发词
设计Redis、设计ES、设计MongoDB、设计缓存、设计索引、NoSQL

## 核心能力
1. **Redis模型设计**：设计键结构、选择合适的数据类型（String/Hash/List/Set/ZSet）
2. **过期策略**：设计缓存过期策略（TTL、惰性删除、定期删除）
3. **Elasticsearch设计**：设计索引Mapping、分词器、查询优化
4. **MongoDB设计**：设计文档结构、集合规划、分片策略
5. **向量数据库设计**：设计知识库检索的向量索引
6. **缓存策略**：设计多级缓存、缓存穿透/击穿/雪崩解决方案

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| nosql_type | string | 是 | NoSQL类型（redis/elasticsearch/mongodb/chroma） |
| data_requirements | object | 是 | 数据需求和访问模式 |
| read_patterns | array | 否 | 读取模式（按ID查询/全文搜索/聚合查询） |
| write_patterns | array | 否 | 写入模式（实时写入/批量写入） |
| performance_requirements | object | 否 | 性能要求 |

## 输出格式

```json
{
  "redis_design": {
    "key_patterns": [
      {
        "key": "string",
        "type": "string",
        "ttl": "number",
        "description": "string",
        "example_value": "string"
      }
    ],
    "data_structures": [
      {
        "purpose": "string",
        "type": "string",
        "fields": ["string"],
        "operations": ["string"]
      }
    ],
    "cache_strategy": {
      "type": "write-through|write-behind|read-through",
      "ttl_policy": "string",
      "eviction_policy": "string"
    }
  },
  "elasticsearch_design": {
    "indexes": [
      {
        "name": "string",
        "shards": "number",
        "replicas": "number",
        "mapping": {
          "properties": [
            {"name": "string", "type": "string", "analyzer": "string"}
          ]
        }
      }
    ],
    "query_optimization": {
      "preferred_queries": ["string"],
      "avoid_queries": ["string"]
    }
  },
  "mongodb_design": {
    "collections": [
      {
        "name": "string",
        "documents": [
          {
            "field": "string",
            "type": "string",
            "index": "boolean"
          }
        ],
        "indexes": [
          {"fields": ["string"], "type": "string"}
        ]
      }
    ]
  },
  "vector_design": {
    "collection": "string",
    "dimension": "number",
    "metric": "string",
    "index_type": "string"
  }
}
```

## 使用示例

```
输入：
{
  "nosql_type": "redis",
  "data_requirements": {
    "user_session": "用户会话信息",
    "user_profile": "用户基本信息",
    "recent_searches": "最近搜索记录"
  },
  "read_patterns": ["按用户ID查询", "批量查询"],
  "performance_requirements": {"ttl": "1h", "qps": 10000}
}

输出：
{
  "redis_design": {
    "key_patterns": [
      {"key": "session:{user_id}", "type": "hash", "ttl": 7200, "description": "用户会话"},
      {"key": "user:{user_id}", "type": "hash", "ttl": null, "description": "用户信息"},
      {"key": "recent:{user_id}", "type": "list", "ttl": 86400, "description": "最近搜索"}
    ]
  }
}
```

## 与其他Skill的配合
- 与 `db-expert-design` 配合，设计关系型+NoSQL混合架构
- 与 `db-expert-optimize` 配合，优化NoSQL查询性能
