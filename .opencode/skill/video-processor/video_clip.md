# video-clip Skill - 视频智能剪辑

## 功能描述

根据视频内容和剪辑脚本，自动剪辑生成精短视频片段，支持多片段组合和效果添加。

## 触发词

剪辑、裁剪、片段、剪辑视频、提取精华

## 核心能力

1. 根据时间戳自动剪辑视频
2. 多片段组合输出
3. 视频转码和压缩
4. 字幕添加和水印处理

---

## 剪辑目标

| 目标 | 说明 |
|-----|------|
| 时长控制 | 最终输出3-5分钟 |
| 内容精华 | 保留核心知识点 |
| 逻辑完整 | 保持内容连贯性 |

---

## 片段选择标准

| 标准 | 要求 |
|-----|------|
| 知识点密度 | 选择信息量大的片段 |
| 讲解质量 | 选择讲解清晰的部分 |
| 技术可行性 | 确保片段边界清晰 |
| 内容完整性 | 覆盖主要知识点 |

---

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| bvid | string | 是 | B站视频ID |
| clips | array | 是 | 剪辑片段列表 |
| output_format | string | 否 | 输出格式（mp4/webm） |
| output_duration | int | 否 | 输出时长限制 |

---

## 剪辑脚本格式

```json
{
  "bvid": "BV1xxx",
  "clips": [
    {
      "start": 0,
      "end": 195,
      "content": "开场介绍视频背景和主题",
      "label": "开场"
    },
    {
      "start": 510,
      "end": 765,
      "content": "核心概念详细讲解",
      "label": "核心内容"
    }
  ],
  "total_duration": 1200,
  "output_duration": 300
}
```

---

## 输出格式

```json
{
  "success": true,
  "bvid": "BV1xxx",
  "clips_count": 3,
  "output_duration": 300,
  "output_url": "https://...",
  "thumbnails": ["https://...", "https://..."]
}
```

---

## 使用示例

```python
from video_clip import VideoClipper

clipper = VideoClipper()

# 剪辑视频
result = clipper.clip(
    bvid="BV1xxx",
    clips=[
        {"start": 0, "end": 195, "label": "开场"},
        {"start": 510, "end": 765, "label": "核心内容"}
    ],
    output_duration=300
)

print(result.success)
print(result.output_url)
```

---

## 与其他Skill的配合

- **video-summary**：根据摘要结果生成剪辑脚本
- **video-search**：搜索目标视频后进行剪辑
- **video-analyze**：分析视频内容确定剪辑点
