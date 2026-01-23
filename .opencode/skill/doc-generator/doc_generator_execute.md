# 执行开发技能

## 描述
用户确认开发后，执行以下任务：
1. 创建数据库表或数据模型
2. 修改后端代码（API接口、数据访问层）
3. 修改前端代码（页面组件、API调用）
4. 确保项目正常运行

## 触发词
开始开发、执行开发、创建表、修改代码、开发确认

## 核心能力
1. **数据库创建**：执行DDL脚本创建数据表
2. **后端开发**：创建/修改API接口、数据访问层、模型定义
3. **前端开发**：创建/修改页面组件、API调用、类型定义
4. **代码整合**：确保前后端代码协同工作
5. **测试验证**：验证代码正确性和项目可运行性

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| confirmed_design | object | 是 | 已确认的数据模型设计 |
| document_path | string | 是 | 已生成的文档路径 |
| execute_scope | string | 否 | 执行范围（all/backend/frontend/database） |

## 输出格式

```json
{
  "execution_status": "pending_confirm|in_progress|completed|failed",
  "steps": [
    {
      "step": "string",
      "status": "pending|in_progress|completed|failed",
      "details": "string",
      "files_modified": ["string"],
      "files_created": ["string"]
    }
  ],
  "database_result": {
    "tables_created": ["string"],
    "indexes_created": ["string"],
    "ddl_file": "string"
  },
  "backend_result": {
    "files_created": ["string"],
    "files_modified": ["string"],
    "apis_created": ["string"]
  },
  "frontend_result": {
    "files_created": ["string"],
    "files_modified": ["string"],
    "components_created": ["string"]
  },
  "errors": [
    {
      "step": "string",
      "message": "string",
      "resolution": "string"
    }
  ],
  "next_steps": ["string"]
}
```

## 使用示例

```
输入：
{
  "confirmed_design": {
    "tables": [
      {
        "name": "app_major_market_data",
        "columns": [...]
      }
    ],
    "ddl_statements": "CREATE TABLE..."
  },
  "document_path": "doc/爬虫数据分析.md",
  "execute_scope": "all"
}

输出：
{
  "execution_status": "pending_confirm",
  "message_to_user": "文档已生成到 doc/爬虫数据分析.md\n\n是否开始开发？执行以下任务：\n1. 创建数据库表（app_major_market_data等）\n2. 修改后端代码（API接口、数据访问层）\n3. 修改前端代码（页面组件、API调用）\n\n请回复「同意开始开发」或「暂停」。",
  "next_action": "wait_confirm"
}
```

## 工作流程

```
用户确认开始开发
    ↓
执行数据库创建
    ├── 执行DDL脚本
    ├── 创建表结构
    └── 创建索引
    ↓
执行后端开发
    ├── 创建数据模型定义
    ├── 创建数据访问层（DAL）
    ├── 创建API接口
    └── 更新路由配置
    ↓
执行前端开发
    ├── 创建类型定义（TypeScript）
    ├── 创建API调用函数
    ├── 创建页面组件
    └── 更新页面路由
    ↓
验证和反馈
    ├── 验证代码语法
    └── 向用户反馈执行结果
```

## 执行步骤详情

### 1. 数据库创建
```bash
# 连接到PostgreSQL
# 执行DDL脚本
psql -h localhost -U postgres -d employment -f database/migrations/xxx.sql

# 或使用ORM迁移
alembic upgrade head
```

### 2. 后端开发
- **数据模型**：`backend/{service}/models/` 或 `entities/`
- **数据访问层**：`backend/{service}/dal/` 或 `repository/`
- **API接口**：`backend/{service}/api/` 或 `views/`
- **路由配置**：`backend/{service}/routers/` 或 `urls/`

### 3. 前端开发
- **类型定义**：`frontend/web/src/types/` 或 `interfaces/`
- **API调用**：`frontend/web/src/api/` 或 `services/`
- **页面组件**：`frontend/web/src/pages/` 或 `views/`
- **组件库**：`frontend/web/src/components/` 或 `widgets/`

## 与其他Agent的配合

**可调用Backend Agent**：
- 辅助创建后端API和数据访问层
- 辅助编写单元测试

**可调用Frontend Agent**：
- 辅助创建前端组件和页面
- 辅助处理样式和交互

## 与其他Skill的配合

1. 接收 `doc-generator-confirm` 的用户开发确认
2. 生成文档后自动进入等待开发确认状态
3. 用户同意后执行开发任务
4. 可调用 backend/frontend agent 辅助开发

## 注意事项

1. **二次确认**：在执行开发前必须再次获得用户确认
2. **备份代码**：修改代码前先备份或使用版本控制
3. **代码规范**：遵循项目已有的代码风格和规范
4. **测试验证**：执行后验证代码正确性
5. **错误处理**：遇到错误时记录并反馈给用户
6. **不可逆操作**：数据库DDL执行前提示用户确认
