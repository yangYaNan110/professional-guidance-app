---
name: ai-recommend
description: 推荐算法开发，包括用户画像、岗位推荐、推荐解释
license: MIT
compatibility: opencode
---

## 我做什么

负责推荐系统的开发，包括用户画像构建、岗位推荐算法、推荐解释生成等功能。

## 使用场景

- 推荐功能开发
- 用户画像更新
- 推荐结果优化

## 输入格式

```json
{
  "recommendation_type": "岗位/课程/内容",
  "user_features": [],
  "item_features": [],
  "evaluation_metrics": []
}
```

## 输出格式

```json
{
  "files_created": [],
  "user_profile_builder": {},
  "recommendation_algorithm": {},
  "matching_engine": {},
  "explanation_generator": {},
  "a_b_testing": {},
  "tests_written": []
}
```

## 执行流程

1. 设计用户画像结构
2. 实现画像构建流程
3. 实现推荐算法
4. 实现匹配引擎
5. 实现推荐解释
6. 配置A/B测试
7. 编写测试用例

## 注意事项

- 平衡准确性和多样性
- 避免信息茧房
- 保护用户隐私
- 做好冷启动处理

## 推荐模型

- 推荐系统：`anthropic/claude-opus-4-20240307`
