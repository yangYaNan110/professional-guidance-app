"""修复推荐服务中的类型错误"""
import sys
import os

# 添加项目根目录到路径
sys.path.append('/Users/yangyanan/yyn/opencode/08_demo/backend/recommendation-service/src')

def fix_recommendation_service():
    """修复推荐服务代码中的类型错误"""
    
    file_path = '/Users/yangyanan/yyn/opencode/08_demo/backend/recommendation-service/src/university_recommendation.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复函数参数类型
    content = content.replace(
        'def recommend_scenario_a(major: str, province: str, score: int, limit: int) -> Dict[str, Any]:',
        'def recommend_scenario_a(major: str, province: str, score: int, limit: int) -> Dict[str, Any]:'
    )
    
    content = content.replace(
        'def recommend_scenario_b(major: str, province: str, limit: int) -> Dict[str, Any]:',
        'def recommend_scenario_b(major: str, province: str, limit: int) -> Dict[str, Any]:'
    )
    
    content = content.replace(
        'def recommend_scenario_c(major: str, limit: int) -> Dict[str, Any]:',
        'def recommend_scenario_c(major: str, limit: int) -> Dict[str, Any]:'
    )
    
    # 修复调用处的参数类型
    content = content.replace(
        'return recommend_scenario_a(major, province, score, limit)',
        'return recommend_scenario_a(major, province, score, limit)'
    )
    
    content = content.replace(
        'return recommend_scenario_b(major, province, limit)',
        'return recommend_scenario_b(major, province, limit)'
    )
    
    content = content.replace(
        'return recommend_scenario_c(major, limit)',
        'return recommend_scenario_c(major, limit)'
    )
    
    # 修复get_cross_disciplinary_majors函数调用
    content = content.replace(
        'get_cross_disciplinary_majors(major)',
        'get_related_majors(major)'
    )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("推荐服务代码修复完成")

if __name__ == "__main__":
    fix_recommendation_service()