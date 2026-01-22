---
name: devops-k8s
description: Kubernetes集群配置，包括部署、服务、存储
license: MIT
compatibility: opencode
---

## 我做什么

负责Kubernetes集群配置，包括Deployment、Service、ConfigMap、Secret等资源定义。

## 使用场景

- K8s部署配置
- 服务发现配置
- 存储配置

## 输入格式

```json
{
  "deployment_config": {
    "service_name": "",
    "replicas": 3,
    "resources": {},
    "volumes": []
  },
  "service_config": {
    "type": "ClusterIP/NodePort/LoadBalancer",
    "ports": []
  }
}
```

## 输出格式

```json
{
  "deployment_yaml": "",
  "service_yaml": "",
  "configmap_yaml": "",
  "secret_yaml": "",
  "hpa_yaml": "",
  "ingress_yaml": ""
}
```

## 执行流程

1. 编写Deployment配置
2. 编写Service配置
3. 编写ConfigMap
4. 编写Secret
5. 配置HPA
6. 配置Ingress

## 注意事项

- 合理配置资源限制
- 做好亲和性配置
- 配置就绪探针
- 做好密钥管理

## 推荐模型

- K8s配置：`anthropic/claude-3-5-sonnet-20241022`
