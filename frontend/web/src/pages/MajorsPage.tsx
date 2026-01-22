import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

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
      courses: ['数据结构', '算法', '操作系统', '计算机网络'],
      employmentRate: '95%',
      avgSalary: '18K-25K/月',
      matchScore: 95
    },
    {
      id: '2',
      name: '人工智能',
      category: '工学',
      duration: '4年',
      courses: ['机器学习', '深度学习', '自然语言处理', '计算机视觉'],
      employmentRate: '98%',
      avgSalary: '25K-35K/月',
      matchScore: 88
    },
    {
      id: '3',
      name: '数据科学与大数据技术',
      category: '理学',
      duration: '4年',
      courses: ['数据分析', '大数据处理', '数据可视化', '统计学'],
      employmentRate: '92%',
      avgSalary: '20K-30K/月',
      matchScore: 82
    },
    {
      id: '4',
      name: '软件工程',
      category: '工学',
      duration: '4年',
      courses: ['软件测试', '项目管理', '软件架构', '敏捷开发'],
      employmentRate: '94%',
      avgSalary: '18K-28K/月',
      matchScore: 79
    },
    {
      id: '5',
      name: '金融学',
      category: '经济学',
      duration: '4年',
      courses: ['货币银行学', '投资学', '公司金融', '风险管理'],
      employmentRate: '90%',
      avgSalary: '15K-25K/月',
      matchScore: 75
    },
    {
      id: '6',
      name: '临床医学',
      category: '医学',
      duration: '5年',
      courses: ['人体解剖学', '生理学', '药理学', '临床诊断'],
      employmentRate: '100%',
      avgSalary: '15K-30K/月',
      matchScore: 70
    }
  ]);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">📋 专业推荐</h1>
        <div className="flex space-x-4">
          <select className="input w-40">
            <option>全部学科</option>
            <option>工学</option>
            <option>理学</option>
            <option>经济学</option>
            <option>医学</option>
            <option>文学</option>
          </select>
          <select className="input w-40">
            <option>综合排序</option>
            <option>就业率</option>
            <option>薪资水平</option>
            <option>匹配度</option>
          </select>
        </div>
      </div>

      <div className="grid gap-4">
        {majors.map((major, index) => (
          <motion.div
            key={major.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-xl font-semibold">{major.name}</h3>
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">
                    匹配度 {major.matchScore}%
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                    {major.category}
                  </span>
                </div>
                <p className="text-gray-600 mb-2">学制: {major.duration}</p>
                <p className="text-primary-600 font-medium mb-3">平均薪资: {major.avgSalary}</p>
                <p className="text-gray-600 mb-3">就业率: {major.employmentRate}</p>
                <div className="flex flex-wrap gap-2">
                  {major.courses.map(course => (
                    <span
                      key={course}
                      className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
                    >
                      {course}
                    </span>
                  ))}
                </div>
              </div>
              <div className="ml-4">
                <button className="btn-primary">查看详情</button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <button className="btn-secondary">加载更多专业</button>
      </div>
    </div>
  );
};

export default MajorsPage;
