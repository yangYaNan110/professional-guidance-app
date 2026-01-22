# video-search Skill - 视频智能搜索

## 功能描述

在视频平台（B站、YouTube等）搜索专业相关视频，支持多维度筛选和智能排序。

## 触发词

搜索、查找、找视频、视频、影片

## 核心能力

1. 多平台视频搜索（B站为主）
2. 智能关键词构建
3. 视频质量筛选
4. 搜索结果去重

---

## 搜索关键词策略

针对不同专业，自动构建多组搜索关键词：

```python
def build_search_keywords(major_name: str) -> List[str]:
    """构建专业视频搜索关键词"""
    return [
        f"{major_name}专业介绍",      # 专业解读
        f"{major_name}专业解读",       # 深度解读
        f"什么是{major_name}",         # 概念介绍
        f"{major_name}就业前景",       # 就业分析
        f"{major_name}报考指南",       # 报考指导
        f"{major_name}学长学姐",       # 经验分享
    ]
```

---

## 搜索平台

| 平台 | 优先级 | 说明 |
|-----|-------|------|
| B站 | 1 | 国内最大学习视频平台，内容丰富 |
| 知乎 | 2 | 专业问答和经验分享 |
| 小红书 | 3 | 真实学习体验分享 |

---

## B站API调用规范

```python
BILIBILI_API = "https://api.bilibili.com/x/web-interface/search/type"

# 必需请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com"
}

# 搜索参数
SEARCH_PARAMS = {
    "search_type": "video",
    "keyword": keyword,           # 搜索关键词
    "page": 1,                   # 页码
    "page_size": 10,             # 每页数量
    "order": "totalrank"         # 排序方式
}
```

---

## 视频筛选标准

| 标准 | 要求 |
|-----|------|
| 内容相关性 | 标题和描述必须包含搜索关键词 |
| 时长 | 优先3-20分钟的中长视频 |
| 播放量 | 优先1000+播放的视频 |
| 发布时间 | 优先近2年的视频 |
| 内容质量 | 优先有完整知识体系的视频 |

---

## 搜索结果去重规则

| 去重级别 | 规则 | 实现方式 |
|---------|------|---------|
| 完全去重 | 相同BV号视为同一视频 | Set集合 |
| 近似去重 | 标题相似度>80%视为重复 | SimHash |
| 系列去重 | 同一UP主的系列视频归类 | UP主+标题匹配 |

---

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | int | 否 | 页码（默认1） |
| page_size | int | 否 | 每页数量（默认10） |
| order | string | 否 | 排序方式（默认totalrank） |

---

## 输出格式

```json
{
  "success": true,
  "query": "人工智能专业介绍",
  "total_results": 100,
  "page": 1,
  "page_size": 10,
  "videos": [
    {
      "bvid": "BV1xxx",
      "title": "人工智能专业介绍",
      "description": "...",
      "cover": "https://...",
      "duration": 600,
      "author": "UP主名",
      "view_count": 10000,
      "pubdate": 1700000000,
      "url": "https://www.bilibili.com/video/BV1xxx"
    }
  ]
}
```

---

## 使用示例

```python
from video_search import VideoSearcher

searcher = VideoSearcher()

# 搜索专业视频
result = searcher.search(
    keyword="人工智能专业介绍",
    page=1,
    page_size=10
)

print(result.success)
print(result.total_results)
for video in result.videos:
    print(video.title, video.view_count)
```

---

## 专业视频搜索示例

```python
# 搜索人工智能相关视频
result = searcher.search_professional_videos("人工智能")

# 返回5个高质量视频
for video in result.videos:
    print(f"- {video.title}")
    print(f"  播放量: {video.view_count}")
    print(f"  时长: {video.duration}")
```

---

## 与其他Skill的配合

- **video-summary**：搜索结果可进一步使用视频摘要Skill生成摘要
- **video-clip**：找到目标视频后可使用视频剪辑Skill进行剪辑
- **video-analyze**：搜索结果可使用视频分析Skill获取详细信息
