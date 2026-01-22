import React from 'react';
import Taro from '@tarojs/taro';
import { View, Text, Image } from '@tarojs/components';

const HomePage: React.FC = () => {
  const features = [
    { emoji: '🎤', title: '语音交互', desc: '支持语音输入和输出，与智能助手自然对话' },
    { emoji: '💡', title: '智能推荐', desc: '基于您的学科优势和兴趣，智能匹配专业方向' },
    { emoji: '📊', title: '数据分析', desc: '专业趋势、就业前景可视化分析' }
  ];

  const stats = [
    { label: '在招专业', value: '500+' },
    { label: '合作院校', value: '200+' },
    { label: '学生咨询', value: '10K+' },
    { label: '满意度', value: '95%' }
  ];

  return (
    <View className='home-container'>
      {/* Hero Section */}
      <View className='hero-section'>
        <Text className='hero-title'>🎯 智能专业选择助手</Text>
        <Text className='hero-subtitle'>
          基于AI的智能专业指导，帮助高中生找到适合自己的大学专业
        </Text>
        
        <View className='action-buttons'>
          <View 
            className='primary-btn'
            onClick={() => Taro.navigateTo({ url: '/pages/chat/index' })}
          >
            <Text>开始对话 💬</Text>
          </View>
          <View 
            className='secondary-btn'
            onClick={() => Taro.navigateTo({ url: '/pages/majors/index' })}
          >
            <Text>查看专业 📋</Text>
          </View>
        </View>
      </View>

      {/* Features */}
      <View className='features-section'>
        {features.map((feature, index) => (
          <View key={index} className='feature-card'>
            <Text className='feature-emoji'>{feature.emoji}</Text>
            <Text className='feature-title'>{feature.title}</Text>
            <Text className='feature-desc'>{feature.desc}</Text>
          </View>
        ))}
      </View>

      {/* Stats */}
      <View className='stats-section'>
        <Text className='section-title'>📈 专业选择概览</Text>
        <View className='stats-grid'>
          {stats.map((stat, index) => (
            <View key={index} className='stat-item'>
              <Text className='stat-value'>{stat.value}</Text>
              <Text className='stat-label'>{stat.label}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );
};

export default HomePage;
