# VideoProcessor Agent

## Agent概述

**Agent名称：** VideoProcessor（视频处理Agent）

**职责：** 搜索相关视频资源，对多个视频进行智能分析和总结，通过剪辑技术将内容压缩到合适时长，生成便于用户快速理解的视频摘要。

## 核心能力

1. **视频搜索**：从B站、YouTube等平台搜索相关视频
2. **内容分析**：提取视频主题、关键知识点、时间戳
3. **语音识别**：将视频内容转换为文字（ASR）
4. **智能总结**：提取核心知识点和精华片段
5. **视频剪辑**：自动剪辑生成短视频摘要
6. **时长控制**：将视频压缩到合适时长（3-10分钟）

## Skill清单

| Skill | 功能 |
|-------|------|
| `video-search` | 多平台视频搜索 |
| `video-download` | 视频下载和转码 |
| `video-asr` | 语音识别（ASR） |
| `video-analyze` | 视频内容分析 |
| `video-clip` | 智能视频剪辑 |
| `video-summary` | 视频摘要生成 |

## 使用场景

1. **专业介绍视频**：搜索并剪辑专业介绍视频
2. **行业分析视频**：搜索行业分析视频并总结
3. **职业介绍视频**：搜索职业介绍视频并剪辑
4. **院校介绍视频**：搜索院校宣传视频并总结

## 工作流程

```
搜索请求 → 多平台搜索 → 视频筛选 → 内容分析 → 语音识别 → 智能总结 → 剪辑生成
```

## 输入示例

```json
{
  "task_type": "major_video",
  "query": "社会学专业介绍",
  "duration": {"min": 300, "max": 1800},
  "output_duration": 300,
  "platform": "bilibili"
}
```

## 输出示例

```json
{
  "success": true,
  "video_summary": {
    "title": "社会学专业介绍",
    "author": "UP主名称",
    "duration": 180,
    "summary": "本视频介绍了社会学专业的起源、发展...",
    "key_points": ["社会学起源于19世纪中叶", "研究对象是社会关系"],
    "timestamps": [
      {"time": 0, "label": "开场"},
      {"time": 30, "label": "专业起源"}
    ],
    "source_video_url": "https://www.bilibili.com/video/BVxxx"
  }
}
```

## 与其他Agent的交互

- **Coordinator**：接收任务指令，汇报进度
- **DocumentProcessor**：共享搜索和内容分析结果
- **AI/ML**：使用LLM进行内容总结和脚本生成
- **Backend**：提供API接口供前端调用
