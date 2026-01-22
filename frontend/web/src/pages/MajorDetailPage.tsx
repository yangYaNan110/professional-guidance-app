import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import VideoSection from '../components/VideoSection';

interface MajorDetail {
  id: number;
  major_name: string;
  category: string;
  employment_rate: number | null;
  avg_salary: string | null;
  heat_index: number | null;
  courses: string[];
  description: string;
  career_prospects: string;
  notes?: MajorNote[];
}

interface MajorNote {
  category: string;
  icon: string;
  points: string[];
  suggestions?: string[];
}

interface University {
  id: number;
  name: string;
  level: string;
  province: string;
  city: string;
  employment_rate: number;
  type: string;
  major_strengths: string[];
  admission_scores: AdmissionScore[];
  match_type: 'score' | 'province' | 'national';
  match_reason: string;
  latest_score?: AdmissionScore;
}

interface AdmissionScore {
  year: number;
  min_score: number;
  max_score: number;
  avg_score: number;
  province: string;
  batch: string;
}

interface RecommendedUniversitiesResponse {
  universities: University[];
  user_target: {
    province: string | null;
    score: number | null;
    major: string | null;
  };
}

interface UserTarget {
  province: string;
  score?: number;
}

interface MajorIntroduction {
  introduction: string;
  relatedMajors: string[];
}

const API_BASE = 'http://localhost:8004';

// 硬编码的专业介绍数据（备用，现在从API获取）
// const majorIntroductions: Record<string, MajorIntroduction> = {
//   '计算机科学与技术': {
//     origin: '计算机科学与技术专业源于20世纪中期的计算机科学学科...',
//     development: '从最初的机器语言编程到高级语言...',
//     currentStatus: '当前是全球最热门的技术学科之一...',
//     trends: '人工智能、量子计算等方向是未来发展重点...',
//     relatedMajors: ['人工智能', '软件工程', '数据科学与大数据技术', '网络工程', '信息安全']
//   },
//   // ... 其他专业数据
// };

const MajorDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [major, setMajor] = useState<MajorDetail | null>(null);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [userTarget, setUserTarget] = useState<UserTarget | null>(null);
  const [showTargetModal, setShowTargetModal] = useState(false);
  const [targetForm, setTargetForm] = useState({ province: '', score: '' });
  const [activeTab, setActiveTab] = useState<'intro' | 'universities'>('intro');
  const [selectedRelatedMajor, setSelectedRelatedMajor] = useState<string | null>(null);
  const [majorIntro, setMajorIntro] = useState<MajorIntroduction | null>(null);
  const [introLoading, setIntroLoading] = useState(true);

  useEffect(() => {
    const savedTarget = localStorage.getItem('userTarget');
    if (savedTarget) {
      setUserTarget(JSON.parse(savedTarget));
    } else {
      setShowTargetModal(true);
    }
  }, []);

  useEffect(() => {
    const fetchMajorIntro = async () => {
      if (!major?.major_name) return;
      
      try {
        setIntroLoading(true);
        const introResponse = await fetch(`http://localhost:8005/api/v1/major/intro/${encodeURIComponent(major.major_name)}`);
        if (introResponse.ok) {
          const introData = await introResponse.json();
          if (introData.success) {
            setMajorIntro({
              introduction: introData.introduction || '暂无专业介绍',
              relatedMajors: introData.related_majors || []
            });
          }
        }
      } catch (err) {
        console.error('获取专业介绍失败:', err);
      } finally {
        setIntroLoading(false);
      }
    };

    fetchMajorIntro();
  }, [major?.major_name]);

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        
        // 获取专业详情
        const majorResponse = await fetch(`${API_BASE}/api/v1/major/market-data?page_size=100`);
        if (!majorResponse.ok) throw new Error('获取专业详情失败');
        const majorData = await majorResponse.json();
        
        const targetId = parseInt(id);
        const targetItem = (majorData.data || []).find((item: any) => item.id === targetId);
        
        if (targetItem) {
          setMajor({
            id: targetItem.id,
            major_name: targetItem.major_name || targetItem.title,
            category: targetItem.category,
            employment_rate: targetItem.employment_rate,
            avg_salary: targetItem.avg_salary,
            heat_index: targetItem.heat_index,
            courses: targetItem.courses || ['专业基础课', '专业核心课', '专业选修课', '实践课程'],
            description: `${targetItem.major_name || targetItem.title}专业培养具备扎实理论基础和实践能力的高级专门人才，毕业生可在相关领域从事研究、开发、管理等工作。`,
            career_prospects: '随着社会经济发展，该专业人才需求持续增长。毕业生可在相关企业、事业单位、科研院所等从事相关工作，就业前景广阔。建议在校期间多参加实践活动，提升专业技能。',
            notes: getNotesByCategory(targetItem.category || '工学')
          });
        } else {
          setMajor(createDefaultMajor(targetId));
        }

        // 获取推荐大学
        if (userTarget) {
          let apiUrl = `${API_BASE}/api/v1/universities/recommend?province=${encodeURIComponent(userTarget.province)}`;
          if (userTarget.score) {
            apiUrl += `&score=${userTarget.score}`;
          }
          if (major?.name) {
            apiUrl += `&major=${encodeURIComponent(major.name)}`;
          }
          const uniResponse = await fetch(apiUrl);
          if (uniResponse.ok) {
            const uniData: RecommendedUniversitiesResponse = await uniResponse.json();
            setUniversities(uniData.universities || []);
          }
        } else {
          const uniResponse = await fetch(`${API_BASE}/api/v1/universities/recommend`);
          if (uniResponse.ok) {
            const uniData: RecommendedUniversitiesResponse = await uniResponse.json();
            setUniversities(uniData.universities || []);
          }
        }
        
      } catch (err) {
        console.error('获取数据失败:', err);
        setMajor(createDefaultMajor(parseInt(id)));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, userTarget]);

  const createDefaultMajor = (id: number): MajorDetail => {
    const mockMajors: Record<number, { name: string; category: string }> = {
      1: { name: '计算机科学与技术', category: '工学' },
      2: { name: '人工智能', category: '工学' },
      3: { name: '数据科学与大数据技术', category: '理学' },
      4: { name: '金融学', category: '经济学' },
      5: { name: '临床医学', category: '医学' },
    };
    const mock = mockMajors[id] || { name: '专业名称', category: '工学' };
    return {
      id,
      major_name: mock.name,
      category: mock.category,
      employment_rate: 90 + Math.random() * 10,
      avg_salary: '15K-25K/月',
      heat_index: 85 + Math.random() * 15,
      courses: ['专业基础课', '专业核心课', '专业选修课', '实践课程'],
      description: `${mock.name}专业培养具备扎实理论基础和实践能力的高级专门人才。`,
      career_prospects: '毕业生可在相关领域从事研究、开发、管理等工作。',
      notes: getNotesByCategory(mock.category)
    };
  };

  const getNotesByCategory = (category: string): MajorNote[] => {
    const notesMap: Record<string, MajorNote[]> = {
      '工学': [
        { category: '💰 薪资与工作强度', icon: '💰', points: ['起薪较高，但工作强度大，加班是常态', '薪资与个人能力挂钩，差距较大'], suggestions: ['建议在校期间多参与项目实践，积累经验'] },
        { category: '🔄 职业稳定性', icon: '🔄', points: ['35岁后可能面临职业转型或淘汰风险', '行业变化快，需持续学习新技术'], suggestions: ['提前规划职业发展方向，不局限于技术路线'] },
        { category: '📈 发展空间', icon: '📈', points: ['入门门槛低但精通难', '建议深耕细分领域或转向管理/架构方向'], suggestions: ['持续学习，关注行业前沿技术'] }
      ],
      '医学': [
        { category: '📚 学历要求', icon: '📚', points: ['需读到博士（三甲医院门槛）', '硕士就业压力大，本科基本无法进入好医院'], suggestions: ['做好长期学习的准备，本科期间扎实基础'] },
        { category: '💰 薪资与工作强度', icon: '💰', points: ['规培期工资低（3-5年）', '工作强度大（夜班、值班）'], suggestions: ['保持良好心态，熬过规培期就好了'] },
        { category: '🔄 职业稳定性', icon: '🔄', points: ['一旦进入正规医院，工作非常稳定', '越老越吃香，铁饭碗属性强'], suggestions: ['稳定发展，提升专业技能'] }
      ],
      '法学': [
        { category: '📚 学历要求', icon: '📚', points: ['需通过法考（通过率约15%）', '红圈所对学历要求极高'], suggestions: ['提前准备法考，在校期间多参与模拟法庭'] },
        { category: '🔄 职业稳定性', icon: '🔄', points: ['案源是关键', '独立执业前收入不稳定'], suggestions: ['积累人脉资源，提升专业能力'] }
      ],
      '经济学': [
        { category: '📚 学历要求', icon: '📚', points: ['头部机构只要清北复交', '硕士是起步学历，竞争极其激烈'], suggestions: ['提升学历背景，积累实习经验'] },
        { category: '💰 薪资与工作强度', icon: '💰', points: ['起薪高但压力大', '考核指标重，人脉资源很重要'], suggestions: ['培养综合素质，建立人脉网络'] },
        { category: '🔄 职业稳定性', icon: '🔄', points: ['行业周期性明显', '牛市高薪熊市裁员'], suggestions: ['做好心理准备，培养抗压能力'] }
      ]
    };
    return notesMap[category] || notesMap['工学'];
  };

  const universityGroups = useMemo(() => {
    const groups: { type: string; name: string; list: University[] }[] = [];
    
    const scoreGroup = universities.filter(u => u.match_type === 'score');
    const provinceGroup = universities.filter(u => u.match_type === 'province');
    const nationalGroup = universities.filter(u => u.match_type === 'national');
    
    if (scoreGroup.length > 0) {
      groups.push({ type: 'score', name: '🏆 分数匹配大学', list: scoreGroup });
    }
    if (provinceGroup.length > 0) {
      groups.push({ type: 'province', name: '📍 同省优质大学', list: provinceGroup });
    }
    if (nationalGroup.length > 0) {
      groups.push({ type: 'national', name: '🌟 全国推荐大学', list: nationalGroup });
    }
    
    return groups;
  }, [universities]);

  const handleSaveTarget = () => {
    if (targetForm.province) {
      const target: UserTarget = {
        province: targetForm.province,
        score: targetForm.score ? parseInt(targetForm.score) : undefined
      };
      setUserTarget(target);
      localStorage.setItem('userTarget', JSON.stringify(target));
      setShowTargetModal(false);
      window.location.reload();
    }
  };

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

  if (!major) {
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
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3">{major.major_name}</h1>
          <div className="flex flex-wrap gap-3">
            <span className="px-4 py-1.5 bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium border border-blue-100 dark:border-blue-800">{major.category}</span>
            <span className="px-4 py-1.5 bg-orange-50 dark:bg-orange-900/50 text-orange-700 dark:text-orange-300 rounded-full text-sm font-medium border border-orange-100 dark:border-orange-800">🔥 热度 {major.heat_index?.toFixed(1) || '暂无'}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 rounded-xl p-5 text-center border border-blue-100 dark:border-blue-800">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">{major.employment_rate ? `${major.employment_rate.toFixed(1)}%` : '暂无'}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">就业率</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30 rounded-xl p-5 text-center border border-green-100 dark:border-green-800">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">{major.avg_salary || '暂无'}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">平均薪资</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30 rounded-xl p-5 text-center border border-purple-100 dark:border-purple-800">
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-1">{major.heat_index?.toFixed(1) || '暂无'}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">热度指数</div>
          </div>
        </div>

        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4 border-b border-gray-100 dark:border-gray-700">
            <button onClick={() => setActiveTab('intro')} className={`px-4 py-2 font-medium transition-colors ${activeTab === 'intro' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-gray-500 hover:text-gray-700'}`}>
              📚 专业介绍
            </button>
            <button onClick={() => setActiveTab('universities')} className={`px-4 py-2 font-medium transition-colors ${activeTab === 'universities' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-gray-500 hover:text-gray-700'}`}>
              🏫 推荐大学
            </button>
          </div>

          {activeTab === 'intro' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              {introLoading ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">正在加载专业介绍...</p>
                </div>
              ) : majorIntro ? (
                <div>
                  {/* 专业介绍内容 - 一段连贯的文字 */}
                  <div className="prose prose-gray dark:prose-invert max-w-none">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                      {majorIntro.introduction}
                    </p>
                  </div>

                  {/* 相关专业标签 */}
                  {majorIntro.relatedMajors.length > 0 && (
                    <div className="mt-6">
                      <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">相关专业</h4>
                      <div className="flex flex-wrap gap-2">
                        {majorIntro.relatedMajors.map((related) => (
                          <button
                            key={related}
                            onClick={() => {
                              setSelectedRelatedMajor(related);
                              fetch(`http://localhost:8005/api/v1/major/intro/${encodeURIComponent(related)}`)
                                .then(res => res.json())
                                .then(data => {
                                  if (data.success) {
                                    setMajorIntro({
                                      introduction: data.introduction || '暂无专业介绍',
                                      relatedMajors: data.related_majors || []
                                    });
                                  }
                                });
                            }}
                            className={`px-3 py-1.5 text-sm rounded-full transition-colors ${selectedRelatedMajor === related ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-primary-100 dark:hover:bg-primary-900/30'}`}
                          >
                            {related}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 视频模块 */}
                  <VideoSection majorName={major.major_name} />
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">暂无专业介绍</p>
              )}
            </motion.div>
          )}

        </div>

        {major.notes && major.notes.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700"><span>⚠️</span> 注意事项</h2>
            <div className="space-y-4">
              {major.notes.map((note, idx) => (
                <motion.div key={note.category} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }} className="bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl p-5 border border-orange-100 dark:border-orange-800">
                  <h3 className="font-semibold text-orange-900 dark:text-orange-300 mb-3 flex items-center gap-2"><span className="text-lg">{note.icon}</span>{note.category.replace(/[💰🔄📚📈🎯]/g, '').trim()}</h3>
                  <ul className="space-y-2">
                    {note.points.map((point, pidx) => (
                      <li key={pidx} className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2"><span className="text-orange-500 mt-0.5">•</span><span>{point}</span></li>
                    ))}
                  </ul>
                  {note.suggestions && note.suggestions.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-orange-200 dark:border-orange-800">
                      <p className="text-sm font-medium text-orange-800 dark:text-orange-400 mb-2 flex items-center gap-1">💡 <span>发展建议</span></p>
                      <div className="space-y-1">{note.suggestions.map((s, sidx) => (<p key={sidx} className="text-sm text-gray-600 dark:text-gray-400 pl-5">• {s}</p>))}</div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {major.courses && major.courses.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700"><span>📚</span> 核心课程</h2>
            <div className="flex flex-wrap gap-2">{major.courses.map((course, idx) => (<span key={idx} className="px-4 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-700 dark:text-blue-300 rounded-lg text-sm font-medium border border-blue-100 dark:border-blue-800">{course}</span>))}</div>
          </div>
        )}

        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700"><span>💡</span> 专业介绍</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">{major.description}</p>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700"><span>🎯</span> 就业前景</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">{major.career_prospects}</p>
        </div>
      </motion.div>

      {showTargetModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold mb-4 dark:text-white">🎯 设置您的目标</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">设置省份和预估分数，获取个性化的大学推荐</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">目标省份</label>
                <select className="input w-full dark:bg-gray-700 dark:text-white" value={targetForm.province} onChange={(e) => setTargetForm({ ...targetForm, province: e.target.value })}>
                  <option value="">请选择省份</option>
                  {['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '宁夏', '新疆'].map(p => (<option key={p} value={p}>{p}</option>))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">预估分数</label>
                <input type="number" className="input w-full dark:bg-gray-700 dark:text-white" placeholder="请输入预估分数" value={targetForm.score} onChange={(e) => setTargetForm({ ...targetForm, score: e.target.value })} />
              </div>
              <div className="flex gap-3 pt-2">
                <button onClick={() => setShowTargetModal(false)} className="flex-1 btn-secondary dark:bg-gray-700 dark:text-white">取消</button>
                <button onClick={handleSaveTarget} disabled={!targetForm.province} className="flex-1 btn-primary disabled:opacity-50">确认应用</button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default MajorDetailPage;
