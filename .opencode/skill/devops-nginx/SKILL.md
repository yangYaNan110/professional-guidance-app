---
name: devops-nginx
description: Nginx反向代理配置、负载均衡配置、SSL/TLS加密配置
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: development
---

## 我做什么

- 编写Nginx反向代理配置，实现前端与后端服务的代理转发
- 配置负载均衡策略，支持多实例部署和流量分发
- 配置SSL/TLS加密，实现HTTPS安全访问和证书管理
- 优化Nginx性能参数，提升并发处理能力和响应速度
- 配置静态资源缓存和压缩，减少网络传输开销
- 设置访问控制和安全策略，增强系统安全性
- 提供Docker容器化部署方案，优先使用docker启动服务

## 何时使用我

需要配置Nginx反向代理、负载均衡或SSL/TLS加密时使用此技能。

如果服务架构、部署环境或SSL证书信息不明确，请提出澄清问题。

## 核心功能

- **Docker容器化部署**: 优先通过docker-compose启动nginx服务
- **反向代理配置**: 配置upstream服务器和location规则
- **负载均衡策略**: 支持轮询、最少连接、IP哈希等负载均衡算法
- **SSL/TLS管理**: 证书配置、HTTPS重定向、安全头部设置
- **性能调优**: 缓存配置、压缩、连接池优化
- **监控日志**: 访问日志配置和监控告警设置

## 技术要求

**输入**: 服务架构、域名信息、SSL证书、性能要求

**输出**: Nginx配置文件、docker-compose配置、SSL证书、负载均衡规则

## 验收标准

- Docker容器正常启动、代理转发正常、SSL加密有效、负载均衡工作
- 支持HTTP/HTTPS双协议访问
- 性能指标达到用户要求
- 所有服务通过Docker容器启动

## 开发规范

### Docker容器化优先原则
```
项目服务启动优先级：
1. Docker容器启动（推荐）
2. 本地安装启动（备用）
```

### 配置文件结构
```
nginx/
├── nginx.conf              # 主配置文件
├── conf.d/
│   ├── upstream.conf         # 上游服务配置
│   ├── ssl.conf           # SSL配置
│   └── gzip.conf          # 压缩配置
├── ssl/                 # SSL证书目录
├── scripts/             # 部署脚本
├── logs/                # 日志目录
└── html/                 # 静态文件服务
```

### Docker Compose配置
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:1.25-alpine
    container_name: nginx-proxy
    restart: unless-stopped
    ports:
      - "80:80"       # HTTP端口
      - "443:443"     # HTTPS端口
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
      - ./nginx/html:/var/www/html:ro
    depends_on:
      - api-gateway
      - major-service
      - market-data-service
      - university-service
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

### 标准配置模板

**主配置 (nginx.conf)**:
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    tcp_nopush     on;
    keepalive_timeout  65s;
    tcp_nodelay     on;
    keepalive_requests 100;

    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        image/svg+xml;

    client_max_body_size 100m;

    # 包含其他配置文件
    include /etc/nginx/conf.d/*.conf;

    # 主服务器配置
    server {
        listen 80;
        listen 443 ssl;
        server_name localhost;

        # SSL证书配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # 安全头部
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";
        add_header X-XSS-Protection "1; mode=block";

        # 前端静态文件服务
        location / {
            root /var/www/html;
            index index.html index.htm;
            try_files $uri $uri $uri/ =404;
            expires 30d;
        }

        # API代理配置
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;

            # CORS配置
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        }

        # WebSocket代理
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # 健康检查端点
        location /nginx-health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### 上游服务配置 (conf.d/upstream.conf)
```nginx
# 上游后端服务配置
upstream backend {
    least_conn;
    server host.docker.internal:8001;    # user-service
    server host.docker.internal:8003;    # major-service  
    server host.docker.internal:8004;    # market-data-service
    server host.docker.internal:8005;    # university-service
    server host.docker.internal:8006;    # chat-service
    server host.docker.internal:8008;    # crawler-service
    server host.docker.internal:8010;    # video-service
    server host.docker.internal:8011;    # analytics-service
    keepalive 32;
}

# 高可用配置
upstream backend_ha {
    least_conn;
    server host.docker.internal:8001 max_fails=3 fail_timeout=30s;
    server host.docker.internal:8003 max_fails=3 fail_timeout=30s;
    server host.docker.internal:8004 max_fails=3 fail_timeout=30s;
    server host.docker.internal:8005 max_fails=3 fail_timeout=30s;
    server host.docker.internal:8006 max_fails=3 fail_timeout=30s;
    server host.docker.internal:8008 max_fails=3 fail_timeout=30s;
    server host.docker.internal:8010 max_fails=3 fail_timeout=30s;
    server host.docker.internal:8011 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

## 部署要求

**Docker容器化部署（优先方式）**：
```bash
# 启动nginx服务
docker-compose up -d nginx

# 重新加载配置
docker-compose exec nginx nginx -s reload

# 查看nginx状态
docker-compose ps nginx

# 查看日志
docker-compose logs nginx
```

**SSL证书设置**：
```bash
# 生成开发环境自签名证书
./nginx/scripts/setup-ssl.sh

# 启动nginx服务
docker-compose up -d nginx
```

**本地安装（备用方式）**:
```bash
# 安装nginx (Ubuntu/Debian)
sudo apt update
sudo apt install nginx -y

# CentOS/RHEL
sudo yum install nginx -y
```

## 配置验证

**Docker环境验证**：
```bash
# 检查配置语法
docker-compose exec nginx nginx -t

# 测试配置
docker-compose exec nginx nginx -T

# 重载配置
docker-compose exec nginx nginx -s reload
```

**本地环境验证**：
```bash
# 检查配置语法
nginx -t

# 测试配置
nginx -T

# 重载配置
nginx -s reload
```

## 安全最佳实践

1. **Docker安全**: 使用官方镜像，定期更新基础镜像
2. **SSL配置**: 使用有效证书，禁用弱加密算法
3. **访问控制**: 限制敏感路径访问
4. **日志审计**: 启用访问日志并定期分析
5. **安全头部**: 配置安全HTTP头部
6. **Rate Limiting**: 防止滥用攻击

## 故障排查

**Docker环境问题**：
- 容器启动失败：检查端口占用和卷挂载
- 代理失败：检查upstream服务和网络连接
- SSL证书错误：验证证书路径和权限

**常见问题**：
- 502 Bad Gateway: 检查upstream配置
- 504 Gateway Timeout: 检查后端服务状态
- SSL Certificate Error: 检查证书路径和权限
- 413 Request Entity Too Large: 调整client_max_body_size

## 性能优化

**Docker优化**：
```yaml
nginx:
  image: nginx:1.25-alpine
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M
```

**Nginx配置优化**：
```nginx
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65s;
client_max_body_size 100m;

# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m inactive=60m;
```

## 质量保证

**配置检查清单**：
- ✅ Docker容器正常启动
- ✅ 配置语法正确
- ✅ SSL证书有效
- ✅ 负载均衡正常工作
- ✅ 性能指标达标
- ✅ 安全配置完善
- ✅ 日志记录完整
- ✅ 监控告警工作

## 维护指南

**定期任务**：
- 每月检查证书有效性
- 每周检查日志文件大小
- 监控容器资源使用
- 更新Docker镜像
- 备份配置文件

**Docker容器管理**：
- 定期更新nginx镜像
- 监控容器资源使用
- 设置自动重启策略
- 配置健康检查