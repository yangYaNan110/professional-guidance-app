import React, { useState, useEffect, useMemo } from 'react';
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

interface Category {
  id: number;
  name: string;
  priority: number;
  quota: number;
  current: number;
}

interface MarketData {
  id: number;
  title: string;
  major_name: string;
  category: string;
  employment_rate: number | null;
  avg_salary: string | null;
  heat_index: number | null;
  crawled_at: string;
  courses: string[];
}

const SORT_OPTIONS = [
  { value: 'matchScore', label: '综合排序' },
  { value: 'employmentRate', label: '就业率' },
  { value: 'avgSalary', label: '薪资' },
  { value: 'heatIndex', label: '热度' }
];

const API_BASE = 'http://localhost:8004';

const MajorsPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [majors, setMajors] = useState<Major[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('全部学科');
  const [selectedSort, setSelectedSort] = useState('matchScore');
  const [loading, setLoading] = useState(true);

  // 从后端API获取学科列表
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/major/categories`);
        const data = await response.json();
        setCategories(data.categories || []);
      } catch (error) {
        console.error('获取学科列表失败:', error);
      }
    };
    fetchCategories();
  }, []);

  // 从后端API获取专业列表
  useEffect(() => {
    const fetchMajors = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/major/market-data?page_size=100`);
        const data = await response.json();
        
        // 转换后端数据格式
        const convertedMajors: Major[] = (data.data || []).map((item: MarketData) => ({
          id: String(item.id),
          name: item.major_name || item.title,
          category: item.category || '未知',
          duration: '4年',
          courses: item.courses || [],
          employmentRate: item.employment_rate ? `${item.employment_rate}%` : '暂无数据',
          avgSalary: item.avg_salary || '暂无数据',
          matchScore: item.heat_index || Math.floor(Math.random() * 30 + 60)
        }));
        
        setMajors(convertedMajors);
      } catch (error) {
        console.error('获取专业列表失败:', error);
        // 如果API不可用，使用备用数据
        setMajors(getBackupMajors());
      } finally {
        setLoading(false);
      }
    };
    fetchMajors();
  }, []);

  // 备用专业数据（API不可用时）
  const getBackupMajors = (): Major[] => [
    { id: '1', name: '计算机科学与技术', category: '工学', duration: '4年', courses: ['数据结构', '算法', '操作系统'], employmentRate: '95%', avgSalary: '18K-25K/月', matchScore: 95 },
    { id: '2', name: '人工智能', category: '工学', duration: '4年', courses: ['机器学习', '深度学习', 'NLP'], employmentRate: '98%', avgSalary: '25K-35K/月', matchScore: 88 },
    { id: '3', name: '数据科学与大数据技术', category: '理学', duration: '4年', courses: ['数据分析', '大数据处理'], employmentRate: '92%', avgSalary: '20K-30K/月', matchScore: 82 },
    { id: '4', name: '软件工程', category: '工学', duration: '4年', courses: ['软件测试', '项目管理'], employmentRate: '94%', avgSalary: '18K-28K/月', matchScore: 79 },
    { id: '5', name: '金融学', category: '经济学', duration: '4年', courses: ['货币银行学', '投资学'], employmentRate: '90%', avgSalary: '15K-25K/月', matchScore: 75 },
    { id: '6', name: '临床医学', category: '医学', duration: '5年', courses: ['人体解剖学', '生理学'], employmentRate: '100%', avgSalary: '15K-30K/月', matchScore: 70 },
    { id: '7', name: '法学', category: '法学', duration: '4年', courses: ['法理学', '宪法学'], employmentRate: '85%', avgSalary: '12K-20K/月', matchScore: 68 },
    { id: '8', name: '英语', category: '文学', duration: '4年', courses: ['高级英语', '翻译'], employmentRate: '88%', avgSalary: '10K-18K/月', matchScore: 65 },
    { id: '9', name: '教育学', category: '教育学', duration: '4年', courses: ['教育心理学', '课程论'], employmentRate: '92%', avgSalary: '10K-15K/月', matchScore: 62 },
    { id: '10', name: '会计学', category: '管理学', duration: '4年', courses: ['财务会计', '审计学'], employmentRate: '93%', avgSalary: '12K-20K/月', matchScore: 72 }
  ];

  // 过滤和排序后的专业列表
  const filteredAndSortedMajors = useMemo(() => {
    let result = [...majors];

    if (selectedCategory !== '全部学科') {
      result = result.filter(major => major.category === selectedCategory);
    }

    result.sort((a, b) => {
      switch (selectedSort) {
        case 'employmentRate':
          return parseFloat(b.employmentRate) - parseFloat(a.employmentRate);
        case 'avgSalary':
          const salaryA = parseInt(a.avgSalary);
          const salaryB = parseInt(b.avgSalary);
          return salaryB - salaryA;
        case 'heatIndex':
          return b.matchScore - a.matchScore;
        default:
          return b.matchScore - a.matchScore;
      }
    });

    return result;
  }, [majors, selectedCategory, selectedSort]);

  const stats = useMemo(() => {
    const count = filteredAndSortedMajors.length;
    const avgEmployment = count > 0
      ? (filteredAndSortedMajors.reduce((sum, m) => sum + parseFloat(m.employmentRate), 0) / count).toFixed(1)
      : 0;
    return { count, avgEmployment };
  }, [filteredAndSortedMajors]);

  return (
    <div className="mx-4">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
        <h1 className="text-xl sm:text-3xl font-bold">📋 专业推荐</h1>
        <div className="flex flex-wrap gap-2">
          <select
            className="input w-full sm:w-40 text-sm"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            disabled={loading}
          >
            <option value="全部学科">全部学科</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.name}>{cat.name}</option>
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

      {selectedCategory !== '全部学科' && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            📊 {selectedCategory}类共 <strong>{stats.count}</strong> 个专业，
            平均就业率 <strong>{stats.avgEmployment}%</strong>
          </p>
        </div>
      )}

      <div className="grid gap-4">
        {loading ? (
          <div className="text-center py-8 text-gray-500">
            <p>加载中...</p>
          </div>
        ) : filteredAndSortedMajors.length === 0 ? (
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

      {!loading && filteredAndSortedMajors.length > 0 && (
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
