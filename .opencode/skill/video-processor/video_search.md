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
    
    # 1. 从B站搜索热点视频（按最新发布时间排序）
    bilibili_events = await search_bilibili_hot(major_name)
    all_events.extend(bilibili_events)
    
    # 2. 从微博热搜搜索
    weibo_events = await search_weibo_hot(major_name)
    all_events.extend(weibo_events)
    
    # 3. 从今日头条搜索
    toutiao_events = await search_toutiao_hot(major_name)
    all_events.extend(toutiao_events)
    
    # 4. 从腾讯新闻搜索
    qq_news_events = await search_qqnews_hot(major_name)
    all_events.extend(qq_news_events)
    
    # 去重并按时间+热度排序（最新在前）
    unique_events = deduplicate_by_title(all_events)
    unique_events.sort(key=lambda x: (x.get("pub_date", ""), x.get("heat_index", 0)), reverse=True)
    
    # 只保留最近180天的内容
    unique_events = filter_events_by_days(unique_events, days=180)
    
    return unique_events[:15]
```

### 行业大佬动态规则

**核心原则：查找热点时，多关注领域大佬的动态和新闻**

#### 行业大佬关键词库

| 专业领域 | 行业大佬/公司 | 关键词 |
|---------|-------------|--------|
| **人工智能** | 黄仁勋（Jensen Huang）、马斯克（Elon Musk） | "人工智能 黄仁勋"、"人工智能 马斯克"、"AI Agent" |
| | OpenAI、英伟达（NVIDIA） | "人工智能 OpenAI"、"人工智能 英伟达"、"AI GPT" |
| | 月之暗面（MoonShot AI） | "人工智能 估值"、"AI Agent Skill" |
| **计算机科学** | 比尔·盖茨、扎克伯格 | "计算机 微软"、"Meta 最新" |
| **软件工程** | 马斯克、扎克伯格 | "软件 工程 特斯拉"、"代码 开源" |
| **自动驾驶/新能源** | 马斯克、李想、何小鹏 | "自动驾驶 特斯拉"、"新能源 车" |
| **生物医药** | 各大药企CEO | "医药 突破"、"创新药 研发" |

#### 行业动态关键词

| 关键词类型 | 示例 | 说明 |
|-----------|------|------|
| **技术突破** | "GPT-5发布"、"Agent能力提升" | 技术领域的重大进展 |
| **融资估值** | "估值创新高"、"融资10亿" | 公司发展动态 |
| **产品发布** | "新模型发布"、"新一代芯片" | 产品发布新闻 |
| **行业会议** | "世界AI大会"、"发布会" | 重要会议和活动 |
| **政策变化** | "新政策发布"、"行业规划" | 政策相关动态 |

#### 热点事件数据结构

**核心原则：热点内容不一定是视频，也可以是跳转到外部网页链接**

| 内容类型 | 说明 | 优先级 |
|---------|------|-------|
| 视频内容 | B站、YouTube等平台的视频 | 优先（带封面、时长、播放量） |
| 新闻资讯 | 知乎、36氪、虎嗅等平台的文章 | 优先（带阅读量、来源） |
| 社交动态 | 微博、小红书的热门讨论 | 次优（带讨论热度） |

```json
{
  "hot_video": {
    "title": "黄仁勋最新演讲：AI正在重塑整个行业",
    "description": "...",
    "cover": "https://...",
    "duration": 600,
    "author": "科技博主",
    "view_count": 100000,
    "pub_date": "2025-01-20",
    "url": "https://www.bilibili.com/video/BVxxx",
    "source": "B站",
    "is_video": true,
    "event_type": "重要会议"
  },
  "hot_events": [
    {
      "title": "月之暗面估值突破30亿美元，AI独角兽再添新成员",
      "description": "...",
      "view_count": 50000,
      "pub_date": "2025-01-19",
      "url": "https://36kr.com/p/xxx",
      "source": "36氪",
      "is_video": false,
      "event_type": "行业动态"
    },
    {
      "title": "马斯克发布新版FSD，宣称自动驾驶安全性提升10倍",
      "description": "...",
      "view_count": 80000,
      "pub_date": "2025-01-18",
      "url": "https://weibo.com/status/xxx",
      "source": "微博",
      "is_video": false,
      "event_type": "技术突破"
    }
  ]
}
```

#### 搜索关键词构建规则

```python
def build_hot_event_keywords(major_name: str) -> List[str]:
    """构建热点事件搜索关键词（包含行业大佬和关键术语）"""
    base_keywords = [
        f"{major_name} 2025",
        f"{major_name} 最新",
        f"{major_name} 热点",
        f"{major_name} 重大突破",
        f"{major_name} GPT",
        f"{major_name} DeepSeek",
        f"{major_name} Agent",
        f"AI {major_name} 2025"
    ]
    
    # 行业大佬关键词
    leader_keywords = [
        f"{major_name} 黄仁勋",
        f"{major_name} 马斯克",
        f"{major_name} Agent Skill",
        f"{major_name} 估值",
        f"{major_name} OpenAI",
        f"{major_name} 英伟达"
    ]
    
    return base_keywords + leader_keywords
```

#### 180天时间过滤规则

| 规则 | 说明 |
|-----|------|
| 时间范围 | 只保留最近180天的内容 |
| 排序方式 | 按时间倒序 + 热度加权 |
| 去重规则 | 标题相似度>80%视为重复 |
| 最低数量 | 返回最多15个热点事件 |

```python
def filter_events_by_days(events: List[Dict], days: int = 180) -> List[Dict]:
    """过滤指定天数内的事件"""
    now = datetime.now()
    cutoff = timedelta(days=days)
    filtered = []
    
    for event in events:
        pub_date = event.get("pub_date", "")
        if pub_date:
            try:
                event_date = datetime.strptime(pub_date, "%Y-%m-%d")
                if (now - event_date) <= cutoff:
                    filtered.append(event)
            except:
                # 如果日期解析失败，保留该事件
                filtered.append(event)
        else:
            # 没有日期信息的事件也保留
            filtered.append(event)
    
    return filtered
```

### 多数据源结构

| 数据源 | 内容类型 | 返回字段 | 优先级 |
|-------|---------|---------|--------|
| B站 | 视频 | title, cover, duration, author, play, url, is_video=True | 1 |
| 微博 | 热搜 | title, url, views, pub_date, is_video=False | 2 |
| 今日头条 | 新闻 | title, description, url, views, pub_date, is_video=False | 3 |
| 腾讯新闻 | 新闻 | title, description, url, views, pub_date, is_video=False | 4 |

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
