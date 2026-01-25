import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface MajorV2 {
  id: number;
  name: string;
  category: string;
  heat_index: number;
  employment_rate: number;
  avg_salary: string;
  core_courses: string[];
  career_prospects: string;
  employment_directions: string[];
  major_concepts: {
    origin: Array<{ title: string; content: string; year: number }>;
    development_history: Array<{ title: string; content: string; year: number }>;
    major_events: Array<{ title: string; content: string; year: number }>;
    current_status: Array<{ title: string; content: string; year: number }>;
    future_prospects: Array<{ title: string; content: string; year: number }>;
  };
  warnings: {
    learning_requirements: string[];
    employment_requirements: string[];
    salary_workload: string[];
    career_stability: string[];
    development_space: string[];
    development_suggestions: string[];
  };
}

const MajorDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [majorV2, setMajorV2] = useState<MajorV2 | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = 'http://localhost:8003';

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        
        const majorDetailResponse = await fetch(`${API_BASE}/api/v2/majors/${id}/detail`);
        if (!majorDetailResponse.ok) throw new Error('获取专业详情失败');
        const majorData = await majorDetailResponse.json();
        
        if (majorData.success) {
          setMajorV2(majorData.data);
        } else {
          throw new Error('数据格式错误');
        }
      } catch (err) {
        console.error('获取专业详情失败:', err);
        setError('获取数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <motion.div className="text-4xl mb-4" animate={{ scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] }} transition={{ repeat: Infinity, duration: 2 }}>
            📚
          </motion.div>
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  if (!majorV2) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500">专业不存在</p>
        <button onClick={() => navigate('/majors')} className="btn-primary mt-4">返回专业列表</button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      <motion.button onClick={() => navigate('/majors')} className="mb-4 text-primary-600 hover:text-primary-800 dark:text-primary-400 flex items-center gap-2 font-medium" whileHover={{ x: -5 }}>
        ← 返回专业列表
      </motion.button>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card bg-white dark:bg-gray-800">
        <div className="border-b border-gray-100 dark:border-gray-700 pb-4 mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3">{majorV2.name}</h1>
          <div className="flex flex-wrap gap-3">
            <span className="px-4 py-1.5 bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium border border-blue-100 dark:border-blue-800">{majorV2.category}</span>
            <span className="px-4 py-1.5 bg-orange-50 dark:bg-orange-900/50 text-orange-700 dark:text-orange-300 rounded-full text-sm font-medium border border-orange-100 dark:border-orange-800">🔥 热度 {majorV2.heat_index?.toFixed(1) || '暂无'}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 rounded-xl p-5 text-center border border-blue-100 dark:border-blue-800">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">{majorV2.employment_rate ? `${majorV2.employment_rate.toFixed(1)}%` : '暂无'}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">就业率</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30 rounded-xl p-5 text-center border border-green-100 dark:border-green-800">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">{majorV2.avg_salary || '暂无'}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">平均薪资</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30 rounded-xl p-5 text-center border border-purple-100 dark:border-purple-800">
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-1">{majorV2.heat_index?.toFixed(1) || '暂无'}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">热度指数</div>
          </div>
        </div>

        {/* 专业介绍Tab */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4 border-b border-gray-100 dark:border-gray-700">
            <button className="px-4 py-2 font-medium text-primary-600 border-b-2 border-primary-600">
              📚 专业介绍
            </button>
          </div>

          {majorV2 ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="space-y-8">
                {/* 1️⃣ 专业概念介绍 */}
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-100 dark:border-blue-800">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl">🎓</span>
                    专业概念介绍
                  </h3>
                  <div className="text-gray-700 dark:text-gray-300 space-y-4">
                    {majorV2.major_concepts?.origin && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">🌱 起源</h4>
                        <p className="leading-relaxed">
                          {majorV2.major_concepts.origin[0]?.content || '暂无起源信息'}
                        </p>
                      </div>
                    )}
                    
                    {majorV2.major_concepts?.development_history && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">📈 发展历史</h4>
                        <div className="space-y-2">
                          {majorV2.major_concepts.development_history.slice(0, 3).map((event, index) => (
                            <div key={index} className="flex items-start gap-2">
                              <span className="text-blue-600 dark:text-blue-400 font-medium">•</span>
                              <span>{event.content}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {majorV2.major_concepts?.major_events && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">⚡ 重大事件与曲折</h4>
                        <div className="space-y-2">
                          {majorV2.major_concepts.major_events.slice(0, 2).map((event, index) => (
                            <div key={index} className="flex items-start gap-2">
                              <span className="text-orange-600 dark:text-orange-400 font-medium">•</span>
                              <span>{event.content}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {majorV2.major_concepts?.current_status && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">🚀 现状与发展</h4>
                        <p className="leading-relaxed">
                          {majorV2.major_concepts.current_status[0]?.content || '暂无现状信息'}
                        </p>
                      </div>
                    )}
                    
                    {majorV2.major_concepts?.future_prospects && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">🔮 未来前景</h4>
                        <p className="leading-relaxed">
                          {majorV2.major_concepts.future_prospects[0]?.content || '暂无未来前景信息'}
                        </p>
                      </div>
                    )}
                  </div>

                {/* 2️⃣ 核心课程 */}
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border border-green-100 dark:border-green-800">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl">📚</span>
                    核心课程
                  </h3>
                  <div className="text-gray-700 dark:text-gray-300">
                    {majorV2.core_courses && majorV2.core_courses.length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {majorV2.core_courses.map((course, index) => (
                          <div key={index} className="bg-white dark:bg-gray-700 rounded-lg px-4 py-3 text-center border border-green-200 dark:border-green-700">
                            <span className="text-green-800 dark:text-green-200 font-medium">{course}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400">暂无核心课程信息</p>
                    )}
                  </div>
                </div>

                {/* 3️⃣ 就业前景 */}
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6 border border-purple-100 dark:border-purple-800">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl">💼</span>
                    就业前景
                  </h3>
                  <div className="text-gray-700 dark:text-gray-300">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">就业方向</h4>
                    {majorV2.employment_directions && majorV2.employment_directions.length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {majorV2.employment_directions.map((direction, index) => (
                          <div key={index} className="bg-white dark:bg-gray-700 rounded-lg px-4 py-3 text-center border border-purple-200 dark:border-purple-700">
                            <span className="text-purple-800 dark:text-purple-200 font-medium">{direction}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400">暂无就业方向信息</p>
                    )}
                  </div>
                </div>

                {/* 4️⃣ 注意事项 */}
                <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl p-6 border border-orange-100 dark:border-orange-800">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl">⚠️</span>
                    注意事项
                  </h3>
                  <div className="space-y-4">
                    {majorV2.warnings?.learning_requirements && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">📚 学习要求</h4>
                        <ul className="space-y-1">
                          {majorV2.warnings.learning_requirements.map((req, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-orange-600 dark:text-orange-400 mt-0.5">•</span>
                              <span className="text-gray-700 dark:text-gray-300">{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {majorV2.warnings?.employment_requirements && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">💼 就业要求</h4>
                        <ul className="space-y-1">
                          {majorV2.warnings.employment_requirements.map((req, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-orange-600 dark:text-orange-400 mt-0.5">•</span>
                              <span className="text-gray-700 dark:text-gray-300">{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {majorV2.warnings?.salary_workload && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">💰 薪资与工作强度</h4>
                        <ul className="space-y-1">
                          {majorV2.warnings.salary_workload.map((req, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-orange-600 dark:text-orange-400 mt-0.5">•</span>
                              <span className="text-gray-700 dark:text-gray-300">{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {majorV2.warnings?.career_stability && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">🔄 职业稳定性</h4>
                        <ul className="space-y-1">
                          {majorV2.warnings.career_stability.map((req, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-orange-600 dark:text-orange-400 mt-0.5">•</span>
                              <span className="text-gray-700 dark:text-gray-300">{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {majorV2.warnings?.development_space && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">📈 发展空间</h4>
                        <ul className="space-y-1">
                          {majorV2.warnings.development_space.map((req, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-orange-600 dark:text-orange-400 mt-0.5">•</span>
                              <span className="text-gray-700 dark:text-gray-300">{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {majorV2.warnings?.development_suggestions && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">💡 发展建议</h4>
                        <ul className="space-y-1">
                          {majorV2.warnings.development_suggestions.map((req, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-orange-600 dark:text-orange-400 mt-0.5">•</span>
                              <span className="text-gray-700 dark:text-gray-300">{req}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
                </div>
                </div>
              </motion.div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">正在加载专业详细信息...</p>
              </div>
            )}
          </div>
      </motion.div>
    </div>
  );
};

export default MajorDetailPage;