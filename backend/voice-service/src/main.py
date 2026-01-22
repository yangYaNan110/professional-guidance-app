"""语音服务主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="语音服务",
    description="就业指导应用 - 语音识别和合成服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "voice-service"}

@app.post("/api/v1/voice/stt")
async def speech_to_text(audio_data: bytes):
    """语音识别"""
    return {"text": "示例文本"}

@app.post("/api/v1/voice/tts")
async def text_to_speech(text: str):
    """语音合成"""
    return {"audio_url": "/audio/example.mp3"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
