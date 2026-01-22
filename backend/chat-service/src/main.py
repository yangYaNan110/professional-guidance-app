"""对话服务 - 集成GPT-4和语音"""
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, JSON, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
import json
import httpx
from openai import OpenAI

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== 数据库模型 ====================

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), default="新对话")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    audio_url = Column(String(500), nullable=True)
    emotion = Column(String(50), nullable=True)
    intent = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ==================== Pydantic模型 ====================

class MessageCreate(BaseModel):
    role: str
    content: str
    audio_url: Optional[str] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    audio_url: Optional[str]
    emotion: Optional[str]
    created_at: datetime

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    use_voice: bool = False

class ChatResponse(BaseModel):
    conversation_id: str
    reply: MessageResponse
    suggestions: List[str] = []

# ==================== OpenAI配置 ====================

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==================== 对话系统提示 ====================

COUNSELING_SYSTEM_PROMPT = """你是就业指导应用的专业职业顾问助手。你的任务是：

1. **心理支持** - 理解用户的职业困惑和焦虑，给予温暖、支持的回应
2. **专业引导** - 通过提问引导用户思考，而不是直接给答案
3. **共情表达** - 理解用户的情绪，用真诚、关心的语气交流
4. **信息提供** - 提供就业市场信息、岗位要求、技能建议
5. **鼓励支持** - 帮助用户建立自信，看到自己的优势

**交流风格**：
- 友好、温暖、专业
- 善于倾听和理解
- 适度使用鼓励性语言
- 分享有启发性的案例

**核心原则**：
- 不评判用户的困惑
- 帮助用户自己找到答案
- 提供具体、可行的建议
- 尊重用户的节奏和选择

请用中文回答，保持自然、流畅的对话风格。"""

# ==================== 对话引擎 ====================

class CounselingEngine:
    """职业指导对话引擎 - 集成GPT-4"""
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """使用GPT-4生成回复"""
        
        # 构建消息
        messages = [{"role": "system", "content": COUNSELING_SYSTEM_PROMPT}]
        
        # 添加对话历史（最近10轮）
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            
            content = response.choices[0].message.content
            
            # 分析用户情绪
            emotion = self._analyze_emotion(user_message)
            
            # 生成建议问题
            suggestions = self._generate_suggestions(user_message, content)
            
            return {
                "content": content,
                "emotion": emotion,
                "suggestions": suggestions
            }
            
        except Exception as e:
            print(f"GPT-4 API错误: {e}")
            return {
                "content": "抱歉，我现在有些困难。让我为您提供一些职业建议...\n\n关于您的困惑，我建议您可以：\n1. 先梳理自己的优势和兴趣\n2. 了解目标行业的要求\n3. 制定一个实际的行动计划",
                "emotion": "supportive",
                "suggestions": ["分享您的专业背景", "说说您的职业目标", "问行业发展趋势"]
            }
    
    def _analyze_emotion(self, message: str) -> str:
        """分析用户情绪"""
        message_lower = message.lower()
        
        anxiety_keywords = ["焦虑", "担心", "害怕", "迷茫", "不知道", "怎么办", "困惑"]
        frustration_keywords = ["挫折", "失败", "被拒", "沮丧", "累", "难", "烦"]
        confused_keywords = ["不太确定", "选择", "方向", "迷茫"]
        
        if any(kw in message_lower for kw in anxiety_keywords):
            return "anxious"
        elif any(kw in message_lower for kw in frustration_keywords):
            return "frustrated"
        elif any(kw in message_lower for kw in confused_keywords):
            return "confused"
        else:
            return "neutral"
    
    def _generate_suggestions(
        self,
        user_message: str,
        ai_response: str
    ) -> List[str]:
        """生成建议问题"""
        base_suggestions = [
            "能详细说说您的想法吗？",
            "您之前有过类似的想法吗？",
            "您对哪个方面最感兴趣？",
            "需要我帮您分析某个具体岗位吗？",
            "我们可以聊聊您的技能优势"
        ]
        
        # 根据用户消息内容添加针对性建议
        suggestions = base_suggestions.copy()
        
        message_lower = user_message.lower()
        
        if "工资" in message_lower or "薪资" in message_lower:
            suggestions.insert(0, "我可以帮您查询不同岗位的薪资范围")
        elif "技术" in message_lower or "技能" in message_lower:
            suggestions.insert(0, "您想了解哪些技能的需求情况？")
        elif "公司" in message_lower:
            suggestions.insert(0, "您对哪类公司感兴趣？")
        elif "城市" in message_lower or "地点" in message_lower:
            suggestions.insert(0, "您更倾向于在哪个城市发展？")
        
        return suggestions[:4]

# ==================== 语音处理 ====================

class VoiceProcessor:
    """语音处理器 - Whisper ASR + ElevenLabs TTS"""
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """使用Whisper将音频转为文字"""
        try:
            response = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=("audio.mp3", audio_data, "audio/mp3")
            )
            return response.text
        except Exception as e:
            print(f"语音识别错误: {e}")
            return ""
    
    async def synthesize_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    ) -> bytes:
        """使用ElevenLabs将文字转为语音"""
        try:
            response = openai_client.audio.speech.create(
                model="tts-1",
                voice=voice_id,
                input=text
            )
            return response.content
        except Exception as e:
            print(f"语音合成错误: {e}")
            return b""

# ==================== 依赖 ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_counseling_engine():
    return CounselingEngine()

def get_voice_processor():
    return VoiceProcessor()

# ==================== 路由 ====================

app = FastAPI(
    title="对话服务",
    description="专业选择指导应用 - 智能对话引擎服务（集成GPT-4）",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

counseling_engine = CounselingEngine()
voice_processor = VoiceProcessor()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chat-service-v2",
        "features": ["gpt-4", "voice"]
    }

@app.post("/api/v1/chat/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """创建对话会话"""
    conversation = Conversation(
        user_id=user_id,
        title=request.title or "新对话"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

@app.get("/api/v1/chat/conversations")
async def get_conversations(
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """获取用户的对话列表"""
    conversations = db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(Conversation.updated_at.desc())\
        .all()
    
    result = []
    for conv in conversations:
        last_msg = db.query(Message)\
            .filter(Message.conversation_id == conv.id)\
            .order_by(Message.created_at.desc())\
            .first()
        
        result.append({
            "id": conv.id,
            "title": conv.title,
            "status": conv.status,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "last_message": last_msg.content[:100] if last_msg else None
        })
    
    return result

@app.get("/api/v1/chat/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """获取对话消息"""
    messages = db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at.asc())\
        .all()
    
    return messages

@app.post("/api/v1/chat/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    engine: CounselingEngine = Depends(get_counseling_engine)
):
    """发送消息，获取GPT-4 AI回复"""
    
    # 1. 创建或获取会话
    if request.conversation_id:
        conversation = db.query(Conversation)\
            .filter(Conversation.id == request.conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
    else:
        conversation = Conversation(user_id=request.user_id, title="新对话")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # 2. 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    conversation.updated_at = datetime.utcnow()
    db.commit()
    
    # 3. 获取对话历史
    history = db.query(Message)\
        .filter(Message.conversation_id == conversation.id)\
        .order_by(Message.created_at.asc())\
        .all()
    
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]
    
    # 4. 调用GPT-4生成回复
    result = await engine.generate_response(
        request.message,
        conversation_history
    )
    
    # 5. 保存AI回复
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["content"],
        emotion=result["emotion"]
    )
    db.add(ai_message)
    db.commit()
    
    # 6. 如果需要语音，生成语音回复
    audio_url = None
    if request.use_voice:
        audio_data = await voice_processor.synthesize_speech(result["content"])
        if audio_data:
            # 保存音频文件（实际项目中应保存到对象存储）
            audio_url = f"/api/v1/chat/audio/{ai_message.id}"
    
    return {
        "conversation_id": conversation.id,
        "reply": {
            "id": ai_message.id,
            "role": "assistant",
            "content": result["content"],
            "audio_url": audio_url,
            "emotion": result["emotion"],
            "created_at": ai_message.created_at
        },
        "suggestions": result["suggestions"]
    }

@app.post("/api/v1/voice/stt")
async def speech_to_text(
    audio_data: bytes,
    voice_processor: VoiceProcessor = Depends(get_voice_processor)
):
    """语音识别 - Whisper"""
    text = await voice_processor.transcribe_audio(audio_data)
    return {"text": text}

@app.post("/api/v1/voice/tts")
async def text_to_speech(
    text: str,
    voice_id: str = Query("21m00Tcm4TlvDq8ikWAM"),
    voice_processor: VoiceProcessor = Depends(get_voice_processor)
):
    """语音合成 - ElevenLabs"""
    audio_data = await voice_processor.synthesize_speech(text, voice_id)
    return {"audio_data": audio_data.hex()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
