"""
专业推荐API单元测试
严格按照需求设计文档规范验证：
1. 数据真实性原则
2. 开发期间禁用Redis缓存
3. 专业列表排序规则
4. API响应格式
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommendation_api import app

client = TestClient(app)

class TestMajorMarketDataAPI:
    """专业行情数据API测试类"""
    
    @patch('recommendation_api.get_db_connection')
    def test_get_major_market_data_default_sorting(self, mock_get_conn):
        """测试默认按热度指数排序"""
        # 模拟数据库响应
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # 模拟查询结果
        mock_cursor.fetchone.return_value = {'total': 2}
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'major_name': '计算机科学与技术',
                'category': '工学',
                'employment_rate': 95.5,
                'avg_salary': '15000-20000',
                'heat_index': 98.5,
                'crawled_at': '2026-01-25T10:00:00'
            },
            {
                'id': 2,
                'major_name': '软件工程',
                'category': '工学',
                'employment_rate': 94.2,
                'avg_salary': '14000-18000',
                'heat_index': 92.3,
                'crawled_at': '2026-01-25T09:00:00'
            }
        ]
        
        # 发送请求
        response = client.get("/api/v1/major/market-data")
        
        # 验证响应
        assert response.status_code == 200
        assert response.headers.get("X-Cache") == "DISABLED"
        
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 2
        
        # 验证默认按热度指数降序排序
        assert data["data"][0]["heat_index"] >= data["data"][1]["heat_index"]
        
        # 验证SQL查询包含正确的排序
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args[0][0]
        assert "ORDER BY heat_index desc" in call_args.lower()
    
    @patch('recommendation_api.get_db_connection')
    def test_get_major_market_data_with_category_filter(self, mock_get_conn):
        """测试学科门类筛选"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = {'total': 1}
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'major_name': '人工智能',
                'category': '工学',
                'employment_rate': 96.0,
                'avg_salary': '18000-25000',
                'heat_index': 99.2,
                'crawled_at': '2026-01-25T10:00:00'
            }
        ]
        
        response = client.get("/api/v1/major/market-data?category=工学")
        
        assert response.status_code == 200
        assert response.headers.get("X-Cache") == "DISABLED"
        
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["category"] == "工学"
        
        # 验证SQL查询包含筛选条件
        call_args = mock_cursor.execute.call_args[0]
        assert "category = %s" in call_args[0]
        assert "工学" in call_args[1]
    
    @patch('recommendation_api.get_db_connection')
    def test_get_major_market_data_different_sort_fields(self, mock_get_conn):
        """测试不同排序字段"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = {'total': 2}
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'major_name': 'A', 'category': '工学', 'employment_rate': 90.0, 'avg_salary': '10000', 'heat_index': 80.0, 'crawled_at': '2026-01-25T10:00:00'},
            {'id': 2, 'major_name': 'B', 'category': '理学', 'employment_rate': 95.0, 'avg_salary': '12000', 'heat_index': 85.0, 'crawled_at': '2026-01-25T09:00:00'}
        ]
        
        # 测试按就业率排序
        response = client.get("/api/v1/major/market-data?sort_by=employment_rate&order=asc")
        
        assert response.status_code == 200
        call_args = mock_cursor.execute.call_args[0][0]
        assert "ORDER BY employment_rate asc" in call_args.lower()
    
    @patch('recommendation_api.get_db_connection')
    def test_get_major_market_data_pagination(self, mock_get_conn):
        """测试分页功能"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = {'total': 50}
        mock_cursor.fetchall.return_value = []
        
        response = client.get("/api/v1/major/market-data?page=2&page_size=10")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["page_size"] == 10
        assert data["pagination"]["total"] == 50
        assert data["pagination"]["total_pages"] == 5
        
        # 验证分页参数
        call_args = mock_cursor.execute.call_args[0][1]
        assert call_args[-2] == 10  # page_size
        assert call_args[-1] == 10  # offset (page-1)*page_size
    
    def test_page_size_validation(self):
        """测试分页大小验证"""
        # 测试超出最大限制
        response = client.get("/api/v1/major/market-data?page_size=150")
        # FastAPI会自动验证Query参数，超出限制会返回422
        assert response.status_code == 422
    
    @patch('recommendation_api.get_db_connection')
    def test_invalid_sort_field_defaults_to_heat_index(self, mock_get_conn):
        """测试无效排序字段默认使用热度指数"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = {'total': 0}
        mock_cursor.fetchall.return_value = []
        
        response = client.get("/api/v1/major/market-data?sort_by=invalid_field")
        
        assert response.status_code == 200
        
        # 验证使用了默认排序字段
        call_args = mock_cursor.execute.call_args[0][0]
        assert "ORDER BY heat_index" in call_args.lower()
    
    @patch('recommendation_api.get_db_connection')
    def test_database_connection_error(self, mock_get_conn):
        """测试数据库连接错误处理"""
        mock_get_conn.side_effect = Exception("数据库连接失败")
        
        response = client.get("/api/v1/major/market-data")
        
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]


class TestCategoriesAPI:
    """学科分类API测试类"""
    
    @patch('recommendation_api.get_db_connection')
    def test_get_categories_from_real_data(self, mock_get_conn):
        """测试从真实数据获取学科分类"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # 模拟真实数据库查询结果
        mock_cursor.fetchall.return_value = [
            {'category': '工学', 'count': 50, 'display_name': '🔧 工学'},
            {'category': '理学', 'count': 30, 'display_name': '🔬 理学'},
            {'category': '经济学', 'count': 25, 'display_name': '💰 经济学'}
        ]
        
        response = client.get("/api/v1/data/categories")
        
        assert response.status_code == 200
        assert response.headers.get("X-Cache") == "DISABLED"
        
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 3
        
        # 验证数据格式
        category = data["data"][0]
        assert "category" in category
        assert "count" in category
        assert "display_name" in category
        
        # 验证按数量降序排序
        assert data["data"][0]["count"] >= data["data"][1]["count"]
        assert data["data"][1]["count"] >= data["data"][2]["count"]
        
        # 验证emoji标识
        assert "🔧" in data["data"][0]["display_name"]
        assert "🔬" in data["data"][1]["display_name"]
    
    @patch('recommendation_api.get_db_connection')
    def test_categories_ignores_null_and_empty(self, mock_get_conn):
        """测试学科分类过滤NULL和空值"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        mock_cursor.fetchall.return_value = [
            {'category': '工学', 'count': 50, 'display_name': '🔧 工学'},
            {'category': '理学', 'count': 30, 'display_name': '🔬 理学'}
        ]
        
        response = client.get("/api/v1/data/categories")
        
        assert response.status_code == 200
        
        # 验证SQL查询包含过滤条件
        call_args = mock_cursor.execute.call_args[0][0]
        assert "WHERE category IS NOT NULL" in call_args
        assert "AND category != ''" in call_args
    
    @patch('recommendation_api.get_db_connection')
    def test_categories_database_error(self, mock_get_conn):
        """测试学科分类数据库错误处理"""
        mock_get_conn.side_effect = Exception("查询失败")
        
        response = client.get("/api/v1/data/categories")
        
        assert response.status_code == 500
        assert "查询学科分类失败" in response.json()["detail"]


class TestHealthCheckAPI:
    """健康检查API测试类"""
    
    @patch('recommendation_api.get_db_connection')
    def test_health_check_success(self, mock_get_conn):
        """测试健康检查成功"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        response = client.get("/api/v1/major/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["cache"] == "disabled (development mode)"
        assert "timestamp" in data
    
    @patch('recommendation_api.get_db_connection')
    def test_health_check_failure(self, mock_get_conn):
        """测试健康检查失败"""
        mock_get_conn.side_effect = Exception("连接失败")
        
        response = client.get("/api/v1/major/health")
        
        assert response.status_code == 200  # 健康检查总是返回200
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
        assert "error" in data


class TestOptimizationSQL:
    """优化SQL测试类"""
    
    def test_get_optimization_sql(self):
        """测试获取优化SQL"""
        response = client.get("/api/v1/admin/optimization-sql")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "title" in data
        assert "sql" in data
        assert "usage" in data
        
        # 验证包含关键索引
        sql = data["sql"]
        assert "idx_major_market_heat_index" in sql
        assert "idx_major_market_category" in sql
        assert "ANALYZE major_market_data" in sql


class TestCacheHeader:
    """缓存头部测试类"""
    
    @patch('recommendation_api.get_db_connection')
    def test_cache_headers_in_all_responses(self, mock_get_conn):
        """测试所有响应都包含禁用缓存头部"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # 模拟数据
        mock_cursor.fetchone.return_value = {'total': 0}
        mock_cursor.fetchall.return_value = []
        
        # 测试各个API端点
        endpoints = [
            "/api/v1/major/market-data",
            "/api/v1/data/categories"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.headers.get("X-Cache") == "DISABLED", f"端点 {endpoint} 缺少缓存禁用头部"


class TestPaginationAndSorting:
    """分页和排序综合测试类"""
    
    @patch('recommendation_api.get_db_connection')
    def test_complex_query_parameters(self, mock_get_conn):
        """测试复杂查询参数组合"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = {'total': 100}
        mock_cursor.fetchall.return_value = []
        
        # 测试多个参数组合
        response = client.get(
            "/api/v1/major/market-data?"
            "category=工学&page=3&page_size=15&sort_by=employment_rate&order=asc"
        )
        
        assert response.status_code == 200
        
        # 验证SQL查询包含所有条件
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0].lower()
        params = call_args[0][1]
        
        assert "category = %s" in query
        assert "工学" in params
        assert "order by employment_rate asc" in query
        assert 15 in params  # page_size
        assert 30 in params  # offset (3-1)*15


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])