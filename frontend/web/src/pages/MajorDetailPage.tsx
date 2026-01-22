import React, { useState, useEffect, useMemo } from 'react';
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
  origin: string;
  development: string;
  currentStatus: string;
  trends: string;
  relatedMajors: string[];
}

const API_BASE = 'http://localhost:8004';

const majorIntroductions: Record<string, MajorIntroduction> = {
  '计算机科学与技术': {
    origin: '计算机科学与技术专业源于20世纪中期的计算机科学学科，随着电子计算机的发明而产生。该学科最初服务于军事和科学研究需求，后逐步发展为独立的学术领域。',
    development: '从最初的机器语言编程到高级语言，从大型机到个人电脑，从局域网到互联网，经历了多次技术革命。学科体系从单一的计算机硬件研究，发展为涵盖软件、硬件、网络、人工智能等多领域的综合性学科。',
    currentStatus: '当前是全球最热门的技术学科之一。中国在超级计算、5G通信、人工智能等领域达到世界领先水平。几乎所有高校都开设此专业，年招生规模超过30万人。',
    trends: '人工智能、量子计算、边缘计算、隐私计算等方向是未来发展重点。跨学科融合趋势明显，如计算机+医学、计算机+金融等复合型人才需求旺盛。',
    relatedMajors: ['人工智能', '软件工程', '数据科学与大数据技术', '网络工程', '信息安全']
  },
  '人工智能': {
    origin: '人工智能（AI）作为一门学科诞生于1956年达特茅斯会议。早期研究受限于计算能力，发展经历多次起伏，直到深度学习技术的突破才迎来爆发式增长。',
    development: '从早期的专家系统、机器学习，到深度学习、强化学习，AI经历了多次技术范式转变。2012年AlexNet在ImageNet竞赛中取得突破性成绩，标志着深度学习时代的到来。',
    currentStatus: 'AI技术已广泛应用于各行各业。中国在计算机视觉、自然语言处理等领域处于国际第一梯队。ChatGPT等大语言模型引发新一轮技术革命。',
    trends: '大模型、多模态AI、具身智能、AI for Science是主要发展方向。AI与各行业的深度融合将创造大量就业机会，同时也带来伦理和安全挑战。',
    relatedMajors: ['计算机科学与技术', '数据科学与大数据技术', '自动化', '数学']
  },
  '金融学': {
    origin: '金融学源于经济学，是研究货币、信贷、银行、证券等金融活动及其规律的学科。现代金融学形成于20世纪初，随着金融市场的繁荣发展而不断壮大。',
    development: '从传统的货币银行学，到公司金融、资产定价、行为金融等分支学科的建立，金融学体系日趋完善。数学模型和量化方法在金融领域的应用日益广泛。',
    currentStatus: '金融行业是现代经济体系的核心。中国金融市场规模位居世界前列，但对高端金融人才需求旺盛。 fintech（金融科技）正在重塑传统金融业。',
    trends: '绿色金融、普惠金融、金融科技是发展方向。量化投资、智能投顾、区块链在金融领域的应用将持续深化。',
    relatedMajors: ['经济学', '统计学', '工商管理', '会计学', '数学']
  },
  '临床医学': {
    origin: '临床医学是医学的核心分支，致力于疾病的诊断、治疗和预防。其历史可追溯至古代巫医不分的状态，经过数千年发展逐步成为一门科学。',
    development: '从经验医学到循证医学，从传统诊疗到精准医疗，临床医学经历了深刻变革。影像学、检验医学、内镜技术等大大提高了诊断准确率。',
    currentStatus: '临床医学是医疗体系的基础。中国医疗资源总量大但分布不均，基层医疗人才缺口较大。医患关系、医疗改革是社会热点话题。',
    trends: '精准医学、转化医学、智慧医疗是发展方向。人工智能辅助诊断、基因治疗等新技术将改变传统诊疗模式。',
    relatedMajors: ['基础医学', '口腔医学', '护理学', '公共卫生与预防医学']
  },
  '法学': {
    origin: '法学是研究法律规范及其适用规律的学科。在中国，法学教育始于清末民初的新式学堂，经过百余年的发展已成为高等教育的重要组成部分。',
    development: '从移植西方法律制度到建设中国特色社会主义法治体系，中国法学经历了从借鉴到创新的过程。法理学、宪法学、刑法学、民法学等分支学科体系完备。',
    currentStatus: '全面依法治国战略为法学发展提供了广阔空间。法治政府建设、企业合规管理、国际商事争端解决等领域人才需求旺盛。',
    trends: '数字法学、环境法学、国际法等新兴领域快速发展。法律与科技融合带来新的研究方向和就业机会。',
    relatedMajors: ['社会学', '政治学与行政学', '知识产权', '经济学']
  },
  '社会学': {
    origin: '社会学是一门研究社会关系、社会结构和社会变迁的学科。19世纪末由孔德、涂尔干等学者创立，20世纪初传入中国。',
    development: '从经典社会学到现代社会学，学科理论和方法不断丰富。实证研究方法的引入使社会学更加科学化。中国社会学在社会转型期发挥了重要作用。',
    currentStatus: '社会治理现代化为社会学提供了广阔舞台。社会调查、政策评估、社区建设等领域需要大量专业人才。',
    trends: '数字社会学、人口老龄化、城乡发展等议题研究深入。社会工作、社会政策方向人才需求增加。',
    relatedMajors: ['社会工作', '政治学与行政学', '法学', '心理学']
  },
  '数据科学与大数据技术': {
    origin: '数据科学是21世纪新兴的交叉学科，整合了统计学、计算机科学和领域知识。2012年《哈佛商业评论》称数据科学家为"21世纪最性感职业"。',
    development: '大数据概念2011年由麦肯锡提出后迅速普及。云计算、分布式计算等技术突破使海量数据处理成为可能。数据科学成为企业数字化转型的核心能力。',
    currentStatus: '数据驱动决策已成为各行业共识。中国大数据产业规模超万亿，但数据人才缺口仍达百万级。',
    trends: '数据中台、隐私计算、实时数据处理是技术热点。数据治理、数据安全方向人才需求上升。',
    relatedMajors: ['计算机科学与技术', '统计学', '人工智能', '数学']
  },
  '自动化': {
    origin: '自动化是利用控制系统代替人工操作的工程技术。工业革命催生了自动化需求，20世纪自动控制理论的确立奠定了学科基础。',
    development: '从机械自动化到电气自动化，再到智能自动化，技术水平不断提升。PLC、DCS、工业机器人等设备广泛应用。',
    currentStatus: '智能制造为中国工业转型升级提供支撑。工业互联网、机器人产业快速发展，对自动化人才需求旺盛。',
    trends: '工业互联网、数字孪生、智能机器人是发展方向。人机协作、柔性制造成为新趋势。',
    relatedMajors: ['电气工程及其自动化', '测控技术与仪器', '计算机科学与技术', '机械工程']
  }
};

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

  useEffect(() => {
    const savedTarget = localStorage.getItem('userTarget');
    if (savedTarget) {
      setUserTarget(JSON.parse(savedTarget));
    } else {
      setShowTargetModal(true);
    }
  }, []);

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
              {(() => {
                const intro = majorIntroductions[major.major_name];
                if (!intro) return <p className="text-gray-500">暂无专业介绍</p>;

                const relatedMajors = intro.relatedMajors || [];
                const displayMajor = selectedRelatedMajor || major.major_name;
                const displayIntro = majorIntroductions[displayMajor] || intro;

                return (
                  <div>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {relatedMajors.map((related) => (
                        <button
                          key={related}
                          onClick={() => setSelectedRelatedMajor(related)}
                          className={`px-3 py-1.5 text-sm rounded-full transition-colors ${displayMajor === related ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-primary-100 dark:hover:bg-primary-900/30'}`}
                        >
                          {related}
                        </button>
                      ))}
                    </div>

                    <div className="grid gap-4">
                      <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">🔍 溯源</h4>
                        <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{displayIntro.origin}</p>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">📈 发展</h4>
                        <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{displayIntro.development}</p>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">📊 现状</h4>
                        <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{displayIntro.currentStatus}</p>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">🚀 趋势</h4>
                        <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{displayIntro.trends}</p>
                      </div>
                    </div>

                    <div className="mt-6 p-4 bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20 rounded-lg border border-orange-100 dark:border-orange-800">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">🎬 视频介绍</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">观看视频，深入了解{displayMajor}专业</p>
                      <div className="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                        <span className="text-gray-500 text-sm">🎥 视频功能开发中...</span>
                      </div>
                    </div>
                  </div>
                );
              })()}
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
