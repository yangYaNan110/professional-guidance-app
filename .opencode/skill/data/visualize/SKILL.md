---
name: data-visualize
description: 数据可视化开发，包括图表组件、数据看板
license: MIT
compatibility: opencode
---

## 我做什么

负责数据可视化模块的开发，包括图表组件、数据看板、报表导出等功能。

## 使用场景

- 可视化功能开发
- 新图表类型添加
- 数据看板定制

## 输入格式

```json
{
  "visualization_type": "图表类型",
  "data_source": {},
  "interactions": [],
  "responsive": true
}
```

## 输出格式

```json
{
  "files_created": [],
  "chart_components": [],
  "dashboard_layouts": [],
  "export_formats": [],
  "interactive_features": [],
  "tests_written": []
}
```

## 执行流程

1. 选择图表类型
2. 实现图表组件
3. 实现交互功能
4. 设计看板布局
5. 实现导出功能
6. 编写测试用例

## 注意事项

- 优化渲染性能
- 确保数据准确
- 适配不同屏幕
- 提供无障碍支持

## 推荐模型

- 可视化开发：`anthropic/claude-3-5-sonnet-20241022`
