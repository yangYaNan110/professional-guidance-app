#!/bin/bash

echo "========================================"
echo "  就业指导应用 - 一键启动脚本"
echo "========================================"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装"
    exit 1
fi

# 切换到项目目录
cd "$(dirname "$0")"

echo "🚀 启动基础设施服务..."
echo ""

# 启动基础设施
docker-compose -f docker/docker-compose.infra.yml up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
docker-compose -f docker/docker-compose.infra.yml ps

echo ""
echo "✅ 基础设施启动完成！"
echo ""
echo "服务访问地址："
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Elasticsearch: localhost:9200"
echo "  - MinIO: localhost:9000 (控制台: localhost:9001)"
echo "  - Kafka: localhost:9092"
echo "  - Prometheus: localhost:9090"
echo "  - Grafana: localhost:3000 (admin/admin)"
echo ""
echo "📝 下一步："
echo "  1. 启动后端服务: cd backend && pip install -r requirements.txt"
echo "  2. 启动前端服务: cd frontend/web && npm install && npm run dev"
echo ""
