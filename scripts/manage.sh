#!/bin/bash

# ═══════════════════════════════════════════════════════════════
#  就业指导应用 - Docker Compose 一键管理脚本
# ═══════════════════════════════════════════════════════════════

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Docker Compose 文件
COMPOSE_FILE="${PROJECT_DIR}/docker/docker-compose.yml"
SIMPLE_COMPOSE_FILE="${PROJECT_DIR}/docker-compose.simple.yml"

echo_color() {
    echo -e "${2}${1}${NC}"
}

show_menu() {
    echo ""
    echo_color "╔══════════════════════════════════════════════════════╗" $BLUE
    echo_color "║         就业指导应用 - Docker 管理菜单              ║" $BLUE
    echo_color "╚══════════════════════════════════════════════════════╝" $BLUE
    echo ""
    echo_color "  1. 🚀  启动所有服务" $GREEN
    echo_color "  2. ⏸️  暂停所有服务" $YELLOW
    echo_color "  3. 🔄  重启所有服务" $BLUE
    echo_color "  4. 📊  查看服务状态" $GREEN
    echo_color "  5. 📝  查看日志" $YELLOW
    echo_color "  6. 🛑  停止并删除容器" $RED
    echo_color "  7. 🧹  清理数据(谨慎!)" $RED
    echo_color "  0. ❌  退出" $NC
    echo ""
    echo -n "  请选择 [0-7]: "
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo_color "❌ Docker未安装，请先安装Docker" $RED
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        echo_color "❌ Docker Compose未安装，请先安装" $RED
        exit 1
    fi
}

# 启动服务
start_services() {
    echo_color "\n🚀 启动服务中..." $GREEN
    
    cd "$PROJECT_DIR"
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" up -d
    elif [ -f "$SIMPLE_COMPOSE_FILE" ]; then
        docker-compose -f "$SIMPLE_COMPOSE_FILE" up -d
    else
        echo_color "❌ 未找到 docker-compose.yml 文件" $RED
        return 1
    fi
    
    echo ""
    echo_color "✅ 服务启动完成!" $GREEN
    echo ""
    echo_color "  访问地址:" $BLUE
    echo_color "    - 前端: http://localhost:3000" $NC
    echo_color "    - 后端API: http://localhost:8001" $NC
    echo ""
}

# 暂停服务
stop_services() {
    echo_color "\n⏸️ 暂停服务中..." $YELLOW
    
    cd "$PROJECT_DIR"
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" stop
    elif [ -f "$SIMPLE_COMPOSE_FILE" ]; then
        docker-compose -f "$SIMPLE_COMPOSE_FILE" stop
    fi
    
    echo_color "✅ 服务已暂停" $GREEN
    echo_color "  使用选项1可重新启动" $NC
}

# 重启服务
restart_services() {
    echo_color "\n🔄 重启服务中..." $BLUE
    stop_services
    sleep 2
    start_services
}

# 查看服务状态
status_services() {
    echo_color "\n📊 服务状态:" $GREEN
    echo ""
    
    cd "$PROJECT_DIR"
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" ps
    elif [ -f "$SIMPLE_COMPOSE_FILE" ]; then
        docker-compose -f "$SIMPLE_COMPOSE_FILE" ps
    else
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAME|postgres|redis|08_demo" || echo "  无运行中的服务"
    fi
}

# 查看日志
show_logs() {
    echo_color "\n📝 查看日志 (Ctrl+C 退出)" $YELLOW
    echo -n "  查看哪个服务? (直接回车查看全部): "
    read service
    
    cd "$PROJECT_DIR"
    
    if [ -z "$service" ]; then
        if [ -f "$COMPOSE_FILE" ]; then
            docker-compose -f "$COMPOSE_FILE" logs -f
        elif [ -f "$SIMPLE_COMPOSE_FILE" ]; then
            docker-compose -f "$SIMPLE_COMPOSE_FILE" logs -f
        fi
    else
        if [ -f "$COMPOSE_FILE" ]; then
            docker-compose -f "$COMPOSE_FILE" logs -f "$service"
        elif [ -f "$SIMPLE_COMPOSE_FILE" ]; then
            docker-compose -f "$SIMPLE_COMPOSE_FILE" logs -f "$service"
        fi
    fi
}

# 停止并删除容器
remove_services() {
    echo_color "\n🛑 停止并删除容器..." $RED
    echo -n "  确认? (输入 y 确认): "
    read confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        cd "$PROJECT_DIR"
        
        if [ -f "$COMPOSE_FILE" ]; then
            docker-compose -f "$COMPOSE_FILE" down
        elif [ -f "$SIMPLE_COMPOSE_FILE" ]; then
            docker-compose -f "$SIMPLE_COMPOSE_FILE" down
        fi
        
        echo_color "✅ 容器已删除" $GREEN
    else
        echo_color "  已取消" $NC
    fi
}

# 清理数据
cleanup_data() {
    echo_color "\n🧹 清理所有数据..." $RED
    echo -n "  这将删除所有数据! 确认? (输入 DELETE 确认): "
    read confirm
    
    if [ "$confirm" = "DELETE" ]; then
        cd "$PROJECT_DIR"
        
        # 删除Docker卷
        docker volume rm $(docker volume ls -q | grep -E "postgres|redis|08_demo") 2>/dev/null || true
        
        # 删除容器和网络
        if [ -f "$COMPOSE_FILE" ]; then
            docker-compose -f "$COMPOSE_FILE" down -v
        elif [ -f "$SIMPLE_COMPOSE_FILE" ]; then
            docker-compose -f "$SIMPLE_COMPOSE_FILE" down -v
        fi
        
        echo_color "✅ 数据已清理" $GREEN
    else
        echo_color "  已取消" $NC
    fi
}

# 主循环
main() {
    check_docker
    
    while true; do
        show_menu
        read choice
        
        case $choice in
            1) start_services ;;
            2) stop_services ;;
            3) restart_services ;;
            4) status_services ;;
            5) show_logs ;;
            6) remove_services ;;
            7) cleanup_data ;;
            0) 
                echo_color "\n👋 再见!" $BLUE
                exit 0
                ;;
            *)
                echo_color "\n❌ 无效选择，请重试" $RED
                ;;
        esac
        
        echo ""
        echo -n "按回车键继续..."
        read
    done
}

main
