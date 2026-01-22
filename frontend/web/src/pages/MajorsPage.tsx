import React, { useState } from 'react';
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
      courses: ['数据分析', '大数据处理', '可视化'],
      employmentRate: '92%',
      avgSalary: '20K-30K/月',
      matchScore: 82
    },
    {
      id: '4',
      name: '软件工程',
      category: '工学',
      duration: '4年',
      courses: ['软件测试', '项目管理', '架构'],
      employmentRate: '94%',
      avgSalary: '18K-28K/月',
      matchScore: 79
    },
    {
      id: '5',
      name: '金融学',
      category: '经济学',
      duration: '4年',
      courses: ['货币银行学', '投资学', '风险管理'],
      employmentRate: '90%',
      avgSalary: '15K-25K/月',
      matchScore: 75
    },
    {
      id: '6',
      name: '临床医学',
      category: '医学',
      duration: '5年',
      courses: ['人体解剖学', '生理学', '药理学'],
      employmentRate: '100%',
      avgSalary: '15K-30K/月',
      matchScore: 70
    }
  ]);

  return (
    <div className="mx-4">
      {/* 标题和筛选 */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
        <h1 className="text-xl sm:text-3xl font-bold">📋 专业推荐</h1>
        <div className="flex flex-wrap gap-2">
          <select className="input w-full sm:w-32 text-sm">
            <option>全部学科</option>
            <option>工学</option>
            <option>理学</option>
            <option>经济学</option>
          </select>
          <select className="input w-full sm:w-32 text-sm">
            <option>综合排序</option>
            <option>就业率</option>
            <option>薪资</option>
          </select>
        </div>
      </div>

      {/* 专业列表 */}
      <div className="grid gap-4">
        {majors.map((major, index) => (
          <motion.div
            key={major.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <h3 className="text-base sm:text-xl font-semibold">{major.name}</h3>
                  <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">
                    匹配{major.matchScore}%
                  </span>
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                    {major.category}
                  </span>
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-600 mb-3">
                  <span>学制: {major.duration}</span>
                  <span className="text-primary-600 font-medium">薪资: {major.avgSalary}</span>
                  <span>就业: {major.employmentRate}</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {major.courses.map(course => (
                    <span
                      key={course}
                      className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs"
                    >
                      {course}
                    </span>
                  ))}
                </div>
              </div>
              <button className="btn-primary w-full sm:w-auto text-sm py-1.5 px-4">
                查看详情
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 text-center">
        <button className="btn-secondary text-sm py-2 px-6">
          加载更多专业
        </button>
      </div>
    </div>
  );
};

export default MajorsPage;
