#!/usr/bin/env python3
"""测试场景A推荐分组逻辑"""
import sys
import os

# 添加项目根目录到路径
sys.path.append('/Users/yangyanan/yyn/opencode/08_demo/backend/recommendation-service/src')

from university_recommendation import recommend_scenario_a

def test_scenario_a():
    """测试场景A推荐逻辑"""
    
    print("=== 测试场景A推荐分组逻辑 ===")
    print("输入参数:")
    print("  专业: 计算机科学与技术")
    print("  省份: 江苏省") 
    print("  分数: 620")
    print("  限制: 5")
    print()
    
    try:
        result = recommend_scenario_a("计算机科学与技术", "江苏省", 620, 5)
        
        print("推荐结果:")
        print(f"  场景: {result.get('scenario')}")
        print(f"  总数: {result.get('total')}")
        print(f"  成功: {result.get('success')}")
        print()
        
        groups = result.get('groups', {})
        print("分组结果:")
        
        for group_key, group_data in groups.items():
            print(f"  {group_key}:")
            print(f"    名称: {group_data.get('name')}")
            print(f"    数量: {group_data.get('count')}")
            print(f"    描述: {group_data.get('description')}")
            print(f"    大学: {[uni.get('name') for uni in group_data.get('universities', [])[:2]]}...")
            print()
            
        print("✅ 测试成功：场景A分组逻辑正常工作")
        
        # 验证新分组结构
        if "province_score_match" in groups and "national_score_match" in groups:
            print("✅ 分组拆分成功：同省分数匹配 + 全国分数匹配")
        else:
            print("❌ 分组拆分失败：缺少期望的分组")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scenario_a()