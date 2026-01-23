# 数据库需求分析技能

## 描述
分析用户提出的数据库设计需求，理解业务场景，提取实体、关系和约束条件，输出详细的数据需求规格说明。

## 触发词
分析需求、分析数据库需求、数据需求分析、理解业务需求

## 核心能力
1. **需求理解**：解析用户描述的业务场景，识别核心业务实体
2. **实体提取**：识别系统中的主要数据对象（用户、订单、商品等）
3. **关系识别**：分析实体之间的关联关系（一对一、一对多、多对多）
4. **约束识别**：识别数据完整性约束（唯一性、外键、CHECK约束）
5. **性能评估**：评估数据量级、并发访问量、读写比例
6. **需求文档生成**：输出结构化的数据需求规格文档

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| requirement_text | string | 是 | 用户描述的业务需求文本 |
| context | string | 否 | 额外的上下文信息（如技术约束、已有系统等） |

## 输出格式

```json
{
  "entities": [
    {
      "name": "string",
      "description": "string",
      "attributes": [
        {
          "name": "string",
          "type": "string",
          "constraints": ["string"],
          "description": "string"
        }
      ]
    }
  ],
  "relationships": [
    {
      "from": "string",
      "to": "string",
      "type": "one-to-one|one-to-many|many-to-many",
      "description": "string"
    }
  ],
  "constraints": [
    {
      "type": "unique|foreign-key|check|not-null",
      "target": "string",
      "expression": "string"
    }
  ],
  "performance_requirements": {
    "expected_qps": "number",
    "expected_data_volume": "string",
    "read_write_ratio": "string",
    "max_latency_ms": "number"
  },
  "notes": "string"
}
```

## 使用示例

```
用户输入：
"设计一个用户管理系统，需要存储用户的基本信息（ID、姓名、邮箱、手机号、注册时间），
用户可以拥有多个角色，每个角色可以有多个权限。系统预计有100万用户，读多写少。"

db-expert-analyze 返回：
{
  "entities": ["用户", "角色", "权限"],
  "relationships": [
    {"from": "用户", "to": "角色", "type": "many-to-many"},
    {"from": "角色", "to": "权限", "type": "many-to-many"}
  ],
  "performance_requirements": {
    "expected_qps": 1000,
    "expected_data_volume": "100万用户",
    "read_write_ratio": "9:1",
    "max_latency_ms": 100
  }
}
```

## 与其他Skill的配合
- 输出给 `db-expert-design` 进行数据库结构设计
- 输出给 `db-expert-optimize` 进行性能评估
