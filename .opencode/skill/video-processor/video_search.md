# video-search Skill - 视频智能搜索

## 功能描述

在视频库中搜索符合条件的视频，支持多维度筛选、关键词匹配、内容检索和相似视频推荐。

## 核心能力

1. 关键词视频搜索
2. 多维度视频筛选
3. 内容相关度排序
4. 相似视频推荐
5. 实时搜索建议
6. 搜索结果去重

---

## 搜索维度

| 搜索维度 | 说明 | 筛选方式 |
|---------|------|---------|
| `KEYWORD` | 关键词匹配 | 标题、描述、字幕 |
| `TOPIC` | 主题分类 | 预设分类体系 |
| `DURATION` | 时长筛选 | 范围筛选 |
| `DATE` | 发布时间 | 时间范围 |
| `VIEW_COUNT` | 播放量 | 排序和筛选 |
| `QUALITY` | 视频质量 | 分辨率、清晰度 |
| `SOURCE` | 来源平台 | YouTube、B站等 |
| `LANGUAGE` | 语言 | 语种筛选 |
| `TAGS` | 标签 | 精确/模糊匹配 |
| `CONTENT` | 内容检索 | 字幕内容分析 |

---

## 搜索类型

| 搜索类型 | 说明 | 特点 |
|---------|------|------|
| `BASIC` | 基础搜索 | 简单关键词匹配 |
| `ADVANCED` | 高级搜索 | 多条件组合 |
| `FULL_TEXT` | 全文搜索 | 字幕内容检索 |
| `SEMANTIC` | 语义搜索 | 基于向量相似度 |
| `RECOMMEND` | 推荐搜索 | 基于用户偏好 |
| `RELATED` | 相关搜索 | 基于种子视频 |

---

## 语义搜索规范

### 1. 向量化处理

```
搜索流程：
1. 将查询文本向量化（使用预训练模型）
2. 在视频向量库中检索相似向量
3. 返回相似度最高的结果
4. 结合其他排序因素综合评分
```

### 2. 内容理解

- ✅ 理解搜索意图
- ✅ 支持同义词扩展
- ✅ 处理口语化表达
- ✅ 支持多语言搜索

### 3. 相似度计算

| 维度 | 权重 | 说明 |
|-----|------|------|
| 语义相似度 | 40% | 向量相似度计算 |
| 标题匹配度 | 25% | 标题关键词匹配 |
| 描述匹配度 | 15% | 描述相关性 |
| 标签匹配度 | 10% | 标签覆盖度 |
| 质量评分 | 10% | 视频质量因素 |

---

## 搜索结果处理

### 1. 结果排序

| 排序方式 | 说明 |
|---------|------|
| `RELEVANCE` | 相关性优先 |
| `DATE_DESC` | 最新发布优先 |
| `DATE_ASC` | 最早发布优先 |
| `VIEW_DESC` | 播放量优先 |
| `VIEW_ASC` | 播放量升序 |
| `DURATION` | 时长优先 |
| `QUALITY` | 质量优先 |
| `HYBRID` | 综合排序 |

### 2. 结果去重

| 去重策略 | 说明 | 适用场景 |
|---------|------|---------|
| `EXACT` | 完全相同视频 | 跨平台搜索 |
| `NEAR_DUPLICATE` | 近似重复检测 | 内容搬运识别 |
| `SERIES` | 系列视频归类 | 连续剧集处理 |

### 3. 结果分页

```
分页参数：
- page: 当前页码（从1开始）
- page_size: 每页数量（默认10，最大100）
- offset: 偏移量（替代page使用）
```

---

## 搜索建议与补全

### 1. 实时建议

- ✅ 基于搜索历史推荐
- ✅ 热门搜索词推荐
- ✅ 关联词扩展推荐
- ✅ 拼写纠错建议

### 2. 搜索补全

```
补全流程：
1. 监听用户输入
2. 实时查询补全词库
3. 返回候选词列表
4. 用户选择或继续输入
```

### 3. 建议类型

| 类型 | 说明 | 示例 |
|-----|------|------|
| `HISTORY` | 历史搜索 | "人工智能" |
| `HOT` | 热门搜索 | "ChatGPT教程" |
| `RELATED` | 关联搜索 | "深度学习" → "神经网络" |
| `CORRECTION` | 拼写纠正 | "机哭学习" → "机器学习" |

---

## 输出格式

### 搜索结果

```json
{
  "search_id": "search_123",
  "query": "人工智能教程",
  "total_results": 1500,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "video_id": "vid_456",
      "title": "人工智能入门教程",
      "description": "本教程介绍人工智能基础知识...",
      "duration": 3600,
      "publish_time": "2024-01-10",
      "view_count": 50000,
      "source": "youtube",
      "url": "https://youtube.com/watch?v=xxx",
      "thumbnail": "https://img.youtube.com/vi/xxx/0.jpg",
      "relevance_score": 0.95,
      "match_type": "semantic",
      "matched_terms": ["人工智能", "入门", "教程"]
    }
  ],
  "suggestions": ["人工智能入门", "AI教程", "深度学习"]
}
```

### 语义搜索结果

```json
{
  "search_id": "semantic_789",
  "query_vector": [0.1, 0.5, 0.3, ...],
  "results": [
    {
      "video_id": "vid_001",
      "title": "深度学习基础",
      "similarity": 0.92,
      "embedding_model": "text-embedding-3-small",
      "highlights": [
        {"field": "description", "snippet": "...深度学习是AI的核心..."}
      ]
    }
  ],
  "related_searches": ["神经网络入门", "机器学习基础"]
}
```

### 推荐结果

```json
{
  "recommend_id": "rec_321",
  "based_on": "vid_seed_123",
  "recommendations": [
    {
      "video_id": "vid_789",
      "title": "相似主题视频",
      "similarity": 0.88,
      "reason": "主题相似",
      "tags": ["AI", "教程", "入门"]
    }
  ]
}
```

---

## 使用示例

```python
from video_search import VideoSearcher, SearchType, SortBy

searcher = VideoSearcher()

# 基础搜索
results = searcher.search(
    query="人工智能教程",
    search_type=SearchType.BASIC,
    sort_by=SortBy.RELEVANCE,
    filters={
        "duration_min": 300,
        "duration_max": 3600,
        "language": "zh-CN",
        "quality": "high"
    },
    pagination={
        "page": 1,
        "page_size": 20
    }
)

print(results.total_results)
print(results.results)

# 语义搜索
semantic_results = searcher.semantic_search(
    query="如何学习机器学习",
    top_k=10,
    include_highlights=True
)

print(semantic_results.results)

# 相关视频推荐
recommendations = searcher.get_recommendations(
    video_id="vid_123",
    count=5,
    reason=True
)

print(recommendations.recommendations)

# 获取搜索建议
suggestions = searcher.get_suggestions(
    prefix="人工",
    count=5
)

print(suggestions)
```

---

## 与其他Skill的配合

- **video-summary**：搜索结果可进一步使用视频摘要Skill生成摘要
- **video-clip**：找到目标视频后可使用视频剪辑Skill进行剪辑
- **video-asr**：搜索结果可使用语音识别Skill获取字幕进行二次分析
