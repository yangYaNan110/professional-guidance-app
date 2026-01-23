# 爬虫数据分析技能

## 描述
分析项目中需要爬取数据的模块和业务，识别数据来源、更新频率和数据量级。

## 触发词
分析爬虫数据、分析数据需求、分析模块业务、数据来源分析

## 核心能力
1. **模块识别**：识别项目中需要数据爬取的模块
2. **业务分析**：分析各模块的业务需求和数据依赖
3. **来源识别**：识别数据的权威来源网站
4. **频率评估**：评估数据更新频率要求
5. **量级评估**：评估数据量和性能要求
6. **输出分析报告**：生成爬虫数据需求分析报告

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| task_type | string | 是 | 任务类型（如"爬虫数据分析"） |
| scope | string | 否 | 分析范围（默认分析所有模块） |
| existing_modules | array | 否 | 已识别的模块列表 |

## 输出格式

```json
{
  "modules": [
    {
      "name": "string",
      "description": "string",
      "data_types": ["string"],
      "source_websites": [
        {
          "name": "string",
          "url": "string",
          "data_type": "string",
          "update_frequency": "string"
        }
      ],
      "data_volume": "string",
      "update_frequency": "string",
      "priority": "number"
    }
  ],
  "summary": {
    "total_modules": "number",
    "total_data_types": "number",
    "total_source_websites": "number",
    "critical_requirements": ["string"]
  }
}
```

## 使用示例

```
输入：
{
  "task_type": "爬虫数据分析",
  "scope": "全部模块"
}

输出：
{
  "modules": [
    {
      "name": "专业行情数据",
      "description": "爬取各专业的就业率、薪资、热度等行情数据",
      "data_types": ["就业率", "平均薪资", "热度指数", "发展趋势"],
      "source_websites": [
        {"name": "阳光高考", "url": "https://gaokao.chsi.com.cn", "data_type": "专业信息", "update_frequency": "每日"},
        {"name": "中国教育在线", "url": "https://www.eol.cn", "data_type": "专业介绍", "update_frequency": "每日"}
      ],
      "data_volume": "约10000条专业数据",
      "update_frequency": "每3天",
      "priority": 10
    },
    {
      "name": "录取分数线",
      "description": "爬取各高校各专业的录取分数线",
      "data_types": ["最低录取分", "最高录取分", "平均分", "录取人数"],
      "source_websites": [
        {"name": "阳光高考", "url": "https://gaokao.chsi.com.cn", "data_type": "录取分数", "update_frequency": "每年更新"}
      ],
      "data_volume": "约50000条录取数据",
      "update_frequency": "每年高考后",
      "priority": 9
    }
  ],
  "summary": {
    "total_modules": 6,
    "total_data_types": 15,
    "total_source_websites": 8,
    "critical_requirements": ["录取分数线数据必须准确", "专业行情需要定期更新"]
  }
}
```

## 与其他Skill的配合
- 输出给 `doc-generator-design` 进行数据模型设计
- 可调用DB-Expert分析数据结构
