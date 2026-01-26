"""共享工具函数"""
import re
from typing import List, Optional
import uuid
from datetime import datetime

def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())

def generate_order_id() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random = uuid.uuid4().hex[:6].upper()
    return f"ORD{timestamp}{random}"

def parse_salary(salary_str: str) -> tuple:
    """
    解析薪资字符串
    例如: "20K-30K/月" -> (20000, 30000)
    """
    if not salary_str:
        return None, None
    
    # 移除空格和单位
    salary_str = salary_str.replace(" ", "").replace("K", "000")
    
    # 匹配范围
    match = re.search(r"(\d+)[万w]?-(\d+)[万w]?", salary_str, re.I)
    if match:
        min_salary = int(match.group(1)) * 10000
        max_salary = int(match.group(2)) * 10000
        return min_salary, max_salary
    
    # 匹配单一数值
    match = re.search(r"(\d+)[万w]?", salary_str, re.I)
    if match:
        salary = int(match.group(1)) * 10000
        return salary, salary
    
    return None, None

def format_salary(min_salary: Optional[int], max_salary: Optional[int]) -> str:
    """格式化薪资显示"""
    if min_salary and max_salary:
        if min_salary == max_salary:
            return f"{min_salary // 1000}K/月"
        return f"{min_salary // 1000}K-{max_salary // 1000}K/月"
    elif min_salary:
        return f"{min_salary // 1000}K+/月"
    elif max_salary:
        return f"~{max_salary // 1000}K/月"
    return "面议"

def extract_skills(text: str) -> List[str]:
    """从文本中提取技能关键词"""
    common_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
        "React", "Vue", "Angular", "Next.js", "Nuxt.js",
        "FastAPI", "Django", "Flask", "Spring", "Express", "NestJS",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Kafka",
        "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
        "AWS", "Azure", "GCP", "Tencent Cloud", "Aliyun",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "OpenCV",
        "NLP", "CV", "Machine Learning", "Deep Learning",
        "Git", "SVN", "Linux", "Apache",
        "TCP/IP", "HTTP", "HTTPS", "WebSocket", "REST", "GraphQL"
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """验证手机号格式（中国）"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def async_retry(max_retries: int = 3, delay: float = 1.0):
    """异步重试装饰器"""
    def decorator(func):
        import asyncio
        async def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** i))
            return None
        return wrapper
    return decorator
