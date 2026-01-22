const API_BASE = 'http://localhost:8001';

export const api = {
  // 认证
  login: (data: { email: string; password: string }) => 
    fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),

  register: (data: any) =>
    fetch(`${API_BASE}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),

  // 对话
  sendMessage: (data: { user_id: string; message: string; conversation_id?: string }) =>
    fetch(`http://localhost:8003/api/v1/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),

  // 专业
  getMajors: () => Promise.resolve([
    { id: '1', name: '计算机科学与技术', category: '工学', employmentRate: '95%', avgSalary: '18K-25K/月' },
    { id: '2', name: '人工智能', category: '工学', employmentRate: '98%', avgSalary: '25K-35K/月' },
    { id: '3', name: '数据科学与大数据技术', category: '理学', employmentRate: '92%', avgSalary: '20K-30K/月' }
  ])
};
