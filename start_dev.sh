#!/bin/bash
echo "=== 关闭所有服务 ==="
docker-compose -f ./docker-compose-dev.yml down
echo "✅ 所有 Docker 服务已关闭"


echo "=== 启动开发环境 ==="

# 1. 基础设施
docker-compose -f ./docker-compose-dev.yml up -d
echo "✅ Docker 服务已启动"

# 2. 前端（后台）
cd frontend/web
npm run dev &
echo "✅ 前端已启动: http://localhost:3000"

# 3. 网关（后台）
cd ../../backend/api-gateway
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
echo "✅ API 网关已启动: http://localhost:8000"

# 4. 其他服务（后台）
cd ../user-service
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload &
echo "✅ 用户服务已启动: http://localhost:8001"

cd ../chat-service
uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload &
echo "✅ 聊天服务已启动: http://localhost:8003"

cd ../voice-service
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload &
echo "✅ 语音服务已启动: http://localhost:8002"

cd ../recommendation-service
uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload &
echo "✅ 推荐服务已启动: http://localhost:8005"

cd ../analytics-service
uvicorn src.main:app --host 0.0.0.0 --port 8006 --reload &
echo "✅ 分析服务已启动: http://localhost:8006"

cd ../crawler-service
uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload &
echo "✅ 爬虫服务已启动: http://localhost:8004"

# 其他服务...

echo ""
echo "=== 所有服务已启动 ==="
echo "访问: http://localhost (Nginx 代理)"
echo ""

# 等待所有后台进程
wait