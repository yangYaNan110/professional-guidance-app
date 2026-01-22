---
name: data-crawler
description: 爬虫服务开发，包括数据采集、清洗、结构化
license: MIT
compatibility: opencode
---

## 我做什么

负责就业数据爬虫服务的开发，包括招聘网站数据采集、反爬处理、数据清洗和结构化。

## 使用场景

- 爬虫功能开发
- 新数据源接入
- 数据清洗流程优化

## 输入格式

```json
{
  "target_source": "目标网站",
  "data_types": [],
  "update_frequency": "daily/weekly",
  "anti_detection": true
}
```

## 输出格式

```json
{
  "files_created": [],
  "spider_modules": [],
  "parser_modules": [],
  "cleaner_modules": [],
  "anti_detection": {},
  "scheduler_config": {},
  "tests_written": []
}
```

## 执行流程

1. 分析目标网站结构
2. 编写爬虫模块
3. 实现数据解析
4. 实现数据清洗
5. 实现反爬策略
6. 配置调度任务
7. 编写测试用例

## 注意事项

- 遵守robots.txt
- 控制请求频率
- 处理动态内容
- 做好数据去重

## 推荐模型

- 爬虫开发：`anthropic/claude-3-5-sonnet-20241022`
