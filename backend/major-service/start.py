#!/usr/bin/env python3
"""
专业推荐API启动脚本
提供多种启动模式供选择
"""

import os
import sys
import argparse
import subprocess

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'psycopg2-binary',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def start_development():
    """启动开发模式"""
    print("🚀 启动开发模式...")
    cmd = [
        'uvicorn', 
        'recommendation_api:app',
        '--host', '0.0.0.0',
        '--port', '8005',
        '--reload',
        '--log-level', 'info'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 开发服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")

def start_production():
    """启动生产模式"""
    print("🚀 启动生产模式...")
    cmd = [
        'uvicorn', 
        'recommendation_api:app',
        '--host', '0.0.0.0',
        '--port', '8005',
        '--workers', '4',
        '--log-level', 'warning'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 生产服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")

def run_tests():
    """运行测试"""
    print("🧪 运行单元测试...")
    
    # 运行pytest测试
    try:
        result = subprocess.run([
            'pytest', 
            'test_recommendation_api.py', 
            '-v'
        ], check=True, capture_output=False)
        print("✅ 所有单元测试通过")
    except subprocess.CalledProcessError:
        print("❌ 单元测试失败")
        return False
    
    # 运行快速测试（如果服务已启动）
    print("\n🔍 运行API快速测试...")
    try:
        result = subprocess.run([
            'python', 
            'test_api_quick.py'
        ], check=True, timeout=30)
        print("✅ API快速测试通过")
    except subprocess.CalledProcessError:
        print("⚠️ API快速测试失败 - 请确保API服务已启动")
    except subprocess.TimeoutExpired:
        print("⏰ API快速测试超时")
    
    return True

def show_status():
    """显示服务状态"""
    print("📊 服务状态检查...")
    
    # 检查环境变量
    env_vars = {
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_NAME': os.getenv('DB_NAME', 'employment'),
        'DB_USER': os.getenv('DB_USER', 'postgres'),
        'DB_PASSWORD': '***' if os.getenv('DB_PASSWORD') else '未设置'
    }
    
    print("\n🔧 环境配置:")
    for key, value in env_vars.items():
        print(f"  {key}: {value}")
    
    # 检查数据库连接
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=env_vars['DB_HOST'],
            port=int(env_vars['DB_PORT']),
            database=env_vars['DB_NAME'],
            user=env_vars['DB_USER'],
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        conn.close()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
    
    # 检查API服务状态
    try:
        import requests
        response = requests.get('http://localhost:8005/', timeout=5)
        if response.status_code == 200:
            print("✅ API服务运行中")
        else:
            print(f"⚠️ API服务状态异常: {response.status_code}")
    except Exception:
        print("❌ API服务未运行")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='专业推荐API启动脚本')
    parser.add_argument('mode', 
                       choices=['dev', 'prod', 'test', 'status'],
                       help='运行模式')
    parser.add_argument('--skip-deps', 
                       action='store_true',
                       help='跳过依赖检查')
    
    args = parser.parse_args()
    
    print("🎯 专业推荐API管理脚本")
    print("=" * 40)
    
    # 基础检查
    check_python_version()
    if not args.skip_deps:
        if not check_dependencies():
            sys.exit(1)
    
    # 根据模式执行操作
    if args.mode == 'dev':
        start_development()
    elif args.mode == 'prod':
        start_production()
    elif args.mode == 'test':
        run_tests()
    elif args.mode == 'status':
        show_status()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("使用说明:")
        print("  python start.py dev     # 启动开发模式")
        print("  python start.py prod    # 启动生产模式")
        print("  python start.py test    # 运行测试")
        print("  python start.py status  # 检查状态")
        print("\n示例:")
        print("  python start.py dev     # 启动开发服务器")
        sys.exit(0)
    
    main()