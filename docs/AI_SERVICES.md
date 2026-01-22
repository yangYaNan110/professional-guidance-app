# 就业指导应用 - 集成GPT-4和语音服务

本文档说明如何配置和使用集成的高级功能。

## 目录

1. [GPT-4对话引擎](#gpt-4对话引擎)
2. [语音识别(Whisper)](#语音识别whisper)
3. [语音合成(ElevenLabs)](#语音合成elevenlabs)
4. [API接口](#api接口)
5. [配置说明](#配置说明)

---

## GPT-4对话引擎

### 概述

对话服务已集成OpenAI GPT-4模型，提供智能、专业的职业指导对话能力。

### 系统特点

- **专业角色**：职业顾问助手
- **心理支持**：理解用户情绪，提供温暖回应
- **智能引导**：通过提问帮助用户思考
- **上下文理解**：维护多轮对话历史

### 系统提示示例

```
你是就业指导应用的专业职业顾问助手。你的任务是：

1. 心理支持 - 理解用户的职业困惑和焦虑，给予温暖、支持的回应
2. 专业引导 - 通过提问引导用户思考，而不是直接给答案
3. 共情表达 - 理解用户的情绪，用真诚、关心的语气交流
4. 信息提供 - 提供就业市场信息、岗位要求、技能建议
5. 鼓励支持 - 帮助用户建立自信，看到自己的优势
```

---

## 语音识别(Whisper)

### 概述

使用OpenAI Whisper模型进行高质量的语音识别。

### 支持的格式

- MP3
- WAV
- OGG
- WebM (来自浏览器录音)

### 使用方式

```bash
# API调用示例
curl -X POST http://localhost:8003/api/v1/voice/stt \
  -H "Content-Type: audio/mp3" \
  --data-binary @recording.mp3
```

### 响应

```json
{
  "text": "我想找一份Python开发的工作"
}
```

---

## 语音合成(ElevenLabs)

### 概述

使用ElevenLabs提供自然、高质量的语音合成服务。

### 特点

- 自然流畅的语音
- 支持多种声音风格
- 可调节语速和情感
- 低延迟响应

### 使用方式

```bash
# API调用示例
curl -X POST http://localhost:8003/api/v1/voice/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "您好！我是您的职业发展助手，很高兴为您服务。",
    "voice_id": "21m00Tcm4TlvDq8ikWAM"
  }'
```

### 可选声音

| 声音ID | 描述 |
|-------|------|
| 21m00Tcm4TlvDq8ikWAM | 默认男声 |
| AZnzlk1XvdvUeBsqxVgV | 清晰女声 |
| nPczCjz82KWdKScP46B1 | 温和女声 |

---

## API接口

### 对话接口

#### 发送消息

```http
POST /api/v1/chat/message
Content-Type: application/json

{
  "user_id": "user-123",
  "message": "我想找Python开发的工作",
  "conversation_id": "conv-456",  // 可选
  "use_voice": false  // 是否返回语音
}
```

**响应**

```json
{
  "conversation_id": "conv-456",
  "reply": {
    "id": "msg-789",
    "role": "assistant",
    "content": "您好！很高兴您对Python开发感兴趣。Python是一门非常受欢迎的语言...\n\n能告诉我您目前的学习或工作经历吗？这样我可以更好地帮您规划。",
    "audio_url": null,
    "emotion": "supportive",
    "created_at": "2024-01-22T10:00:00Z"
  },
  "suggestions": [
    "分享您的学习经历",
    "说说您的技能优势",
    "问行业发展趋势"
  ]
}
```

#### 创建对话

```http
POST /api/v1/chat/conversations?user_id=user-123
Content-Type: application/json

{
  "title": "职业规划咨询"
}
```

#### 获取对话历史

```http
GET /api/v1/chat/conversations?user_id=user-123
```

#### 获取消息列表

```http
GET /api/v1/chat/conversations/{conversation_id}/messages
```

### 语音接口

#### 语音识别(音频转文字)

```http
POST /api/v1/voice/stt
Content-Type: audio/mp3

--audio_data--
```

#### 语音合成(文字转音频)

```http
POST /api/v1/voice/tts
Content-Type: application/json

{
  "text": "您好！我是您的职业发展助手。",
  "voice_id": "21m00Tcm4TlvDq8ikWAM"
}
```

---

## 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# OpenAI API密钥（必需）
OPENAI_API_KEY=your_openai_api_key

# ElevenLabs API密钥（必需）
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# 默认语音ID（可选）
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### 获取API密钥

#### OpenAI

1. 访问 https://platform.openai.com/api-keys
2. 创建新的API密钥
3. 确保账户有GPT-4访问权限

#### ElevenLabs

1. 访问 https://elevenlabs.io/api
2. 复制API密钥
3. 可选：创建自定义声音

### 成本说明

| 服务 | 计费方式 | 估算成本 |
|-----|---------|---------|
| GPT-4 | 按token | $0.03/1K输入tokens, $0.06/1K输出tokens |
| Whisper | 按分钟 | $0.006/分钟 |
| ElevenLabs | 按字符 | $0.003/字符 (免费层: 10K字符/月) |

---

## 错误处理

### 常见错误

| 错误码 | 说明 | 处理方式 |
|-------|------|---------|
| 401 | API密钥无效 | 检查环境变量配置 |
| 429 | 请求频率超限 | 降低请求频率 |
| 500 | 服务内部错误 | 查看服务器日志 |

### 降级策略

当AI服务不可用时，系统会：
1. 返回预置的默认回复
2. 标记消息为"fallback"类型
3. 记录错误日志便于排查

---

## 性能优化

### 缓存策略

- 对话历史：Redis缓存（1小时）
- 语音识别结果：缓存24小时
- 用户画像：长期缓存

### 响应优化

- 流式响应（可选）
- 异步处理长时间任务
- CDN加速静态资源

---

## 安全考虑

### 数据保护

- 不持久化音频数据
- 对话记录加密存储
- 符合GDPR要求

### 访问控制

- JWT Token认证
- API请求频率限制
- 输入内容过滤
