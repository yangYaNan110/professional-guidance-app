#!/usr/bin/env python3
"""
专业推荐API快速测试脚本
用于验证API基本功能和响应格式
"""

import requests
import json
import sys
from typing import Dict, Any

# API服务配置
BASE_URL = "http://localhost:8005"
TIMEOUT = 10

def test_endpoint(endpoint: str, description: str, params: Dict[str, Any] | None = None) -> bool:
    """测试单个API端点"""
    print(f"\n🔍 测试: {description}")
    print(f"端点: {endpoint}")
    
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=TIMEOUT)
        
        print(f"状态码: {response.status_code}")
        
        # 检查响应头
        cache_header = response.headers.get("X-Cache")
        if cache_header:
            print(f"缓存头部: X-Cache: {cache_header}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON解析成功")
                print(f"响应键: {list(data.keys())}")
                
                # 美化输出前几行
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                lines = json_str.split('\n')
                for i, line in enumerate(lines[:10]):
                    print(line)
                if len(lines) > 10:
                    print("... (截断显示)")
                    
                return True
            except json.JSONDecodeError:
                print("❌ JSON解析失败")
                print(f"响应内容: {response.text[:200]}...")
                return False
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保API服务已启动")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 专业推荐API测试开始")
    print("=" * 50)
    
    # 测试用例列表
    test_cases = [
        {
            "endpoint": "/",
            "description": "根路径状态检查",
            "params": None
        },
        {
            "endpoint": "/api/v1/major/health",
            "description": "健康检查",
            "params": None
        },
        {
            "endpoint": "/api/v1/major/market-data",
            "description": "专业行情数据（默认查询）",
            "params": None
        },
        {
            "endpoint": "/api/v1/major/market-data",
            "description": "专业行情数据（工学分类）",
            "params": {"category": "工学", "page": 1, "page_size": 5}
        },
        {
            "endpoint": "/api/v1/major/market-data",
            "description": "专业行情数据（按就业率排序）",
            "params": {"sort_by": "employment_rate", "order": "desc", "page_size": 3}
        },
        {
            "endpoint": "/api/v1/data/categories",
            "description": "学科分类列表",
            "params": None
        },
        {
            "endpoint": "/api/v1/admin/optimization-sql",
            "description": "数据库优化SQL",
            "params": None
        }
    ]
    
    # 执行测试
    success_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        success = test_endpoint(
            test_case["endpoint"], 
            test_case["description"], 
            test_case["params"]
        )
        if success:
            success_count += 1
    
    # 测试结果汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查API服务")
        return 1

if __name__ == "__main__":
    # 使用说明
    print("专业推荐API快速测试脚本")
    print("请确保API服务已启动: python recommendation_api.py")
    print("或使用: uvicorn recommendation_api:app --host 0.0.0.0 --port 8005")
    print("\n按回车键开始测试...")
    input()
    
    # 执行测试
    exit_code = main()
    sys.exit(exit_code)