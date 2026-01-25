#!/usr/bin/env python3
"""
端口管理脚本 - 确保所有服务使用固定端口
根据需求设计文档中的端口规范统一管理所有服务端口
"""

import os
import json
import subprocess
import sys
from typing import Dict, List

# 固定端口配置（来自需求设计文档）
PORT_CONFIG = {
    "database": {
        "postgresql": 5432,
        "redis": 6379,
        "elasticsearch": 9200
    },
    "infrastructure": {
        "nginx": 80,
        "minio": 9000,
        "kafka": 9092
    },
    "backend": {
        "api-gateway": 8000,
        "user-service": 8001,
        "recommendation-service": 8002,
        "major-service": 8003,
        "market-data-service": 8004,
        "university-service": 8005,
        "chat-service": 8006,
        "voice-service": 8007,
        "crawler-service": 8008,
        "document-service": 8009,
        "video-service": 8010,
        "analytics-service": 8011
    },
    "frontend": {
        "web": 3000,
        "mobile": 19000
    }
}

def check_port_usage(port: int) -> bool:
    """检查端口是否被占用"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def get_process_on_port(port: int) -> str:
    """获取占用端口的进程信息"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return ""

def kill_process_on_port(port):
    """终止占用端口的进程"""
    try:
        processes = get_process_on_port(port).split('\n')
        killed_count = 0
        for process_line in processes:
            if process_line.strip():
                parts = process_line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    try:
                        subprocess.run(['kill', '-9', pid])
                        killed_count += 1
                        print(f"✅ 已终止占用端口 {port} 的进程 {pid}")
                    except:
                        pass
        return killed_count > 0
    except:
        return False

def check_all_ports() -> Dict[str, any]:
    """检查所有端口的使用情况"""
    issues = []
    
    for category, services in PORT_CONFIG.items():
        for service_name, port in services.items():
            if check_port_usage(port):
                process_info = get_process_on_port(port)
                issues.append({
                    "category": category,
                    "service": service_name,
                    "port": port,
                    "status": "occupied",
                    "process": process_info
                })
    
    return {
        "total_issues": len(issues),
        "issues": issues
    }

def cleanup_conflicts() -> Dict[str, any]:
    """清理端口冲突"""
    results = {
        "killed_processes": [],
        "failed_kills": [],
        "total_attempted": 0
    }
    
    for category, services in PORT_CONFIG.items():
        for service_name, port in services.items():
            if check_port_usage(port):
                results["total_attempted"] += 1
                killed_result = kill_process_on_port(port)
                if killed_result:
                    results["killed_processes"].append({
                        "service": service_name,
                        "port": port
                    })
                else:
                    results["failed_kills"].append({
                        "service": service_name,
                        "port": port
                    })
    
    return results

def generate_port_config() -> str:
    """生成端口配置文件"""
    config = {
        "version": "1.0.0",
        "last_updated": "2026-01-25",
        "services": PORT_CONFIG,
        "rules": {
            "fixed_ports": True,
            "conflict_check": True,
            "auto_restart_on_conflict": False
        }
    }
    
    return json.dumps(config, indent=2, ensure_ascii=False)

def save_port_config():
    """保存端口配置到文件"""
    config_path = "backend/config/ports.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(generate_port_config())
    
    print(f"✅ 端口配置已保存到: {config_path}")

def generate_frontend_config():
    """生成前端API配置"""
    frontend_config = {
        "API_BASE_URL": "http://localhost:8000",
        "SERVICES": {
            "MAJOR_DETAIL": "http://localhost:8003",
            "MARKET_DATA": "http://localhost:8004",
            "RECOMMENDATION": "http://localhost:8002",
            "UNIVERSITY": "http://localhost:8005",
            "CHAT": "http://localhost:8006",
            "VOICE": "http://localhost:8007"
        }
    }
    
    # TypeScript接口格式
    typescript_config = """// 前端统一API配置 - 根据需求设计文档端口规范
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',  // API网关
  SERVICES: {
    MAJOR_DETAIL: 'http://localhost:8003',     // 专业详情
    MARKET_DATA: 'http://localhost:8004',      // 专业行情
    RECOMMENDATION: 'http://localhost:8002',   // 推荐服务
    UNIVERSITY: 'http://localhost:8005',       // 大学推荐
    CHAT: 'http://localhost:8006',          // 对话服务
    VOICE: 'http://localhost:8007'          // 语音服务
  }
};
"""
    
    return typescript_config

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/ports.py check      # 检查端口状态")
        print("  python scripts/ports.py cleanup   # 清理端口冲突")
        print("  python scripts/ports.py generate   # 生成配置文件")
        print("  python scripts/ports.py all       # 执行所有检查")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        print("🔍 检查端口使用状态...")
        result = check_all_ports()
        
        if result["total_issues"] <= 0:
            print("✅ 所有端口都未被占用")
        else:
            print(f"⚠️  发现 {result['total_issues']} 个端口冲突:")
            for issue in result["issues"]:
                print(f"  - {issue['category']}.{issue['service']}: 端口 {issue['port']} 被占用")
    
    elif command == "cleanup":
        print("🧹 清理端口冲突...")
        result = cleanup_conflicts()
        
        print(f"📊 清理结果:")
        print(f"  - 尝试清理: {result['total_attempted']} 个端口")
        print(f"  - 成功终止: {len(result['killed_processes'])} 个进程")
        print(f"  - 清理失败: {len(result['failed_kills'])} 个端口")
        
        if result["killed_processes"]:
            print("✅ 成功清理的进程:")
            for killed in result["killed_processes"]:
                print(f"  - {killed['service']}: 端口 {killed['port']}")
        
        if result["failed_kills"]:
            print("❌ 清理失败的端口:")
            for failed in result["failed_kills"]:
                print(f"  - {failed['service']}: 端口 {failed['port']}")
    
    elif command == "generate":
        print("📝 生成端口配置文件...")
        save_port_config()
        
        print("📝 生成前端API配置...")
        frontend_config = generate_frontend_config()
        
        frontend_path = "frontend/web/src/config/ports.ts"
        os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
        
        with open(frontend_path, 'w', encoding='utf-8') as f:
            f.write(frontend_config)
        
        print(f"✅ 前端配置已保存到: {frontend_path}")
    
    elif command == "all":
        print("🔄 执行完整的端口管理流程...")
        main_check = check_all_ports()
        
        if main_check["total_issues"] > 0:
            print("发现端口冲突，开始清理...")
            cleanup_result = cleanup_conflicts()
        
        print("生成配置文件...")
        save_port_config()
        
        frontend_config = generate_frontend_config()
        frontend_path = "frontend/web/src/config/ports.ts"
        os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
        
        with open(frontend_path, 'w', encoding='utf-8') as f:
            f.write(frontend_config)
        
        print("✅ 端口管理流程完成!")
    
    else:
        print(f"❌ 未知命令: {command}")
        main()

if __name__ == "__main__":
    main()