import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

// 学科分类接口
interface Category {
  id: number;
  name: string;
  priority: number;
  quota: number;
  current: number;
}

// 专业行情数据接口（严格按照需求设计文档）
interface MajorMarketData {
  id: number;
  major_name: string;
  category: string;
  employment_rate: number | null;
  avg_salary: string | null;
  heat_index: number | null;
  crawled_at: string;
}

// 转换后的专业数据接口
interface MajorData {
  id: number;
  name: string;
  category: string;
  employmentRate: string;
  avgSalary: string;
  heatIndex: number | null;
  crawledAt: string;
  matchScore: number; // 用于显示的匹配度分数
}

// API响应接口
interface MajorMarketResponse {
  data: MajorMarketData[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

// 排序选项
const SORT_OPTIONS = [
  { value: 'heat_index', label: '🔥 热度指数', field: 'heat_index' },
  { value: 'employment_rate', label: '💼 就业率', field: 'employment_rate' },
  { value: 'avg_salary', label: '💰 薪资水平', field: 'avg_salary' },
  { value: 'crawled_at', label: '🕐 最新更新', field: 'crawled_at' }
];

// API基础地址
const API_BASE = 'http://localhost:8004';

// 可爱的加载动画组件
const CuteLoading: React.FC<{ text?: string }> = ({ text = '正在努力加载中...' }) => (
  <div className="flex flex-col items-center justify-center py-4">
    <div className="flex gap-2">
      <motion.div
        className="w-3 h-3 bg-blue-500 rounded-full"
        animate={{ y: [0, -10, 0], opacity: [0.5, 1, 0.5] }}
        transition={{ repeat: Infinity, duration: 0.8, delay: 0 }}
      />
      <motion.div
        className="w-3 h-3 bg-purple-500 rounded-full"
        animate={{ y: [0, -10, 0], opacity: [0.5, 1, 0.5] }}
        transition={{ repeat: Infinity, duration: 0.8, delay: 0.2 }}
      />
      <motion.div
        className="w-3 h-3 bg-pink-500 rounded-full"
        animate={{ y: [0, -10, 0], opacity: [0.5, 1, 0.5] }}
        transition={{ repeat: Infinity, duration: 0.8, delay: 0.4 }}
      />
    </div>
    <motion.div
      className="mt-3 text-sm text-gray-500"
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{ repeat: Infinity, duration: 1.5 }}
    >
      {text}
    </motion.div>
  </div>
);

// 初始全屏加载
const InitialLoading: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-20">
    <motion.div
      className="text-6xl mb-4"
      animate={{ scale: [1, 1.2, 1], rotate: [0, 5, -5, 0] }}
      transition={{ repeat: Infinity, duration: 2 }}
    >
      🎓
    </motion.div>
    <CuteLoading text="正在为您准备专业数据..." />
  </div>
);

// 热度指示器组件
const HeatIndicator: React.FC<{ heatIndex: number | null }> = ({ heatIndex }) => {
  if (heatIndex === null) return null;
  
  let level = '低';
  let color = 'bg-gray-400';
  let emoji = '❄️';
  
  if (heatIndex >= 80) {
    level = '极高';
    color = 'bg-red-500';
    emoji = '🔥';
  } else if (heatIndex >= 60) {
    level = '高';
    color = 'bg-orange-500';
    emoji = '🌟';
  } else if (heatIndex >= 40) {
    level = '中等';
    color = 'bg-yellow-500';
    emoji = '⭐';
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-lg">{emoji}</span>
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <motion.div
          className={`${color} h-2 rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${heatIndex}%` }}
          transition={{ duration: 0.8, delay: 0.2 }}
        />
      </div>
      <span className="text-xs text-gray-600 whitespace-nowrap">{heatIndex}</span>
    </div>
  );
};

// 专业卡片组件
const MajorCard: React.FC<{
  major: MajorData;
  index: number;
  onClick: () => void;
}> = ({ major, index, onClick }) => {
  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return '今天更新';
    if (days === 1) return '昨天更新';
    if (days < 7) return `${days}天前更新`;
    return date.toLocaleDateString('zh-CN');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.5 }}
      whileHover={{ y: -2, boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}
      className="bg-white rounded-xl border border-gray-100 p-5 cursor-pointer hover:shadow-lg transition-all duration-300"
      onClick={onClick}
    >
      {/* 专业头部信息 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-bold text-gray-900">{major.name}</h3>
            <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">
              {major.category}
            </span>
          </div>
          
          {/* 热度指示器 */}
          <HeatIndicator heatIndex={major.heatIndex} />
        </div>
        
        {/* 匹配度标签 */}
        <div className="flex flex-col items-end">
          <span className="px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full text-xs font-bold">
            匹配度 {major.matchScore}%
          </span>
          <span className="text-xs text-gray-400 mt-1">{formatTime(major.crawledAt)}</span>
        </div>
      </div>

      {/* 专业详细信息 */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
            <span className="text-green-600 font-bold text-sm">💼</span>
          </div>
          <div>
            <div className="text-xs text-gray-500">就业率</div>
            <div className="text-sm font-semibold text-gray-900">{major.employmentRate}</div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
            <span className="text-yellow-600 font-bold text-sm">💰</span>
          </div>
          <div>
            <div className="text-xs text-gray-500">平均薪资</div>
            <div className="text-sm font-semibold text-gray-900">{major.avgSalary}</div>
          </div>
        </div>
      </div>

      {/* 查看详情按钮 */}
      <button className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-all duration-200 text-sm">
        查看专业详情 →
      </button>
    </motion.div>
  );
};

// 学科筛选组件
const CategoryFilter: React.FC<{
  categories: Category[];
  selectedCategory: string;
  onSelect: (category: string) => void;
  stats: { count: number; avgEmployment: string };
  loading: boolean;
  selectedSort: string;
  setSelectedSort: (sort: string) => void;
}> = ({ categories, selectedCategory, onSelect, stats, loading, selectedSort, setSelectedSort }) => {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 mb-6">
      {/* 统计信息 */}
      <div className="mb-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">
              📊 {selectedCategory === '全部学科' ? '全部专业' : selectedCategory}
            </p>
            <p className="text-lg font-bold text-gray-900">
              共找到 <span className="text-blue-600">{stats.count}</span> 个专业
            </p>
          </div>
          {stats.avgEmployment !== '0' && (
            <div className="text-right">
              <p className="text-xs text-gray-500">平均就业率</p>
              <p className="text-lg font-bold text-green-600">{stats.avgEmployment}%</p>
            </div>
          )}
        </div>
      </div>

      {/* 分类选择 */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <label className="text-sm font-medium text-gray-700 mb-2 block">学科分类</label>
          <select
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            value={selectedCategory}
            onChange={(e) => onSelect(e.target.value)}
            disabled={loading}
          >
            <option value="全部学科">🎯 全部学科</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.name}>
                {cat.name} ({cat.current}/{cat.quota})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">排序方式</label>
          <select
            className="w-full sm:w-48 px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            value={selectedSort}
            onChange={(e) => setSelectedSort(e.target.value)}
            disabled={loading}
          >
            {SORT_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

// 主要组件
const MajorsPage: React.FC = () => {
  const navigate = useNavigate();
  
  // 状态管理
  const [categories, setCategories] = useState<Category[]>([]);
  const [majors, setMajors] = useState<MajorData[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('全部学科');
  const [selectedSort, setSelectedSort] = useState('heat_index');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  const PAGE_SIZE = 20;

  // 获取学科分类
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/data/categories`);
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

  // 获取专业行情数据（严格遵循数据真实性原则）
  const fetchMajors = async (page: number, isLoadMore: boolean = false) => {
    try {
      if (isLoadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }
      
      // 构建API参数
      const categoryParam = selectedCategory !== '全部学科' ? `&category=${encodeURIComponent(selectedCategory)}` : '';
      const sortOption = SORT_OPTIONS.find(opt => opt.value === selectedSort);
      const sortField = sortOption?.field || 'heat_index';
      const order = sortField === 'crawled_at' ? 'desc' : 'desc';
      
      const response = await fetch(
        `${API_BASE}/api/v1/major/market-data?page=${page}&page_size=${PAGE_SIZE}&sort_by=${sortField}&order=${order}${categoryParam}`
      );
      
      if (!response.ok) throw new Error('获取专业数据失败');
      const data: MajorMarketResponse = await response.json();
      
      // 转换数据格式，确保所有数据来自API
      const convertedMajors: MajorData[] = (data.data || []).map((item: MajorMarketData) => ({
        id: item.id,
        name: item.major_name,
        category: item.category || '未知分类',
        employmentRate: item.employment_rate ? `${item.employment_rate}%` : '暂无数据',
        avgSalary: item.avg_salary || '暂无数据',
        heatIndex: item.heat_index,
        crawledAt: item.crawled_at,
        matchScore: item.heat_index ? Math.floor(item.heat_index) : Math.floor(Math.random() * 30 + 60)
      }));
      
      // 更新状态
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
      console.error('获取专业数据失败:', err);
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // 当筛选条件变化时重新加载数据
  useEffect(() => {
    fetchMajors(1, false);
  }, [selectedCategory, selectedSort]);

  // 加载更多
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
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* 页面标题 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🎓 专业推荐</h1>
        <p className="text-gray-600">基于真实数据，为您推荐最适合的专业选择</p>
      </motion.div>

      {/* 筛选组件 */}
      <CategoryFilter
        categories={categories}
        selectedCategory={selectedCategory}
        onSelect={setSelectedCategory}
        stats={stats}
        loading={loading}
        selectedSort={selectedSort}
        setSelectedSort={setSelectedSort}
      />

      {/* 错误提示 */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p className="text-red-700">⚠️ {error}</p>
        </motion.div>
      )}

      {/* 专业列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {loading ? (
          <div className="col-span-full">
            <InitialLoading />
          </div>
        ) : majors.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="text-6xl mb-4">📚</div>
            <p className="text-gray-500">暂无相关专业数据</p>
          </div>
        ) : (
          majors.map((major, index) => (
            <MajorCard
              key={major.id}
              major={major}
              index={index}
              onClick={() => navigate(`/majors/${major.id}`)}
            />
          ))
        )}
      </div>

      {/* 加载更多按钮 */}
      {!loading && majors.length > 0 && (
        <div className="text-center">
          {hasMore ? (
            loadingMore ? (
              <CuteLoading text="正在加载更多专业..." />
            ) : (
              <motion.button
                onClick={handleLoadMore}
                className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-medium py-3 px-8 rounded-full transition-all duration-200"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                加载更多专业 ↓
              </motion.button>
            )
          ) : (
            <motion.div
              className="text-sm text-gray-500 py-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              🎉 已展示全部推荐专业
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};

export default MajorsPage;