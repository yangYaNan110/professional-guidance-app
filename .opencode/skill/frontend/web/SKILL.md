---
name: frontend-web
description: Web端React应用开发，包括推荐大学弹窗、用户目标设置
license: MIT
compatibility: opencode
---

## 我做什么

负责专业选择指导应用Web端的React应用开发，包括页面组件、语音交互界面、数据可视化、推荐大学弹窗、用户目标设置等。

## 使用场景

- Web端功能开发
- 页面组件实现
- 语音交互界面开发
- 专业信息展示开发
- 推荐大学弹窗开发
- 用户目标设置功能开发

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
7. 实现推荐大学弹窗逻辑
8. 实现用户目标存储（localStorage）
9. 编写测试代码

## 推荐大学弹窗规则

### 首次进入逻辑

1. 用户进入"推荐大学"选项卡
2. 检查 localStorage 中是否有用户目标
3. 如果没有设置过用户目标，显示目标设置弹窗
4. 设置完成后保存到 localStorage

### 弹窗UI设计

| 字段 | 类型 | 说明 |
|-----|------|------|
| 目标省份 | 下拉选择 | 可选择任意省份或"不设置省份" |
| 预估分数 | 数字输入 | 可输入分数或"不设置分数" |
| 确认按钮 | 按钮 | 保存并应用 |
| 跳过按钮 | 按钮 | 跳过，使用默认值 |

### 再次进入逻辑

1. 用户再次进入"推荐大学"选项卡
2. 直接使用 localStorage 中保存的用户目标
3. 右上角显示"修改目标"按钮，点击可重新设置

### 用户目标存储

```typescript
interface UserTarget {
  province?: string;  // 可选
  score?: number;     // 可选
}

// 存储位置：localStorage
// key: 'userTarget'
```

### 大学卡片显示规则

#### 录取分数显示

在大学卡片中清晰展示录取分数信息：

```typescript
// 格式化历史录取分数
const formatAdmissionScores = (scores: AdmissionScore[], targetProvince: string): string => {
  // 筛选目标省份的数据
  const provinceScores = scores.filter(s => s.province === targetProvince);
  // 按年份降序排序
  const sorted = [...provinceScores].sort((a, b) => b.year - a.year);
  
  // 最近一年
  const latest = sorted[0];
  // 过往2-3年（最多取2个）
  const history = sorted.slice(1, 3);
  
  if (history.length > 0) {
    const historyStr = history.map(s => `${s.year}年${s.min_score}分`).join(' → ');
    return `${latest.year}年: ${latest.min_score}分 (${historyStr})`;
  }
  
  return `${latest.year}年: ${latest.min_score}分`;
};
```

#### 大学卡片UI布局

```
┌─────────────────────────────────────────────────────────────┐
│  [标签] 大学名称           [985] [211]           680分     │
│  省份 城市  •  就业率 xx%                                  │
│  推荐理由                                             │
│  📈 历史: 2023年659分 → 2022年652分                      │
└─────────────────────────────────────────────────────────────┘
```

**显示规则：**
- 标签：985/211/其他
- 优先显示目标省份的录取分数
- 历史分数最多显示2年
- 悬停可查看完整历史记录

## 注意事项

- 实现响应式布局
- 优化语音交互体验
- 做好错误处理（语音识别失败）
- 遵循React最佳实践
- 弹窗中的省份和分数都是可选的
- 用户跳过时仍能正常显示推荐结果

## 推荐模型

- 代码生成：`anthropic/claude-3-5-sonnet-20241022`
