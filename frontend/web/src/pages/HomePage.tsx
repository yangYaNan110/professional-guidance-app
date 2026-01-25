import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

interface Stats {
  total: number;
  categories: { name: string; count: number }[];
  last_crawl: string;
}

const API_BASE = 'http://localhost:8002';

const HomePage: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        console.log('开始获取统计数据...');
        const response = await fetch(`${API_BASE}/api/v1/statistics`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          console.error('Response not ok:', response.statusText);
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        
        if (data.success) {
          setStats({
            total: data.data.total_majors || 0,
            categories: [],
            last_crawl: data.data.data_updated_at || ''
          });
          console.log('Stats set successfully');
        } else {
          console.error('API returned error:', data.message);
          throw new Error(data.message || '获取统计数据失败');
        }
      } catch (err) {
        console.error('获取统计数据失败:', err);
        setError(err instanceof Error ? err.message : '未知错误');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="space-y-8 sm:space-y-12">
      <section className="text-center py-8 sm:py-16 px-4">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl sm:text-3xl md:text-5xl font-bold text-gray-900 mb-4 sm:mb-6"
        >
          🎯 智能专业选择助手
        </motion.h1>
        <p className="text-sm sm:text-base md:text-xl text-gray-600 max-w-xl mx-auto mb-6 sm:mb-8 leading-relaxed">
          基于AI的智能专业指导，帮助高中生找到适合自己的大学专业，让专业选择不再迷茫
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-3 sm:space-x-4 px-4">
          <Link to="/chat" className="btn-primary text-base sm:text-lg px-6 sm:px-8 py-2.5 sm:py-3 w-full sm:w-auto">
            开始对话 💬
          </Link>
          <Link to="/majors" className="btn-secondary text-base sm:text-lg px-6 sm:px-8 py-2.5 sm:py-3 w-full sm:w-auto">
            查看专业 📋
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6 md:gap-8 px-4">
        <FeatureCard
          emoji="🎤"
          title="语音交互"
          description="支持语音输入和输出，与智能助手自然对话"
        />
        <FeatureCard
          emoji="💡"
          title="智能推荐"
          description="基于您的学科优势和兴趣，智能匹配专业方向"
        />
        <FeatureCard
          emoji="📊"
          title="数据分析"
          description="专业趋势、就业前景可视化分析"
        />
      </section>

      <section className="card mx-4">
        <h2 className="text-lg sm:text-2xl font-bold mb-4 sm:mb-6">📈 专业选择概览</h2>
        {error ? (
          <div className="text-center py-4 text-gray-500">
            <p>⚠️ {error}</p>
          </div>
        ) : loading ? (
          <div className="text-center py-4 text-gray-500">
            <p>加载中...</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-6">
            <StatCard label="在招专业" value={String(stats?.total || 0)} />
            <StatCard label="学科门类" value={String(stats?.categories?.length || 0)} />
            <StatCard label="学生咨询" value="10,000+" />
            <StatCard label="数据来源" value="阳光高考" />
          </div>
        )}
      </section>
    </div>
  );
};

const FeatureCard: React.FC<{ emoji: string; title: string; description: string }> = ({
  emoji,
  title,
  description
}) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className="card text-center"
  >
    <div className="text-3xl sm:text-4xl mb-3 sm:mb-4">{emoji}</div>
    <h3 className="text-base sm:text-xl font-semibold mb-2">{title}</h3>
    <p className="text-sm sm:text-base text-gray-600">{description}</p>
  </motion.div>
);

const StatCard: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="text-center p-3 sm:p-4 bg-primary-50 rounded-lg">
    <div className="text-xl sm:text-3xl font-bold text-primary-600">{value}</div>
    <div className="text-xs sm:text-base text-gray-600 mt-1">{label}</div>
  </div>
);

export default HomePage;
