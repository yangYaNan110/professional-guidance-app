import React, { useState } from 'react';
import Taro from '@tarojs/taro';
import { View, Text, Image, ScrollView } from '@tarojs/components';

interface Major {
  id: string;
  name: string;
  category: string;
  duration: string;
  courses: string[];
  employmentRate: string;
  avgSalary: string;
  matchScore: number;
}

const MajorsPage: React.FC = () => {
  const [majors] = useState<Major[]>([
    {
      id: '1',
      name: '计算机科学与技术',
      category: '工学',
      duration: '4年',
      courses: ['数据结构', '算法', '操作系统'],
      employmentRate: '95%',
      avgSalary: '18K-25K/月',
      matchScore: 95
    },
    {
      id: '2',
      name: '人工智能',
      category: '工学',
      duration: '4年',
      courses: ['机器学习', '深度学习', 'NLP'],
      employmentRate: '98%',
      avgSalary: '25K-35K/月',
      matchScore: 88
    },
    {
      id: '3',
      name: '数据科学与大数据技术',
      category: '理学',
      duration: '4年',
      courses: ['数据分析', '大数据处理', '数据可视化'],
      employmentRate: '92%',
      avgSalary: '20K-30K/月',
      matchScore: 82
    }
  ]);

  return (
    <ScrollView className='majors-container' scrollY>
      <View className='page-header'>
        <Text className='title'>📋 专业推荐</Text>
      </View>

      <View className='filter-bar'>
        <View className='filter-item'>
          <Text>全部学科</Text>
          <Text>▼</Text>
        </View>
        <View className='filter-item'>
          <Text>综合排序</Text>
          <Text>▼</Text>
        </View>
      </View>

      <View className='majors-list'>
        {majors.map((major) => (
          <View key={major.id} className='major-card' onClick={() => {
            Taro.navigateTo({ url: `/pages/major-detail/index?id=${major.id}` });
          }}>
            <View className='major-header'>
              <Text className='major-name'>{major.name}</Text>
              <View className='tags'>
                <View className='tag match-tag'>
                  <Text>匹配度 {major.matchScore}%</Text>
                </View>
                <View className='tag category-tag'>
                  <Text>{major.category}</Text>
                </View>
              </View>
            </View>
            
            <View className='major-info'>
              <Text>学制: {major.duration}</Text>
              <Text className='highlight'>平均薪资: {major.avgSalary}</Text>
              <Text>就业率: {major.employmentRate}</Text>
            </View>

            <View className='course-tags'>
              {major.courses.slice(0, 3).map((course) => (
                <View key={course} className='course-tag'>
                  <Text>{course}</Text>
                </View>
              ))}
            </View>

            <View className='action-area'>
              <Button className='detail-btn'>查看详情</Button>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default MajorsPage;
