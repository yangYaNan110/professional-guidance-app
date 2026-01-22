import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const HomePage: React.FC = () => {
  return (
    <div className="space-y-8 sm:space-y-12">
      {/* Hero Section */}
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

      {/* 功能特性 */}
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

      {/* 数据展示 */}
      <section className="card mx-4">
        <h2 className="text-lg sm:text-2xl font-bold mb-4 sm:mb-6">📈 专业选择概览</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-6">
          <StatCard label="在招专业" value="500+" />
          <StatCard label="合作院校" value="200+" />
          <StatCard label="学生咨询" value="10,000+" />
          <StatCard label="满意度" value="95%" />
        </div>
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
