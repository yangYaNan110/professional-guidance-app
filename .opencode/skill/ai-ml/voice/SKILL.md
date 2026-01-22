---
name: ai-voice
description: 语音处理开发，包括ASR和TTS集成
license: MIT
compatibility: opencode
---

## 我做什么

负责语音处理模块的开发，包括语音识别（ASR）和语音合成（TTS）的集成和优化。

## 使用场景

- 语音识别功能开发
- 语音合成功能开发
- 语音交互优化

## 输入格式

```json
{
  "asr_config": {
    "language": "zh-CN",
    "enable_punctuation": true
  },
  "tts_config": {
    "voice_style": "friendly",
    "speed": 1.0
  }
}
```

## 输出格式

```json
{
  "files_created": [],
  "asr_service": {},
  "tts_service": {},
  "audio_processor": {},
  "stream_handler": {},
  "tests_written": [],
  "performance_report": {}
}
```

## 执行流程

1. 集成ASR服务
2. 集成TTS服务
3. 实现音频预处理
4. 实现流式处理
5. 优化响应延迟
6. 编写测试用例

## 注意事项

- 优化端到端延迟
- 处理网络不稳定
- 支持多语言切换
- 控制TTS成本

## 推荐模型

- 语音集成：`anthropic/claude-opus-4-20240307`
