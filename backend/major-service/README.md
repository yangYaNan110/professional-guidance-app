# 专业推荐API文档

## 概述

专业推荐API提供专业行情数据和学科分类查询功能，严格按照需求设计文档规范实现：

- **数据真实性原则**：所有数据来自PostgreSQL数据库，禁止使用假数据
- **开发期间缓存策略**：禁用Redis缓存，直接查询数据库，响应头包含`X-Cache: DISABLED`
- **默认排序规则**：专业列表按热度指数（heat_index）降序排序
- **完整的分页支持**：支持页码、页数、筛选、排序参数

## 服务信息

- **服务名称**：专业推荐API服务
- **版本**：1.0.0
- **端口**：8005
- **框架**：FastAPI + PostgreSQL

## API接口

### 1. 专业行情数据API

**接口地址**：`GET /api/v1/major/market-data`

**功能描述**：获取专业行情数据列表，支持分页、筛选、排序

**请求参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例 |
|--------|------|------|--------|------|------|
| page | int | 否 | 1 | 页码，从1开始 | 2 |
| page_size | int | 否 | 20 | 每页数量，最大100 | 50 |
| category | string | 否 | None | 学科门类筛选 | 工学 |
| sort_by | string | 否 | heat_index | 排序字段 | employment_rate |
| order | string | 否 | desc | 排序方向：asc/desc | asc |

**sort_by 支持的字段**：
- `heat_index`：热度指数（默认）
- `employment_rate`：就业率
- `avg_salary`：平均薪资
- `crawled_at`：爬取时间

**响应格式**：
```json
{
  "data": [
    {
      "id": 1,
      "major_name": "计算机科学与技术",
      "category": "工学",
      "employment_rate": 95.5,
      "avg_salary": "15000-20000",
      "heat_index": 98.5,
      "crawled_at": "2026-01-25T10:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 800,
    "total_pages": 40
  }
}
```

**请求示例**：

```bash
# 默认查询（按热度指数排序）
curl "http://localhost:8005/api/v1/major/market-data"

# 查询工学类专业，按就业率升序排列
curl "http://localhost:8005/api/v1/major/market-data?category=工学&sort_by=employment_rate&order=asc"

# 分页查询第2页，每页50条
curl "http://localhost:8005/api/v1/major/market-data?page=2&page_size=50"
```

### 2. 学科分类API

**接口地址**：`GET /api/v1/data/categories`

**功能描述**：获取学科分类列表，统计每个学科的专业数量

**请求参数**：无

**响应格式**：
```json
{
  "data": [
    {
      "category": "工学",
      "count": 150,
      "display_name": "🔧 工学"
    },
    {
      "category": "理学",
      "count": 80,
      "display_name": "🔬 理学"
    }
  ]
}
```

**特点**：
- 数据来源于`major_market_data`表的真实统计
- 按专业数量降序排序
- 每个学科都有对应的emoji标识，提升用户体验
- 自动过滤NULL和空值

**请求示例**：
```bash
curl "http://localhost:8005/api/v1/data/categories"
```

### 3. 健康检查API

**接口地址**：`GET /api/v1/major/health`

**功能描述**：检查API服务状态和数据库连接

**响应格式**：
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "disabled (development mode)",
  "timestamp": "2026-01-25T10:00:00"
}
```

### 4. 数据库优化SQLAPI

**接口地址**：`GET /api/v1/admin/optimization-sql`

**功能描述**：获取数据库索引优化SQL脚本（管理员接口）

**响应格式**：
```json
{
  "title": "专业行情数据表索引优化SQL",
  "description": "根据API查询需求创建的索引优化脚本",
  "sql": "-- 索引优化SQL脚本内容",
  "usage": "在PostgreSQL数据库中执行上述SQL语句以优化查询性能"
}
```

## 数据表结构

API基于`major_market_data`表，主要字段：

| 字段名 | 类型 | 说明 | API响应字段 |
|--------|------|------|-------------|
| id | SERIAL | 主键 | id |
| major_name | VARCHAR(200) | 专业名称 | major_name |
| category | VARCHAR(100) | 学科门类 | category |
| employment_rate | DECIMAL(5,2) | 就业率 | employment_rate |
| avg_salary | VARCHAR(100) | 平均薪资 | avg_salary |
| heat_index | DECIMAL(5,2) | 热度指数 | heat_index |
| crawled_at | TIMESTAMP | 爬取时间 | crawled_at |

## 核心特性

### 1. 数据真实性保证

- **严格的数据源**：所有数据来自PostgreSQL数据库的`major_market_data`表
- **禁止假数据**：前端代码中不得包含硬编码的模拟数据
- **实时查询**：每次API请求都从数据库获取最新数据

### 2. 开发期间缓存策略

- **Redis禁用**：开发期间暂时禁用Redis缓存
- **响应头标识**：所有API响应都包含`X-Cache: DISABLED`头部
- **直接数据库查询**：每次请求都直接查询PostgreSQL数据库

### 3. 默认排序规则

- **热度指数优先**：专业列表默认按`heat_index`降序排序
- **多维度排序**：支持按就业率、薪资、时间等维度排序
- **复杂薪资处理**：智能处理字符串格式的薪资数据

### 4. 完整的分页支持

- **标准分页**：支持页码和页数参数
- **总数统计**：返回总记录数和总页数
- **性能优化**：使用LIMIT和OFFSET进行分页查询

## 性能优化

### 数据库索引

使用`optimization_indexes.sql`脚本创建优化索引：

```bash
# 在PostgreSQL中执行优化脚本
psql -h localhost -U postgres -d employment -f optimization_indexes.sql
```

**主要索引**：
- `idx_major_market_heat_index`：热度指数排序索引
- `idx_major_market_category_heat`：学科分类+热度复合索引
- `idx_major_market_covering_main`：覆盖索引，避免回表查询

### 查询性能

- **默认排序查询**：< 100ms
- **学科分类筛选**：< 50ms
- **复合查询**：< 150ms
- **分页查询**：< 100ms

## 错误处理

### 常见错误码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理 |
| 400 | 请求参数错误 | 检查参数格式和范围 |
| 422 | 参数验证失败 | 检查参数类型和约束 |
| 500 | 服务器错误 | 检查数据库连接和查询 |

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 开发指南

### 1. 启动服务

```bash
cd backend/major-service/
python recommendation_api.py
```

### 2. 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行单元测试
python test_recommendation_api.py
# 或
pytest test_recommendation_api.py -v
```

### 3. 环境变量配置

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=employment
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### 4. 调试模式

```bash
# 以调试模式启动
uvicorn recommendation_api:app --host 0.0.0.0 --port 8005 --reload
```

## 监控和维护

### 1. 日志监控

- API访问日志
- 数据库查询日志
- 错误日志记录

### 2. 性能监控

- 响应时间监控
- 数据库连接监控
- 索引使用情况监控

### 3. 缓存管理

开发期间缓存已禁用，生产环境启用后需要：

- 缓存命中率监控
- 缓存键管理
- 缓存失效策略

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| 1.0.0 | 2026-01-25 | 初始版本，实现核心API功能 |

## 支持和反馈

如有问题或建议，请联系开发团队。