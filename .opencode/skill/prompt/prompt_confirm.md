# 需求确认和引导技能

## 描述
向用户展示设计构思，通过友好的对话获取用户的确认或修改意见。

## 触发词
确认、同意吗、你看这样可以吗、有什么需要修改的吗

## 核心能力
1. **友好提示**：以友好方式向用户展示设计建议
2. **方案展示**：清晰展示设计构思（表格、索引、缓存等）
3. **可选方案**：提供多种方案供用户选择
4. **修改意见收集**：收集用户的修改意见
5. **逐步引导**：引导用户完善需求细节
6. **确认决策**：明确获取用户的最终确认

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| design | object | 是 | 设计构思（来自prompt-suggest） |
| user_input | string | 否 | 用户的新输入（如果有修改意见） |
| confirmation_state | string | 否 | 确认状态（pending/confirmed/modifying） |

## 输出格式

```json
{
  "message_to_user": "string",
  "design_summary": "string",
  "key_points": ["string"],
  "options": [
    {
      "name": "string",
      "description": "string",
      "selected": boolean
    }
  ],
  "questions": [
    {
      "question": "string",
      "options": ["string"],
      "selected_option": "string"
    }
  ],
  "confirmation_required": boolean,
  "confirmation_text": "string",
  "next_action": "wait_confirm|execute|request_modification"
}
```

## 使用示例

```
输入：
{
  "design": {"tables": [...], "cache_design": {...}},
  "confirmation_state": "pending"
}

输出：
{
  "message_to_user": "我注意到这个功能需要存储用户收藏数据，我的设计构思如下：",
  "design_summary": "设计一张用户收藏表，记录用户收藏的专业",
  "key_points": [
    "📋 主表：user_favorites（用户收藏表）",
    "🔑 索引：user_id + created_at 用于快速查询用户收藏列表",
    "🔗 外键：关联 users 和 majors 表"
  ],
  "options": [
    {
      "name": "方案A：基础收藏",
      "description": "仅记录用户ID、专业ID和收藏时间",
      "selected": true
    },
    {
      "name": "方案B：带备注",
      "description": "额外记录收藏时的备注信息",
      "selected": false
    }
  ],
  "questions": [
    {
      "question": "收藏列表需要支持排序吗？",
      "options": ["按时间倒序", "按专业分类", "手动排序"],
      "selected_option": "按时间倒序"
    }
  ],
  "confirmation_required": true,
  "confirmation_text": "以上是我的设计构思，包含1张表和3个索引。是否同意这个设计？如果不同意或有其他需求，请告诉我。",
  "next_action": "wait_confirm"
}
```

## 对话示例

```
Agent: 我注意到"用户收藏专业"这个功能需要数据存储支持。

我的设计构思：
📋 表结构：user_favorites (id, user_id, major_id, created_at)
🔑 索引：(user_id), (user_id + created_at DESC)
🔗 外键：关联 users、majors 表

可选方案：
A. 基础收藏（当前推荐）
B. 带备注收藏（可添加收藏时的备注）

您觉得这个设计如何？有什么需要修改的吗？
```

## 与其他Skill的配合
- 接收 `prompt-suggest` 的设计构思
- 用户确认后，输出给 `prompt-execute` 执行设计
- 用户有修改意见，重新输出给 `prompt-suggest` 调整设计
