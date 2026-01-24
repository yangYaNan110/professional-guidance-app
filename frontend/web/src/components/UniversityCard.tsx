// 大学卡片组件
import React, { useState } from 'react';
import { University, TierScoreData } from '../types/university';

interface UniversityCardProps {
  university: University;
  onViewDetail?: (id: number) => void;
}

const UniversityCard: React.FC<UniversityCardProps> = ({ 
  university, 
  onViewDetail 
}) => {
  const [showTierScores, setShowTierScores] = useState(false);

  const getLevelColor = (level?: string) => {
    switch (level) {
      case '985':
        return 'text-red-600 bg-red-50';
      case '211':
        return 'text-orange-600 bg-orange-50';
      case '双一流':
        return 'text-purple-600 bg-purple-50';
      case '省属重点':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getLevelIcon = (level?: string) => {
    switch (level) {
      case '985':
        return '🎯';
      case '211':
        return '🏫';
      case '双一流':
        return '⭐';
      case '省属重点':
        return '📚';
      default:
        return '🏛️';
    }
  };

  const getTierColor = (tier?: string) => {
    switch (tier) {
      case '985_211':
        return 'border-red-200 bg-red-50';
      case 'provincial_key':
        return 'border-blue-200 bg-blue-50';
      case 'first_tier':
        return 'border-green-200 bg-green-50';
      case 'second_tier':
        return 'border-yellow-200 bg-yellow-50';
      case 'vocational':
        return 'border-purple-200 bg-purple-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border border-gray-200">
      {/* 大学标题 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {university.name}
          </h3>
          
          {/* 地理信息 */}
          <div className="flex items-center text-sm text-gray-600 mb-2">
            <span className="mr-1">📍</span>
            <span>{university.province}</span>
            {university.city && <span className="ml-2">• {university.city}</span>}
          </div>
        </div>
        
        {/* 大学层次 */}
        <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center ${getLevelColor(university.level)}`}>
          <span className="mr-1">{getLevelIcon(university.level)}</span>
          <span>{university.level || '普通本科'}</span>
        </div>
      </div>

      {/* 大学信息 */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {university.employment_rate && (
          <div className="text-sm">
            <span className="text-gray-500">就业率：</span>
            <span className="font-medium text-green-600">{university.employment_rate}%</span>
          </div>
        )}
        
        {university.match_score && (
          <div className="text-sm">
            <span className="text-gray-500">匹配度：</span>
            <span className="font-medium text-blue-600">{(university.match_score * 100).toFixed(0)}%</span>
          </div>
        )}
      </div>

      {/* 多层次分数线展示 */}
      {university.tier_scores && typeof university.tier_scores === 'object' && Object.keys(university.tier_scores).length > 0 && (
        <div className="mb-4">
          <button
            onClick={() => setShowTierScores(!showTierScores)}
            className="flex items-center text-sm text-blue-600 hover:text-blue-800 transition-colors duration-200"
          >
            <span className="mr-1">📊</span>
            <span>查看历年分数线</span>
            <span className="ml-1 text-xs">
              {showTierScores ? '▼' : '▶'}
            </span>
          </button>
          
          {showTierScores && (
            <div className="mt-3 space-y-2">
              {Object.entries(university.tier_scores).map(([tierKey, tierData]) => (
                <div key={tierKey} className={`border rounded-md p-3 ${getTierColor(tierKey)}`}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-sm">{tierData.tier_name}</h4>
                    <span className="text-xs text-gray-600">
                      {tierData.years ? tierData.years.length : 0}年数据
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    {tierData.years && tierData.years.slice(0, 3).map((yearData) => (
                      <div key={yearData.year} className="text-center">
                        <div className="font-medium text-gray-700">{yearData.year}</div>
                        <div className="text-gray-600">
                          {yearData.avg_score ? `${yearData.avg_score}分` : '暂无'}
                        </div>
                        {yearData.admission_type && (
                          <div className="text-gray-500 text-xs">{yearData.admission_type}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 匹配原因 */}
      {university.match_reason && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4">
          <p className="text-sm text-blue-800">
            <span className="font-medium">推荐理由：</span>
            {university.match_reason}
          </p>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => onViewDetail?.(university.id)}
          className="flex-1 mr-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
        >
          查看详情
        </button>
        
        {university.website && (
          <a
            href={university.website}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
            title={`访问${university.name}官方网站`}
          >
            🌐 官网
          </a>
        )}
      </div>
    </div>
  );
};

export default UniversityCard;