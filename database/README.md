# 就业指导应用 - 数据库

## 目录结构

```
database/
├── migrations/     # 数据库迁移文件
├── seeds/          # 种子数据
└── README.md
```

## 使用方法

```bash
# 运行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 生成迁移
alembic revision -m "description"

# 填充种子数据
python -m database.seeds.run
```
