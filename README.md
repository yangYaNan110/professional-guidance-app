# OpenCode Project Configuration
# 就业指导应用

## Agent 列表

| Agent | 职责 | 模式 | 模型 |
|-------|------|------|------|
| coordinator | 整体协调和任务调度 | primary | Claude Sonnet 4 |
| frontend | 前端开发（Web/移动端/小程序） | subagent | Claude 3.5 Sonnet |
| backend | 后端开发（API网关/服务） | subagent | Claude 3.5 Sonnet |
| ai-ml | AI能力开发（对话/语音/推荐） | subagent | Claude Opus 4 |
| data | 数据服务开发（爬虫/分析/可视化） | subagent | Claude 3.5 Sonnet |
| devops | 基础设施和运维 | subagent | Claude 3.5 Sonnet |

## 启动方式

```bash
# 启动基础设施服务
docker-compose -f docker/docker-compose.infra.yml up -d

# 启动应用服务
docker-compose -f docker/docker-compose.app.yml up -d

# 查看服务状态
docker-compose ps
```

## 项目结构

```
08_demo/
├── frontend/           # 前端项目
│   ├── web/           # Web端
│   ├── mobile/        # 移动端
│   └── miniprogram/   # 小程序
├── backend/           # 后端服务
│   ├── api-gateway/   # API网关
│   ├── user-service/  # 用户服务
│   ├── voice-service/ # 语音服务
│   ├── chat-service/  # 对话服务
│   └── ...
├── database/          # 数据库
│   └── migrations/    # 迁移文件
├── docker/            # Docker配置
├── docs/              # 文档
└── scripts/           # 脚本
```

## 开发流程

1. 使用 Coordinator Agent 进行需求分析
2. 按阶段调度各子 Agent 进行开发
3. 使用 CI/CD 流水线进行测试和部署
