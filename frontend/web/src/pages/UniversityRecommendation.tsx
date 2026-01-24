// 大学推荐页面
import React, { useState, useEffect } from 'react';
import { UniversityAPI } from '../services/universityAPI';
import { RecommendationResponse } from '../types/university';
import SearchForm from '../components/SearchForm';
import UniversityGroups from '../components/UniversityGroups';
import LoadingSpinner from '../components/LoadingSpinner';

const UniversityRecommendation: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (searchParams: { major: string; province?: string; score?: number }) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await UniversityAPI.getRecommendations(searchParams);
      setRecommendations(result);
      console.log('推荐结果:', result);
    } catch (err) {
      console.error('获取推荐失败:', err);
      setError(err instanceof Error ? err.message : '获取推荐失败，请稍后重试');
      setRecommendations(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewDetail = (universityId: number) => {
    console.log('查看大学详情:', universityId);
    // TODO: 实现大学详情页面或模态框
    // 可以使用导航：history.push(`/universities/${universityId}`);
    // 或者打开模态框显示详细信息
  };

  useEffect(() => {
    // 页面加载时健康检查
    const checkAPIHealth = async () => {
      try {
        const health = await UniversityAPI.healthCheck();
        console.log('API健康状态:', health);
      } catch (err) {
        console.error('API健康检查失败:', err);
        setError('推荐服务暂时不可用，请稍后重试');
      }
    };
    
    checkAPIHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 页面头部 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-2xl mr-3">🎓</span>
              <h1 className="text-2xl font-bold text-gray-900">智能大学推荐</h1>
            </div>
            <div className="text-sm text-gray-500">
              为高中生提供个性化的大学推荐服务
            </div>
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 搜索表单 */}
        <SearchForm onSearch={handleSearch} />

        {/* 加载状态 */}
        {isLoading && (
          <LoadingSpinner 
            size="large" 
            message="正在为您智能推荐最适合的大学..." 
          />
        )}

        {/* 错误状态 */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <div className="flex items-center">
              <span className="text-red-500 text-xl mr-3">⚠️</span>
              <div>
                <h3 className="text-lg font-medium text-red-800">推荐失败</h3>
                <p className="text-red-600 mt-1">{error}</p>
              </div>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-600 text-white font-medium rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              重新加载
            </button>
          </div>
        )}

        {/* 推荐结果 */}
        {!isLoading && !error && recommendations && (
          <div className="space-y-8">
            {/* 推荐统计 */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">📊 推荐结果</h2>
                <div className="text-sm text-gray-500">
                  场景{recommendations.scenario} • 共{recommendations.total}所大学
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(recommendations.groups).map(([key, group]) => (
                  <div key={key} className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {group.count}
                    </div>
                    <div className="text-sm text-gray-600">
                      {group.name.split(' ')[1]}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 分组结果 */}
            <UniversityGroups 
              groups={recommendations.groups}
              scenario={recommendations.scenario}
              onViewDetail={handleViewDetail}
            />
          </div>
        )}

        {/* 空状态提示 */}
        {!isLoading && !error && !recommendations && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <span className="text-6xl mb-4">🎯</span>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">开始您的智能推荐</h2>
            <p className="text-gray-600 mb-6">
              请在上方输入您感兴趣的专业，系统将为您推荐最适合的大学
            </p>
            <div className="text-sm text-gray-500">
              <p>💡 小贴士：</p>
              <ul className="mt-2 space-y-1">
                <li>• 填写专业名称获取基础推荐</li>
                <li>• 添加省份信息获得同省推荐</li>
                <li>• 填写预估分数获得精准匹配</li>
              </ul>
            </div>
          </div>
        )}
      </main>

      {/* 页面底部 */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>© 2026 智能专业选择指导应用 - 帮助高中生找到理想大学</p>
            <div className="mt-2 space-x-4">
              <a href="#" className="text-blue-600 hover:text-blue-800">使用指南</a>
              <a href="#" className="text-blue-600 hover:text-blue-800">联系我们</a>
              <a href="#" className="text-blue-600 hover:text-blue-800">隐私政策</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default UniversityRecommendation;