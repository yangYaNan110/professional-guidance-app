---
name: frontend-web
description: Web端React应用开发
license: MIT
compatibility: opencode
---

## 我做什么

负责专业选择指导应用Web端的React应用开发，包括页面组件、语音交互界面、数据可视化等。

## 使用场景

- Web端功能开发
- 页面组件实现
- 语音交互界面开发
- 专业信息展示开发

## 输入格式

```json
{
  "feature": "功能描述",
  "requirements": [],
  "design_specs": {},
  "api_contracts": []
}
```

## 输出格式

```json
{
  "files_created": [],
  "files_modified": [],
  "components_defined": [],
  "services_defined": [],
  "tests_written": [],
  "documentation_updated": []
}
```

## 执行流程

1. 分析功能需求
2. 设计组件结构
3. 实现页面和组件
4. 集成API和数据
5. 实现语音交互（Web Speech API）
6. 添加可视化图表（Chart.js）
7. 编写测试代码

## 注意事项

- 实现响应式布局
- 优化语音交互体验
- 做好错误处理（语音识别失败）
- 遵循React最佳实践

## 推荐模型

- 代码生成：`anthropic/claude-3-5-sonnet-20241022`
