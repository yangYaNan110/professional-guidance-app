---
name: devops-analyze
description: 分析运维需求和技术需求
license: MIT
compatibility: opencode
---

## 我做什么

分析部署和运维需求，评估系统可用性、安全性要求，识别运维风险。

## 使用场景

- 项目启动时运维需求分析
- 生产环境部署前评估

## 输入格式

```json
{
  "infrastructure_requirements": {},
  "availability_targets": {},
  "security_requirements": {},
  "compliance_requirements": []
}
```

## 输出格式

```json
{
  "infrastructure_architecture": {},
  "availability_plan": {},
  "security_plan": {},
  "monitoring_requirements": {},
  "backup_strategy": {},
  "risk_assessment": {}
}
```

## 执行流程

1. 评估基础设施需求
2. 设计可用性方案
3. 设计安全方案
4. 设计监控方案
5. 设计备份策略
6. 评估风险

## 注意事项

- 考虑成本效益
- 确保可扩展性
- 做好灾备设计
- 预留监控告警

## 推荐模型

- 运维分析：`anthropic/claude-3-5-sonnet-20241022`
