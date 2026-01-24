"""API网关 - 专业选择指导应用"""
import os
import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import redis
import jwt
from pydantic import BaseModel
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="专业选择指导应用 API网关",
    description="智能专业选择指导应用 - API网关服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception as e:
    logger.warning(f"Redis连接失败: {e}")
    redis_client = None

RATE_LIMIT = 100
RATE_LIMIT_WINDOW = 60

SERVICE_URLS = {
    "user-service": "http://localhost:8001",
    "chat-service": "http://localhost:8003",
    "voice-service": "http://localhost:8002",
    "recommendation-service": "http://localhost:8005",
    "analytics-service": "http://localhost:8006",
    "crawler-service": "http://localhost:8004",
}

class RateLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(status_code=429, detail="请求过于频繁，请稍后再试")

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的Token")

def get_current_user(token: str = None) -> Optional[Dict]:
    if token is None:
        return None
    try:
        return verify_token(token)
    except HTTPException:
        return None

def check_rate_limit(user_id: str = "anonymous") -> bool:
    if redis_client is None:
        return True
    key = f"rate_limit:{user_id}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, RATE_LIMIT_WINDOW)
    return current <= RATE_LIMIT

async def proxy_request(
    service_name: str,
    method: str,
    path: str,
    data: Dict = None,
    headers: Dict = None
) -> Dict:
    base_url = SERVICE_URLS.get(service_name)
    if not base_url:
        raise HTTPException(status_code=502, detail=f"未知服务: {service_name}")
    
    url = f"{base_url}{path}"
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=data)
            else:
                response = await client.post(url, json=data, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"服务调用失败 {service_name}: {e}")
            raise HTTPException(status_code=502, detail=f"服务不可用: {service_name}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
        return response
    except Exception as e:
        logger.error(f"请求处理错误: {e}")
        raise

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    user_id = "anonymous"
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        user = get_current_user(token)
        if user:
            user_id = f"user:{user.get('user_id', 'unknown')}"
    
    if not check_rate_limit(user_id):
        raise RateLimitExceeded()
    
    return await call_next(request)

@app.get("/health")
async def health_check():
    services_status = {}
    for name, url in SERVICE_URLS.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=2.0)
                services_status[name] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception:
            services_status[name] = "unreachable"
    
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services_status
    }

@app.get("/")
async def root():
    return {
        "message": "专业选择指导应用 API网关",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def api_health():
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/api/v1/auth/register")
async def auth_register(request: Request):
    return await proxy_request("user-service", "POST", "/api/v1/auth/register", await request.json())

@app.post("/api/v1/auth/login")
async def auth_login(request: Request):
    return await proxy_request("user-service", "POST", "/api/v1/auth/login", await request.json())

@app.post("/api/v1/auth/logout")
async def auth_logout():
    return await proxy_request("user-service", "POST", "/api/v1/auth/logout")

@app.get("/api/v1/users/profile")
async def get_user_profile():
    return await proxy_request("user-service", "GET", "/api/v1/users/profile")

@app.put("/api/v1/users/profile")
async def update_user_profile(request: Request):
    return await proxy_request("user-service", "PUT", "/api/v1/users/profile", await request.json())

@app.post("/api/v1/chat/conversation")
async def create_conversation(request: Request):
    return await proxy_request("chat-service", "POST", "/api/v1/chat/conversation", await request.json())

@app.get("/api/v1/chat/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    return await proxy_request("chat-service", "GET", f"/api/v1/chat/conversation/{conversation_id}")

@app.post("/api/v1/chat/message")
async def send_message(request: Request):
    return await proxy_request("chat-service", "POST", "/api/v1/chat/message", await request.json())

@app.get("/api/v1/major/categories")
async def get_major_categories():
    return await proxy_request("crawler-service", "GET", "/api/v1/major/categories")

@app.get("/api/v1/major/market-data")
async def get_major_market_data(request: Request):
    params = dict(request.query_params)
    return await proxy_request("crawler-service", "GET", "/api/v1/major/market-data", params)

@app.get("/api/v1/major/market-data/stats")
async def get_major_market_stats():
    return await proxy_request("crawler-service", "GET", "/api/v1/major/market-data/stats")

@app.get("/api/v1/major/{major_id}/detail")
async def get_major_detail(major_id: str):
    return await proxy_request("crawler-service", "GET", f"/api/v1/major/{major_id}/detail")

@app.get("/api/v1/universities/recommend")
async def get_recommended_universities(request: Request):
    params = dict(request.query_params)
    return await proxy_request("crawler-service", "GET", "/api/v1/universities/recommend", params)

@app.get("/api/v1/hot-news")
async def get_hot_news(request: Request):
    params = dict(request.query_params)
    return await proxy_request("crawler-service", "GET", "/api/v1/hot-news", params)

@app.post("/api/v1/crawler/crawl")
async def trigger_crawl(request: Request):
    return await proxy_request("crawler-service", "POST", "/api/v1/crawler/crawl", await request.json())

@app.post("/api/v1/crawler/reset-and-seed")
async def reset_and_seed():
    return await proxy_request("crawler-service", "POST", "/api/v1/crawler/reset-and-seed")

@app.post("/api/v1/auth/login")
async def auth_login(request: Request):
    return await proxy_request("user-service", "POST", "/api/v1/auth/login", await request.json())

@app.get("/api/v1/users/me")
async def get_current_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    token = auth_header[7:]
    return await proxy_request("user-service", "GET", "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

@app.put("/api/v1/users/profile")
async def update_profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    return await proxy_request("user-service", "PUT", "/api/v1/users/profile", await request.json(), headers={"Authorization": auth_header})

@app.post("/api/v1/chat/conversations")
async def create_conversation(request: Request):
    data = await request.json()
    return await proxy_request("chat-service", "POST", "/api/v1/chat/conversations", data)

@app.get("/api/v1/chat/conversations")
async def get_conversations(request: Request):
    params = dict(request.query_params)
    return await proxy_request("chat-service", "GET", "/api/v1/chat/conversations", params)

@app.get("/api/v1/chat/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    return await proxy_request("chat-service", "GET", f"/api/v1/chat/conversations/{conversation_id}/messages")

@app.post("/api/v1/chat/message")
async def send_message(request: Request):
    return await proxy_request("chat-service", "POST", "/api/v1/chat/message", await request.json())

@app.post("/api/v1/voice/stt")
async def speech_to_text(request: Request):
    audio_data = await request.body()
    return await proxy_request("voice-service", "POST", "/api/v1/voice/stt", {"audio_data": audio_data.hex()})

@app.post("/api/v1/voice/tts")
async def text_to_speech(request: Request):
    return await proxy_request("voice-service", "POST", "/api/v1/voice/tts", await request.json())

@app.get("/api/v1/recommendations")
async def get_recommendations(request: Request):
    params = dict(request.query_params)
    return await proxy_request("recommendation-service", "GET", "/api/v1/recommendations", params)

@app.get("/api/v1/analytics/trends")
async def get_trends(request: Request):
    params = dict(request.query_params)
    return await proxy_request("analytics-service", "GET", "/api/v1/analytics/trends", params)

@app.post("/api/v1/crawler/crawl")
async def trigger_crawl(request: Request):
    return await proxy_request("crawler-service", "POST", "/api/v1/crawler/crawl", await request.json())

@app.post("/api/v1/crawler/reset-and-seed")
async def reset_and_seed():
    return await proxy_request("crawler-service", "POST", "/api/v1/crawler/reset-and-seed")

@app.get("/api/v1/universities/recommend")
async def get_recommended_universities(request: Request):
    params = dict(request.query_params)
    return await proxy_request("crawler-service", "GET", "/api/v1/universities/recommend", params)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
