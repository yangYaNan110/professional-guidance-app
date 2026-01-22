import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

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

interface Major {
  id: string;
  name: string;
  category: string;
  duration: string;
  courses: string[];
  employmentRate: string;
  avgSalary: string;
  matchScore: number;
  crawled_at: string;
}

const CuteLoading: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-4">
    <div className="flex gap-2">
      <motion.div
        className="w-4 h-4 bg-primary-500 rounded-full"
        animate={{ y: [0, -12, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, delay: 0 }}
      />
      <motion.div
        className="w-4 h-4 bg-primary-500 rounded-full"
        animate={{ y: [0, -12, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, delay: 0.15 }}
      />
      <motion.div
        className="w-4 h-4 bg-primary-500 rounded-full"
        animate={{ y: [0, -12, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, delay: 0.3 }}
      />
    </div>
    <motion.div
      className="mt-3 text-sm text-gray-500"
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{ repeat: Infinity, duration: 1.5 }}
    >
      正在努力加载中...
    </motion.div>
  </div>
);

const InitialLoading: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-16">
    <motion.div
      className="text-4xl mb-4"
      animate={{ scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] }}
      transition={{ repeat: Infinity, duration: 2 }}
    >
      📚
    </motion.div>
    <CuteLoading />
  </div>
);

const SORT_OPTIONS = [
  { value: 'heat_index', label: '综合排序（热度优先）' },
  { value: 'employmentRate', label: '就业率' },
  { value: 'avgSalary', label: '薪资' },
  { value: 'crawled_at', label: '最新更新' }
];

const API_BASE = 'http://localhost:8004';

const MajorsPage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<Category[]>([]);
  const [majors, setMajors] = useState<Major[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('全部学科');
  const [selectedSort, setSelectedSort] = useState('heat_index');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  const PAGE_SIZE = 20;

  // 从后端API获取学科列表
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/major/categories`);
        if (!response.ok) throw new Error('获取学科列表失败');
        const data = await response.json();
        setCategories(data.categories || []);
      } catch (err) {
        console.error('获取学科列表失败:', err);
        setError(err instanceof Error ? err.message : '未知错误');
      }
    };
    fetchCategories();
  }, []);

  // 从后端API获取专业列表（分页）
  const fetchMajors = async (page: number, isLoadMore: boolean = false) => {
    try {
      if (isLoadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }
      
      const categoryParam = selectedCategory !== '全部学科' ? `&category=${encodeURIComponent(selectedCategory)}` : '';
      const sortField = selectedSort === 'heat_index' || selectedSort === 'matchScore' ? 'heat_index' : 
                        selectedSort === 'employmentRate' ? 'employment_rate' : 
                        selectedSort === 'crawled_at' ? 'crawled_at' : 'heat_index';
      const order = 'desc';
      
      const response = await fetch(
        `${API_BASE}/api/v1/major/market-data?page=${page}&page_size=${PAGE_SIZE}&sort_by=${sortField}&order=${order}${categoryParam}`
      );
      
      if (!response.ok) throw new Error('获取专业列表失败');
      const data = await response.json();
      
      const convertedMajors: Major[] = (data.data || []).map((item: MarketData) => ({
        id: String(item.id),
        name: item.major_name || item.title,
        category: item.category || '未知',
        duration: '4年',
        courses: item.courses || [],
        employmentRate: item.employment_rate ? `${item.employment_rate}%` : '暂无数据',
        avgSalary: item.avg_salary || '暂无数据',
        matchScore: item.heat_index || Math.floor(Math.random() * 30 + 60),
        crawled_at: item.crawled_at || new Date().toISOString()
      }));
      
      if (isLoadMore) {
        setMajors(prev => [...prev, ...convertedMajors]);
      } else {
        setMajors(convertedMajors);
      }
      
      setCurrentPage(page);
      setTotalPages(data.pagination?.total_pages || 1);
      setHasMore(page < (data.pagination?.total_pages || 1));
      setError(null);
    } catch (err) {
      console.error('获取专业列表失败:', err);
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // 初始加载或切换学科/排序时重新加载
  useEffect(() => {
    fetchMajors(1, false);
  }, [selectedCategory, selectedSort]);

  // 加载更多专业
  const handleLoadMore = () => {
    if (!loadingMore && hasMore) {
      fetchMajors(currentPage + 1, true);
    }
  };

  // 计算统计数据
  const stats = useMemo(() => {
    const count = majors.length;
    const validMajors = majors.filter(m => m.employmentRate !== '暂无数据');
    const avgEmployment = validMajors.length > 0
      ? (validMajors.reduce((sum, m) => sum + parseFloat(m.employmentRate), 0) / validMajors.length).toFixed(1)
      : '0';
    return { count, avgEmployment };
  }, [majors]);

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

      {error && (
        <div className="mb-4 p-3 bg-red-50 rounded-lg">
          <p className="text-sm text-red-700">
            ⚠️ {error}
          </p>
        </div>
      )}

      <div className="grid gap-4">
        {loading ? (
          <InitialLoading />
        ) : majors.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>暂无专业数据</p>
          </div>
        ) : (
          majors.map((major, index) => (
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
                <button 
                  onClick={() => navigate(`/majors/${major.id}`)}
                  className="btn-primary w-full sm:w-auto text-sm py-1.5 px-4"
                >
                  查看详情
                </button>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {!loading && majors.length > 0 && (
        <div className="mt-6 text-center">
          {hasMore ? (
            loadingMore ? (
              <CuteLoading />
            ) : (
              <motion.button
                onClick={handleLoadMore}
                className="btn-secondary text-sm py-2 px-6"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                加载更多专业
              </motion.button>
            )
          ) : (
            <motion.div
              className="text-sm text-gray-500 py-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              🎉 已展示全部推荐
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};

export default MajorsPage;
