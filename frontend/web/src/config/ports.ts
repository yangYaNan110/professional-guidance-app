// 前端统一API配置 - 根据需求设计文档端口规范
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',  // API网关
  SERVICES: {
    MAJOR_DETAIL: 'http://localhost:8003',     // 专业详情
    MARKET_DATA: 'http://localhost:8004',      // 专业行情
    RECOMMENDATION: 'http://localhost:8002',   // 推荐服务
    UNIVERSITY: 'http://localhost:8005',       // 大学推荐
    CHAT: 'http://localhost:8006',          // 对话服务
    VOICE: 'http://localhost:8007'          // 语音服务
  }
};
