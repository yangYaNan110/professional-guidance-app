# video-search Skill - 视频智能搜索

## 功能描述

在视频平台（B站、YouTube等）搜索专业相关视频，支持多维度筛选和智能排序。

## 触发词

搜索、查找、找视频、视频、影片

## 核心能力

1. 多平台视频搜索（B站为主）
2. 智能关键词构建
3. 视频质量筛选
4. 热点事件获取与整合
5. 搜索结果去重

---

## 热点事件获取

### 热点事件定义

热点事件是指与专业相关的最新重大事件或新闻：

| 事件类型 | 示例 |
|---------|------|
| 技术突破 | "OpenAI发布GPT-5"、"特斯拉发布自动驾驶新算法" |
| 行业动态 | "某AI公司上市"、"某技术获得诺贝尔奖" |
| 政策变化 | "国家发布AI发展规划"、"某专业列入 |
| 重要强基计划"会议 | "世界AI大会召开"、"诺奖得主来华讲座" |
| 社会事件 | "AI换脸引发争议"、"算法歧视事件" |

### 热点事件搜索

```python
async def get_hot_events(major_name: str) -> List[Dict]:
    """从多个平台获取专业相关的热点事件"""
    all_events = []
    
    # 1. 从B站搜索热点视频
    bilibili_events = await search_bilibili_hot(major_name)
    all_events.extend(bilibili_events)
    
    # 2. 从知乎搜索热点问答/文章
    zhihu_events = await search_zhihu_hot(major_name)
    all_events.extend(zhihu_events)
    
    # 3. 从36氪搜索科技新闻
    kr36_events = await search_kr36_hot(major_name)
    all_events.extend(kr36_events)
    
    # 4. 从虎嗅搜索科技资讯
    huxiu_events = await search_huxiu_hot(major_name)
    all_events.extend(huxiu_events)
    
    # 去重并按热度排序
    unique_events = deduplicate_by_title(all_events)
    unique_events.sort(key=lambda x: x.get("heat_index", 0), reverse=True)
    
    return unique_events[:10]
```

### 多数据源结构

| 数据源 | 内容类型 | 返回字段 |
|-------|---------|---------|
| B站 | 视频 | title, cover, duration, author, play, url, is_video=True |
| 知乎 | 问答/文章 | title, description, url, is_video=False |
| 36氪 | 新闻 | title, description, url, is_video=False |
| 虎嗅 | 资讯 | title, description, url, is_video=False |

### 热点事件数据结构

**核心原则：热点内容不一定是视频，也可以是跳转到外部网页链接**

| 内容类型 | 说明 | 优先级 |
|---------|------|-------|
| 视频内容 | B站、YouTube等平台的视频 | 优先（带封面、时长、播放量） |
| 新闻资讯 | 知乎、36氪、虎嗅等平台的文章 | 优先（带阅读量、来源） |
| 社交动态 | 微博、小红书的热门讨论 | 次优（带讨论热度） |

```json
{
  "hot_video": {
    "title": "2025年AI最新突破：GPT-5发布",
    "description": "...",
    "cover": "https://...",
    "duration": 300,
    "author": "科技博主",
    "view_count": 50000,
    "pub_date": "2025-01-20",
    "url": "https://www.bilibili.com/video/BVxxx",
    "source": "B站",
    "is_video": true,
    "event_type": "技术突破"
  },
  "hot_events": [
    {
      "title": "工信部发布人工智能发展规划",
      "description": "...",
      "view_count": 10000,
      "pub_date": "2025-01-19",
      "url": "https://zhihu.com/question/xxx",
      "source": "知乎",
      "is_video": false,
      "event_type": "政策变化"
    }
  ]
}
```

**热点内容字段说明：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| title | string | 标题（必填） |
| description | string | 描述 |
| cover | string\|null | 封面图（视频有，新闻可能无） |
| duration | int\|null | 时长（视频有，单位：秒） |
| author | string\|null | 作者/发布者 |
| view_count | int | 播放量/阅读量/热度 |
| pub_date | string | 发布日期 |
| url | string | 跳转链接（必填） |
| source | string | 来源平台 |
| is_video | boolean | True=视频，False=网页链接 |
| event_type | string\|null | 事件类型 |


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
| **视频数量** | **只返回1个最佳视频** |
| **内容覆盖** | 必须覆盖时间线5个阶段：起源与发展、挫折与争议、重大突破、现状与爆发、未来展望 |
| 时长 | 优先3-5分钟的短视频（最佳180-300秒） |
| 播放量 | 优先1000+播放的视频 |
| 发布时间 | 优先近2年的视频 |
| 内容质量 | 优先有完整知识体系的视频 |

---

## 视频评分规则

```python
def calculate_video_score(video: Dict, major_name: str) -> float:
    """计算视频评分，返回最高分的视频"""
    score = 0.0
    
    # 内容覆盖度（最重要，权重50%）
    title = video.get("title", "")
    description = video.get("description", "")
    content = f"{title} {description}".lower()
    
    required_keywords = [
        ("起源", "发展", "历史"),        # 起源与发展
        ("挫折", "争议", "低谷", "寒冬"), # 挫折与争议
        ("突破", "成就", "里程碑", "革命"), # 重大突破
        ("现状", "爆发", "现在", "当前"),  # 现状与爆发
        ("未来", "展望", "趋势", "前景")   # 未来展望
    ]
    
    coverage_count = sum(1 for kw_group in required_keywords if any(kw in content for kw in kw_group))
    coverage_score = (coverage_count / 5) * 50  # 满分50分
    
    # 时长评分（权重20%），最佳3-5分钟
    duration = video.get("duration", 0)
    if duration <= 60:
        duration_score = 5   # 太短
    elif duration <= 180:
        duration_score = 15  # 偏短
    elif duration <= 300:
        duration_score = 20  # 最佳
    elif duration <= 600:
        duration_score = 12  # 可接受
    else:
        duration_score = 5   # 太长
    
    # 播放量评分（权重15%）
    view_count = video.get("view_count", 0)
    if view_count >= 100000:
        view_score = 15
    elif view_count >= 50000:
        view_score = 13
    elif view_count >= 10000:
        view_score = 11
    elif view_count >= 5000:
        view_score = 9
    elif view_count >= 1000:
        view_score = 7
    else:
        view_score = 4
    
    # 相关度评分（权重15%）
    relevance_score = 0
    if major_name in title:
        relevance_score += 8
    if "专业" in title or "介绍" in title or "解读" in title:
        relevance_score += 7
    
    total_score = coverage_score + duration_score + view_score + relevance_score
    return total_score
```

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
  "major_name": "人工智能",
  "total_results": 10,
  "video": {
    "bvid": "BV1xxx",
    "title": "人工智能专业介绍",
    "description": "...",
    "cover": "https://...",
    "duration": 250,
    "author": "UP主名",
    "view_count": 10000,
    "pubdate": 1700000000,
    "url": "https://www.bilibili.com/video/BV1xxx",
    "score": 85.5
  }
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
