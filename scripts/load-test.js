import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // 预热
    { duration: '1m', target: 50 },    // 升压
    { duration: '2m', target: 100 },   // 高峰
    { duration: '1m', target: 50 },    // 降压
    { duration: '30s', target: 0 },    // 冷却
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95%的请求<500ms
    http_req_failed: ['rate<0.01'],    // 失败率<1%
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  // 1. 健康检查
  const health = http.get(`${BASE_URL}/health`);
  check(health, {
    'health check passed': (r) => r.status === 200,
  });

  // 2. 测试对话接口
  const messages = [
    "我想找Python开发的工作",
    "现在AI行业怎么样？",
    "我的专业是计算机科学，能做什么工作？",
    "前端开发和后端开发哪个更有前景？",
    "薪资一般是多少？"
  ];

  const randomMessage = messages[Math.floor(Math.random() * messages.length)];

  const chatResponse = http.post(
    `${BASE_URL}/api/v1/chat/message`,
    JSON.stringify({
      user_id: "test-user-001",
      message: randomMessage,
    }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  check(chatResponse, {
    'chat response status 200': (r) => r.status === 200,
    'chat has reply': (r) => JSON.parse(r.body).reply !== undefined,
    'chat has suggestions': (r) => JSON.parse(r.body).suggestions !== undefined,
  });

  // 3. 测试职位接口
  const jobsResponse = http.get(`${BASE_URL}/api/v1/jobs?page=1&page_size=10`);
  check(jobsResponse, {
    'jobs response status 200': (r) => r.status === 200,
  });

  // 4. 测试分析接口
  const analyticsResponse = http.get(`${BASE_URL}/api/v1/analytics/salary-trend`);
  check(analyticsResponse, {
    'analytics response status 200': (r) => r.status === 200,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'performance-report.json': JSON.stringify(data, null, 2),
  };
}
