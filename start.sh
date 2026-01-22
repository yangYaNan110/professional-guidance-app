#!/bin/bash

# 专业选择指导应用 - 一键启动脚本
# 用法: ./start.sh

set -e

echo "🎯 专业选择指导应用"
echo "===================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}警告: 未找到 Python3，请确保已安装 Python 3.11+${NC}"
fi

# 检查Node
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}警告: 未找到 Node.js，请确保已安装 Node 18+${NC}"
fi

echo -e "${BLUE}步骤 1/4: 启动数据库服务...${NC}"
# 启动Docker数据库（如果使用Docker）
if command -v docker &> /dev/null; then
    if docker ps | grep -q "postgres"; then
        echo "  PostgreSQL 已运行 ✓"
    else
        echo "  启动 PostgreSQL..."
        docker run -d --name major-postgres \
            -e POSTGRES_PASSWORD=postgres \
            -e POSTGRES_DB=employment \
            -p 5432:5432 \
            postgres:15-alpine 2>/dev/null || true
        echo "  PostgreSQL 已启动 ✓"
    fi
    
    if docker ps | grep -q "redis"; then
        echo "  Redis 已运行 ✓"
    else
        echo "  启动 Redis..."
        docker run -d --name major-redis \
            -p 6379:6379 \
            redis:7-alpine 2>/dev/null || true
        echo "  Redis 已启动 ✓"
    fi
else
    echo -e "${YELLOW}  未使用 Docker，请确保 PostgreSQL 和 Redis 已本地启动${NC}"
fi

echo ""
echo -e "${BLUE}步骤 2/4: 启动后端服务...${NC}"

# 启动用户服务
if lsof -i:8001 &> /dev/null; then
    echo "  User Service (8001) 已运行 ✓"
else
    echo "  启动 User Service..."
    cd backend/user-service
    nohup python src/main.py > /tmp/user-service.log 2>&1 &
    cd ../..
    echo "  User Service 已启动 ✓"
fi

# 启动对话服务
if lsof -i:8003 &> /dev/null; then
    echo "  Chat Service (8003) 已运行 ✓"
else
    echo "  启动 Chat Service..."
    cd backend/chat-service
    nohup python src/main.py > /tmp/chat-service.log 2>&1 &
    cd ../..
    echo "  Chat Service 已启动 ✓"
fi

echo ""
echo -e "${BLUE}步骤 3/4: 启动前端...${NC}"

# 启动前端
if lsof -i:3000 &> /dev/null; then
    echo "  Frontend (3000) 已运行 ✓"
else
    echo "  启动 Frontend..."
    cd frontend/web
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    cd ../..
    echo "  Frontend 已启动 ✓"
fi

echo ""
echo -e "${BLUE}步骤 4/4: 检查服务状态...${NC}"
sleep 2

# 检查服务
SERVICES=(
    "8001:User Service"
    "8003:Chat Service"
    "3000:Frontend"
)

all_ok=true
for item in "${SERVICES[@]}"; do
    port="${item%%:*}"
    name="${item##*:}"
    if lsof -i:$port &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $name ($port)"
    else
        echo -e "  ${YELLOW}✗${NC} $name ($port) - 未运行"
        all_ok=false
    fi
done

echo ""
if $all_ok; then
    echo -e "${GREEN}✅ 所有服务已启动！${NC}"
    echo ""
    echo "访问地址:"
    echo -e "  ${BLUE}Web应用:${NC} http://localhost:3000"
    echo -e "  ${BLUE}API文档:${NC} http://localhost:8001/docs"
    echo ""
    
    # 自动打开浏览器
    if command -v open &> /dev/null; then
        echo "正在打开浏览器..."
        open http://localhost:3000
    fi
else
    echo -e "${YELLOW}⚠ 部分服务未启动，请检查日志${NC}"
    echo ""
    echo "查看日志:"
    echo "  后端: tail -f /tmp/user-service.log /tmp/chat-service.log"
    echo "  前端: tail -f /tmp/frontend.log"
fi

echo ""
echo "停止服务: pkill -f 'python.*main.py' && pkill -f 'vite'"
