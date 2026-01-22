import React, { useState, useMemo } from 'react';
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

// 完整学科列表
const ALL_CATEGORIES = [
  '全部学科',
  '工学', '理学', '经济学', '管理学',
  '医学', '法学', '文学', '教育学',
  '艺术学', '哲学', '历史学', '农学', '军事学'
];

// 排序方式
const SORT_OPTIONS = [
  { value: 'matchScore', label: '综合排序' },
  { value: 'employmentRate', label: '就业率' },
  { value: 'avgSalary', label: '薪资' },
  { value: 'heatIndex', label: '热度' }
];

const MajorsPage: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('全部学科');
  const [selectedSort, setSelectedSort] = useState('matchScore');

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
      courses: ['机器学习', '深度学习', 'NLP', '计算机视觉'],
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
    },
    {
      id: '7',
      name: '法学',
      category: '法学',
      duration: '4年',
      courses: ['法理学', '宪法学', '民法学', '刑法学'],
      employmentRate: '85%',
      avgSalary: '12K-20K/月',
      matchScore: 68
    },
    {
      id: '8',
      name: '英语',
      category: '文学',
      duration: '4年',
      courses: ['高级英语', '翻译', '英美文学', '语言学'],
      employmentRate: '88%',
      avgSalary: '10K-18K/月',
      matchScore: 65
    },
    {
      id: '9',
      name: '教育学',
      category: '教育学',
      duration: '4年',
      courses: ['教育心理学', '课程论', '教学论', '教育研究方法'],
      employmentRate: '92%',
      avgSalary: '10K-15K/月',
      matchScore: 62
    },
    {
      id: '10',
      name: '会计学',
      category: '管理学',
      duration: '4年',
      courses: ['财务会计', '管理会计', '审计学', '财务管理'],
      employmentRate: '93%',
      avgSalary: '12K-20K/月',
      matchScore: 72
    }
  ]);

  // 过滤和排序后的专业列表
  const filteredAndSortedMajors = useMemo(() => {
    let result = [...majors];

    // 1. 按学科过滤
    if (selectedCategory !== '全部学科') {
      result = result.filter(major => major.category === selectedCategory);
    }

    // 2. 排序
    result.sort((a, b) => {
      switch (selectedSort) {
        case 'employmentRate':
          return parseFloat(b.employmentRate) - parseFloat(a.employmentRate);
        case 'avgSalary':
          const salaryA = parseInt(a.avgSalary);
          const salaryB = parseInt(b.avgSalary);
          return salaryB - salaryA;
        case 'heatIndex':
          return b.matchScore - a.matchScore; // 使用matchScore作为热度
        default:
          return b.matchScore - a.matchScore; // 默认按匹配度
      }
    });

    return result;
  }, [majors, selectedCategory, selectedSort]);

  // 获取筛选后的统计信息
  const stats = useMemo(() => {
    const count = filteredAndSortedMajors.length;
    const avgEmployment = count > 0
      ? (filteredAndSortedMajors.reduce((sum, m) => sum + parseFloat(m.employmentRate), 0) / count).toFixed(1)
      : 0;
    return { count, avgEmployment };
  }, [filteredAndSortedMajors]);

  return (
    <div className="mx-4">
      {/* 标题和筛选 */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
        <h1 className="text-xl sm:text-3xl font-bold">📋 专业推荐</h1>
        <div className="flex flex-wrap gap-2">
          <select
            className="input w-full sm:w-40 text-sm"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {ALL_CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <select
            className="input w-full sm:w-32 text-sm"
            value={selectedSort}
            onChange={(e) => setSelectedSort(e.target.value)}
          >
            {SORT_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 统计信息 */}
      {selectedCategory !== '全部学科' && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            📊 {selectedCategory}类共 <strong>{stats.count}</strong> 个专业，
            平均就业率 <strong>{stats.avgEmployment}%</strong>
          </p>
        </div>
      )}

      {/* 专业列表 */}
      <div className="grid gap-4">
        {filteredAndSortedMajors.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>暂无该学科的专业数据</p>
          </div>
        ) : (
          filteredAndSortedMajors.map((major, index) => (
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
                    {major.courses.slice(0, 4).map(course => (
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
          ))
        )}
      </div>

      {filteredAndSortedMajors.length > 0 && (
        <div className="mt-6 text-center">
          <button className="btn-secondary text-sm py-2 px-6">
            加载更多专业
          </button>
        </div>
      )}
    </div>
  );
};

export default MajorsPage;
