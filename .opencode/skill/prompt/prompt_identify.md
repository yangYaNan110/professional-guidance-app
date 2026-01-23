# 数据建模场景识别技能

## 描述
分析用户描述的需求，识别是否需要建立数据表、缓存模型、索引策略或其他数据建模工作。

## 触发词
识别场景、是否需要设计、需要建表吗、需要缓存吗、这个功能需要存储数据吗

## 核心能力
1. **需求解析**：理解用户描述的业务场景
2. **数据存储识别**：识别需要持久化存储的数据
3. **缓存需求识别**：识别需要缓存的数据访问模式
4. **搜索需求识别**：识别需要全文搜索或复杂查询的场景
5. **实体提取**：提取潜在的实体和关系
6. **风险识别**：识别数据一致性和性能风险

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| user_input | string | 是 | 用户描述的需求文本 |
| current_context | object | 否 | 当前上下文信息（已存在的表、已有功能等） |
| project_phase | string | 否 | 项目阶段（设计/开发/优化） |

## 输出格式

```json
{
  "needs_data_modeling": boolean,
  "modeling_type": "relational|cache|search|vector|all|none",
  "confidence": "number",
  "entities": [
    {
      "name": "string",
      "description": "string",
      "fields": ["string"],
      "estimated_records": "string"
    }
  ],
  "reasoning": ["string"],
  "suggested_actions": [
    {
      "action": "string",
      "priority": "high|medium|low",
      "description": "string"
    }
  ],
  "existing_assets": {
    "tables": ["string"],
    "caches": ["string"],
    "indexes": ["string"]
  }
}
```

## 使用示例

```
用户输入：
"我想要一个功能，用户可以收藏感兴趣的专业，收藏后可以查看自己的收藏列表"

prompt-identify 返回：
{
  "needs_data_modeling": true,
  "modeling_type": "relational",
  "confidence": 0.95,
  "entities": [
    {
      "name": "用户收藏",
      "description": "用户收藏的专业记录",
      "fields": ["用户ID", "专业ID", "收藏时间"],
      "estimated_records": "每用户平均50条"
    }
  ],
  "reasoning": [
    "需要存储用户和专业的关联关系",
    "需要记录收藏时间用于排序",
    "查询频率高，适合建表索引"
  ],
  "suggested_actions": [
    {
      "action": "设计用户收藏表",
      "priority": "high",
      "description": "需要建立用户与专业的多对多关系表"
    }
  ]
}
```

## 与其他Skill的配合
- 输出给 `prompt-suggest` 生成设计构思
- 如果需要缓存，输出给 `prompt-suggest` 建议NoSQL设计
