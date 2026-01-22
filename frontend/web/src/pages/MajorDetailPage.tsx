import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

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
  universities?: UniversityGroup[];
}

interface MajorNote {
  category: string;
  icon: string;
  points: string[];
  suggestions?: string[];
}

interface UniversityGroup {
  type: string;
  name: string;
  universities: University[];
}

interface University {
  name: string;
  level: string;
  employment_rate: string;
  location: string;
  admission_score?: string;
  match_reason?: string;
  province: string;
}

interface UserTarget {
  province: string;
  score: number;
}

const API_BASE = 'http://localhost:8004';

const MajorDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [major, setMajor] = useState<MajorDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [userTarget, setUserTarget] = useState<UserTarget | null>(null);
  const [showTargetModal, setShowTargetModal] = useState(false);
  const [targetForm, setTargetForm] = useState({ province: '', score: '' });

  useEffect(() => {
    const savedTarget = localStorage.getItem('userTarget');
    if (savedTarget) {
      setUserTarget(JSON.parse(savedTarget));
    } else {
      setShowTargetModal(true);
    }
  }, []);

  useEffect(() => {
    const fetchMajorDetail = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE}/api/v1/major/market-data?page_size=100`);
        if (!response.ok) throw new Error('获取专业详情失败');
        const data = await response.json();
        
        // 按id过滤找到对应的专业
        const targetId = parseInt(id);
        const targetItem = (data.data || []).find((item: any) => item.id === targetId);
        
        if (targetItem) {
          setMajor(generateMockDetail(targetItem));
        } else {
          // 如果没找到，使用模拟数据
          setMajor(generateMockDetailFromId(targetId));
        }
      } catch (err) {
        console.error('获取专业详情失败:', err);
        // 使用模拟数据
        setMajor(generateMockDetailFromId(parseInt(id)));
      } finally {
        setLoading(false);
      }
    };

    fetchMajorDetail();
  }, [id]);

  const generateMockDetail = (item: any): MajorDetail => {
    return {
      id: item.id,
      major_name: item.major_name || item.title,
      category: item.category,
      employment_rate: item.employment_rate,
      avg_salary: item.avg_salary,
      heat_index: item.heat_index,
      courses: item.courses || ['专业基础课', '专业核心课', '专业选修课', '实践课程'],
      description: `${item.major_name || item.title}专业培养具备扎实理论基础和实践能力的高级专门人才。`,
      career_prospects: '毕业生可在相关领域从事研究、开发、管理等工作，就业前景广阔。',
      notes: getNotesByCategory(item.category || '工学'),
      universities: getUniversitiesByCategory(item.major_name || '计算机科学与技术', item.category)
    };
  };

  const generateMockDetailFromId = (id: number): MajorDetail => {
    const mockMajors: Record<number, { name: string; category: string }> = {
      1: { name: '计算机科学与技术', category: '工学' },
      2: { name: '人工智能', category: '工学' },
      3: { name: '数据科学与大数据技术', category: '理学' },
      4: { name: '金融学', category: '经济学' },
      5: { name: '临床医学', category: '医学' },
      9: { name: '软件工程', category: '工学' },
      10: { name: '人工智能', category: '工学' },
    };
    
    const mock = mockMajors[id] || { name: '专业名称', category: '工学' };
    return {
      id,
      major_name: mock.name,
      category: mock.category,
      employment_rate: 90 + Math.random() * 10,
      avg_salary: '15K-25K/月',
      heat_index: 85 + Math.random() * 15,
      courses: ['课程1', '课程2', '课程3', '课程4'],
      description: `${mock.name}专业培养具备扎实理论基础和实践能力的高级专门人才。`,
      career_prospects: '毕业生可在相关领域从事研究、开发、管理等工作。',
      notes: getNotesByCategory(mock.category),
      universities: getUniversitiesByCategory(mock.name, mock.category)
    };
  };

  const getNotesByCategory = (category: string): MajorNote[] => {
    const notesMap: Record<string, MajorNote[]> = {
      '工学': [
        {
          category: '💰 薪资与工作强度',
          icon: '💰',
          points: ['起薪较高，但工作强度大，加班是常态', '薪资与个人能力挂钩，差距较大'],
          suggestions: ['建议在校期间多参与项目实践，积累经验']
        },
        {
          category: '🔄 职业稳定性',
          icon: '🔄',
          points: ['35岁后可能面临职业转型或淘汰风险', '行业变化快，需持续学习新技术'],
          suggestions: ['提前规划职业发展方向，不局限于技术路线']
        },
        {
          category: '📈 发展空间',
          icon: '📈',
          points: ['入门门槛低但精通难', '建议深耕细分领域或转向管理/架构方向'],
          suggestions: ['持续学习，关注行业前沿技术']
        }
      ],
      '医学': [
        {
          category: '📚 学历要求',
          icon: '📚',
          points: ['需读到博士（三甲医院门槛）', '硕士就业压力大，本科基本无法进入好医院'],
          suggestions: ['做好长期学习的准备，本科期间扎实基础']
        },
        {
          category: '💰 薪资与工作强度',
          icon: '💰',
          points: ['规培期工资低（3-5年）', '工作强度大（夜班、值班）'],
          suggestions: ['保持良好心态，熬过规培期就好了']
        },
        {
          category: '🔄 职业稳定性',
          icon: '🔄',
          points: ['一旦进入正规医院，工作非常稳定', '越老越吃香，铁饭碗属性强'],
          suggestions: ['稳定发展，提升专业技能']
        }
      ],
      '法学': [
        {
          category: '📚 学历要求',
          icon: '📚',
          points: ['需通过法考（通过率约15%）', '红圈所对学历要求极高'],
          suggestions: ['提前准备法考，在校期间多参与模拟法庭']
        },
        {
          category: '🔄 职业稳定性',
          icon: '🔄',
          points: ['案源是关键', '独立执业前收入不稳定'],
          suggestions: ['积累人脉资源，提升专业能力']
        }
      ],
      '经济学': [
        {
          category: '📚 学历要求',
          icon: '📚',
          points: ['头部机构只要清北复交', '硕士是起步学历，竞争极其激烈'],
          suggestions: ['提升学历背景，积累实习经验']
        },
        {
          category: '💰 薪资与工作强度',
          icon: '💰',
          points: ['起薪高但压力大', '考核指标重，人脉资源很重要'],
          suggestions: ['培养综合素质，建立人脉网络']
        },
        {
          category: '🔄 职业稳定性',
          icon: '🔄',
          points: ['行业周期性明显', '牛市高薪熊市裁员'],
          suggestions: ['做好心理准备，培养抗压能力']
        }
      ]
    };
    
    return notesMap[category] || notesMap['工学'];
  };

  const getUniversitiesByCategory = (majorName: string, category: string): UniversityGroup[] => {
    const universities: University[] = [
      { name: '清华大学', level: '985/211', employment_rate: '99%', location: '北京', admission_score: '680+', province: '北京' },
      { name: '北京大学', level: '985/211', employment_rate: '98%', location: '北京', admission_score: '675+', province: '北京' },
      { name: '复旦大学', level: '985/211', employment_rate: '96%', location: '上海', admission_score: '665+', province: '上海' },
      { name: '上海交通大学', level: '985/211', employment_rate: '97%', location: '上海', admission_score: '670+', province: '上海' },
      { name: '浙江大学', level: '985/211', employment_rate: '97%', location: '杭州', admission_score: '665+', province: '浙江' },
      { name: '南京大学', level: '985/211', employment_rate: '95%', location: '南京', admission_score: '650+', province: '江苏' },
      { name: '中国科学技术大学', level: '985/211', employment_rate: '98%', location: '合肥', admission_score: '660+', province: '安徽' },
      { name: '华中科技大学', level: '985/211', employment_rate: '94%', location: '武汉', admission_score: '630+', province: '湖北' },
      { name: '武汉大学', level: '985/211', employment_rate: '94%', location: '武汉', admission_score: '630+', province: '湖北' },
      { name: '西安交通大学', level: '985/211', employment_rate: '93%', location: '西安', admission_score: '620+', province: '陕西' },
      { name: '哈尔滨工业大学', level: '985/211', employment_rate: '95%', location: '哈尔滨', admission_score: '640+', province: '黑龙江' },
      { name: '中山大学', level: '985/211', employment_rate: '96%', location: '广州', admission_score: '630+', province: '广东' },
      { name: '四川大学', level: '985/211', employment_rate: '93%', location: '成都', admission_score: '620+', province: '四川' },
      { name: '山东大学', level: '985/211', employment_rate: '92%', location: '济南', admission_score: '620+', province: '山东' },
      { name: '吉林大学', level: '985/211', employment_rate: '91%', location: '长春', admission_score: '610+', province: '吉林' },
      { name: '厦门大学', level: '985/211', employment_rate: '94%', location: '厦门', admission_score: '620+', province: '福建' },
      { name: '天津大学', level: '985/211', employment_rate: '92%', location: '天津', admission_score: '630+', province: '天津' },
      { name: '东南大学', level: '985/211', employment_rate: '93%', location: '南京', admission_score: '640+', province: '江苏' },
      { name: '同济大学', level: '985/211', employment_rate: '95%', location: '上海', admission_score: '660+', province: '上海' },
      { name: '北京航空航天大学', level: '985/211', employment_rate: '97%', location: '北京', admission_score: '660+', province: '北京' },
      // 山西省大学
      { name: '山西大学', level: '双一流', employment_rate: '88%', location: '太原', admission_score: '560+', province: '山西' },
      { name: '太原理工大学', level: '211', employment_rate: '87%', location: '太原', admission_score: '550+', province: '山西' },
      { name: '中北大学', level: '省属重点', employment_rate: '85%', location: '太原', admission_score: '530+', province: '山西' },
      // 江苏省大学
      { name: '苏州大学', level: '211', employment_rate: '93%', location: '苏州', admission_score: '600+', province: '江苏' },
      { name: '南京航空航天大学', level: '211', employment_rate: '94%', location: '南京', admission_score: '610+', province: '江苏' },
      { name: '南京理工大学', level: '211', employment_rate: '93%', location: '南京', admission_score: '610+', province: '江苏' },
      { name: '河海大学', level: '211', employment_rate: '92%', location: '南京', admission_score: '600+', province: '江苏' },
      // 浙江省大学
      { name: '浙江大学', level: '985/211', employment_rate: '97%', location: '杭州', admission_score: '665+', province: '浙江' },
      { name: '浙江工业大学', level: '省属重点', employment_rate: '91%', location: '杭州', admission_score: '600+', province: '浙江' },
      { name: '宁波大学', level: '双一流', employment_rate: '90%', location: '宁波', admission_score: '590+', province: '浙江' },
      // 广东省大学
      { name: '华南理工大学', level: '985/211', employment_rate: '96%', location: '广州', admission_score: '630+', province: '广东' },
      { name: '暨南大学', level: '211', employment_rate: '93%', location: '广州', admission_score: '610+', province: '广东' },
      { name: '深圳大学', level: '省属重点', employment_rate: '94%', location: '深圳', admission_score: '600+', province: '广东' },
      // 北京市大学
      { name: '北京师范大学', level: '985/211', employment_rate: '96%', location: '北京', admission_score: '650+', province: '北京' },
      { name: '中国人民大学', level: '985/211', employment_rate: '98%', location: '北京', admission_score: '670+', province: '北京' },
      { name: '北京理工大学', level: '985/211', employment_rate: '96%', location: '北京', admission_score: '655+', province: '北京' },
      // 上海市大学
      { name: '华东师范大学', level: '985/211', employment_rate: '95%', location: '上海', admission_score: '645+', province: '上海' },
      { name: '同济大学', level: '985/211', employment_rate: '95%', location: '上海', admission_score: '660+', province: '上海' },
      { name: '华东理工大学', level: '211', employment_rate: '93%', location: '上海', admission_score: '620+', province: '上海' },
    ];

    const targetProvince = userTarget?.province || '';
    const targetScore = userTarget?.score || 0;
    
    // 分数匹配大学（±30分范围）
    const group1: University[] = targetScore > 0
      ? universities
          .filter(u => {
            const score = parseInt(u.admission_score?.replace('+', '') || '0');
            return score > 0 && score <= targetScore + 30 && score >= Math.max(500, targetScore - 30);
          })
          .sort((a, b) => {
            const scoreA = parseInt(a.admission_score?.replace('+', '') || '0');
            const scoreB = parseInt(b.admission_score?.replace('+', '') || '0');
            return scoreB - scoreA;
          })
          .slice(0, 5)
      : universities.slice(0, 5);
    
    // 同省优质大学
    const group2: University[] = targetProvince
      ? universities
          .filter(u => u.province === targetProvince)
          .sort((a, b) => {
            const rateA = parseFloat(a.employment_rate.replace('%', ''));
            const rateB = parseFloat(b.employment_rate.replace('%', ''));
            return rateB - rateA;
          })
          .slice(0, 5)
      : [];
    
    // 全国推荐大学（按就业率排序前10，排除已显示的）
    const shownNames = new Set([...group1, ...group2].map(u => u.name));
    const group3: University[] = universities
      .filter(u => !shownNames.has(u.name))
      .sort((a, b) => {
        const rateA = parseFloat(a.employment_rate.replace('%', ''));
        const rateB = parseFloat(b.employment_rate.replace('%', ''));
        return rateB - rateA;
      })
      .slice(0, 5);

    const groups: UniversityGroup[] = [];
    
    if (group1.length > 0) {
      groups.push({
        type: 'score',
        name: targetScore > 0 ? `🏆 分数匹配大学（约${targetScore}分）` : '🏆 分数匹配大学',
        universities: group1.map(u => ({ 
          ...u, 
          match_reason: `录取分${u.admission_score}，${u.location}高校` 
        }))
      });
    }
    
    if (group2.length > 0) {
      groups.push({
        type: 'province',
        name: targetProvince ? `📍 ${targetProvince}省优质大学` : '📍 同省优质大学',
        universities: group2.map(u => ({ 
          ...u, 
          match_reason: `本省高校，就业率${u.employment_rate}，位于${u.location}` 
        }))
      });
    }
    
    if (group3.length > 0) {
      groups.push({
        type: 'national',
        name: '🌟 全国推荐大学',
        universities: group3.map(u => ({ 
          ...u, 
          match_reason: `全国${u.level}高校，就业率${u.employment_rate}` 
        }))
      });
    }

    return groups;
  };

  const getCityByProvince = (province: string): string => {
    const map: Record<string, string> = {
      '北京': '北京', '天津': '天津', '河北': '石家庄', '山西': '太原',
      '内蒙古': '呼和浩特', '辽宁': '沈阳', '吉林': '长春', '黑龙江': '哈尔滨',
      '上海': '上海', '江苏': '南京', '浙江': '杭州', '安徽': '合肥',
      '福建': '福州', '江西': '南昌', '山东': '济南', '河南': '郑州',
      '湖北': '武汉', '湖南': '长沙', '广东': '广州', '广西': '南宁',
      '海南': '海口', '重庆': '重庆', '四川': '成都', '贵州': '贵阳',
      '云南': '昆明', '西藏': '拉萨', '陕西': '西安', '甘肃': '兰州',
      '青海': '西宁', '宁夏': '银川', '新疆': '乌鲁木齐'
    };
    return map[province] || '北京';
  };

  const handleSaveTarget = () => {
    if (targetForm.province && targetForm.score) {
      const target: UserTarget = {
        province: targetForm.province,
        score: parseInt(targetForm.score)
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
          <motion.div
            className="text-4xl mb-4"
            animate={{ scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
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
        <button onClick={() => navigate('/majors')} className="btn-primary mt-4">
          返回专业列表
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.button
        onClick={() => navigate('/majors')}
        className="mb-4 text-primary-600 hover:text-primary-800 dark:text-primary-400 flex items-center gap-2 font-medium"
        whileHover={{ x: -5 }}
      >
        ← 返回专业列表
      </motion.button>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card bg-white dark:bg-gray-800"
      >
        <div className="border-b border-gray-100 dark:border-gray-700 pb-4 mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3">{major.major_name}</h1>
          <div className="flex flex-wrap gap-3">
            <span className="px-4 py-1.5 bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium border border-blue-100 dark:border-blue-800">
              {major.category}
            </span>
            <span className="px-4 py-1.5 bg-orange-50 dark:bg-orange-900/50 text-orange-700 dark:text-orange-300 rounded-full text-sm font-medium border border-orange-100 dark:border-orange-800">
              🔥 热度 {major.heat_index?.toFixed(1) || '暂无'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 rounded-xl p-5 text-center border border-blue-100 dark:border-blue-800">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">
              {major.employment_rate ? `${major.employment_rate}%` : '暂无'}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">就业率</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30 rounded-xl p-5 text-center border border-green-100 dark:border-green-800">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">
              {major.avg_salary || '暂无'}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">平均薪资</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30 rounded-xl p-5 text-center border border-purple-100 dark:border-purple-800">
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-1">
              {major.heat_index?.toFixed(1) || '暂无'}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">热度指数</div>
          </div>
        </div>

            {major.universities && major.universities.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">🏫 推荐大学</h2>
              <button
                onClick={() => setShowTargetModal(true)}
                className="px-4 py-1.5 text-sm text-primary-600 hover:text-primary-800 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded-lg transition-colors"
              >
                {userTarget ? '✏️ 修改目标' : '🎯 设置目标'}
              </button>
            </div>
            
            {userTarget && (
              <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg border border-blue-100 dark:border-blue-800">
                <p className="text-sm text-blue-800 dark:text-blue-300 font-medium">
                  🎯 您的目标：{userTarget.province}省 · 预估分数 {userTarget.score || '--'}分
                </p>
              </div>
            )}

            {major.universities.map((group, idx) => (
              <div key={group.type} className="mb-6">
                <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                  <span className="w-1 h-5 bg-primary-500 rounded-full"></span>
                  {group.name}
                </h3>
                <div className="space-y-3">
                  {group.universities.map((uni, uidx) => (
                    <motion.div
                      key={uni.name}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 + uidx * 0.05 }}
                      className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-gray-100 dark:border-gray-600 hover:shadow-md transition-shadow"
                    >
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className="font-semibold text-lg text-gray-900 dark:text-white">{uni.name}</span>
                        <span className="px-2.5 py-0.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs rounded font-medium">
                          {uni.level}
                        </span>
                        {uni.admission_score && (
                          <span className="px-2.5 py-0.5 bg-gradient-to-r from-green-500 to-green-600 text-white text-xs rounded font-medium">
                            📊 录取分 {uni.admission_score}
                          </span>
                        )}
                        <span className="px-2.5 py-0.5 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 text-xs rounded">
                          💼 就业率 {uni.employment_rate}
                        </span>
                        <span className="px-2.5 py-0.5 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 text-xs rounded">
                          📍 {uni.location}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 bg-white/50 dark:bg-gray-800/50 rounded px-3 py-2">
                        💡 {uni.match_reason}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {major.notes && major.notes.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700">
              <span>⚠️</span> 注意事项
            </h2>
            <div className="space-y-4">
              {major.notes.map((note, idx) => (
                <motion.div
                  key={note.category}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl p-5 border border-orange-100 dark:border-orange-800"
                >
                  <h3 className="font-semibold text-orange-900 dark:text-orange-300 mb-3 flex items-center gap-2">
                    <span className="text-lg">{note.icon}</span>
                    {note.category.replace(/[💰🔄📚📈🎯]/g, '').trim()}
                  </h3>
                  <ul className="space-y-2">
                    {note.points.map((point, pidx) => (
                      <li key={pidx} className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2">
                        <span className="text-orange-500 mt-0.5">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                  {note.suggestions && note.suggestions.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-orange-200 dark:border-orange-800">
                      <p className="text-sm font-medium text-orange-800 dark:text-orange-400 mb-2 flex items-center gap-1">
                        💡 <span>发展建议</span>
                      </p>
                      <div className="space-y-1">
                        {note.suggestions.map((s, sidx) => (
                          <p key={sidx} className="text-sm text-gray-600 dark:text-gray-400 pl-5">• {s}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {major.courses && major.courses.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700">
              <span>📚</span> 核心课程
            </h2>
            <div className="flex flex-wrap gap-2">
              {major.courses.map((course, idx) => (
                <span
                  key={idx}
                  className="px-4 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-700 dark:text-blue-300 rounded-lg text-sm font-medium border border-blue-100 dark:border-blue-800"
                >
                  {course}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700">
            <span>💡</span> 专业介绍
          </h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
            {major.description}
          </p>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700">
            <span>🎯</span> 就业前景
          </h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
            {major.career_prospects}
          </p>
        </div>
      </motion.div>

      {showTargetModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-xl p-6 w-full max-w-md mx-4"
          >
            <h2 className="text-xl font-bold mb-4">🎯 设置您的目标</h2>
            <p className="text-sm text-gray-500 mb-4">
              设置省份和预估分数，获取个性化的大学推荐
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  目标省份
                </label>
                <select
                  className="input w-full"
                  value={targetForm.province}
                  onChange={(e) => setTargetForm({ ...targetForm, province: e.target.value })}
                >
                  <option value="">请选择省份</option>
                  <option value="北京">北京</option>
                  <option value="天津">天津</option>
                  <option value="河北">河北</option>
                  <option value="山西">山西</option>
                  <option value="内蒙古">内蒙古</option>
                  <option value="辽宁">辽宁</option>
                  <option value="吉林">吉林</option>
                  <option value="黑龙江">黑龙江</option>
                  <option value="上海">上海</option>
                  <option value="江苏">江苏</option>
                  <option value="浙江">浙江</option>
                  <option value="安徽">安徽</option>
                  <option value="福建">福建</option>
                  <option value="江西">江西</option>
                  <option value="山东">山东</option>
                  <option value="河南">河南</option>
                  <option value="湖北">湖北</option>
                  <option value="湖南">湖南</option>
                  <option value="广东">广东</option>
                  <option value="广西">广西</option>
                  <option value="海南">海南</option>
                  <option value="重庆">重庆</option>
                  <option value="四川">四川</option>
                  <option value="贵州">贵州</option>
                  <option value="云南">云南</option>
                  <option value="陕西">陕西</option>
                  <option value="甘肃">甘肃</option>
                  <option value="青海">青海</option>
                  <option value="宁夏">宁夏</option>
                  <option value="新疆">新疆</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  预估分数
                </label>
                <input
                  type="number"
                  className="input w-full"
                  placeholder="请输入预估分数"
                  value={targetForm.score}
                  onChange={(e) => setTargetForm({ ...targetForm, score: e.target.value })}
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowTargetModal(false)}
                  className="flex-1 btn-secondary"
                >
                  取消
                </button>
                <button
                  onClick={handleSaveTarget}
                  disabled={!targetForm.province || !targetForm.score}
                  className="flex-1 btn-primary disabled:opacity-50"
                >
                  确认应用
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default MajorDetailPage;
