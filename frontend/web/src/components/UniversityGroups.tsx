// 大学分组展示组件
import React from 'react';
import { UniversityGroup, University } from '../types/university';
import UniversityCard from './UniversityCard';

interface UniversityGroupsProps {
  groups: Record<string, UniversityGroup>;
  scenario: string;
  onViewDetail: (id: number) => void;
}

const UniversityGroups: React.FC<UniversityGroupsProps> = ({ 
  groups, 
  scenario, 
  onViewDetail 
}) => {
  const getScenarioDescription = () => {
    switch (scenario) {
      case 'A':
        return '根据您提供的专业、省份和分数，为您推荐匹配度最高的大学';
      case 'B':
        return '根据您提供的专业和省份，为您推荐同省优质大学和全国知名高校';
      case 'C':
        return '根据您提供的专业，为您推荐全国范围内该专业的优质高校';
      default:
        return '为您推荐最适合的大学';
    }
  };

  const getEmptyStateMessage = () => {
    switch (scenario) {
      case 'A':
        return '很抱歉，未找到符合您分数和专业的匹配大学，请尝试调整分数或专业';
      case 'B':
        return '很抱歉，该省份暂无您专业的优质大学推荐，建议查看全国推荐';
      case 'C':
        return '很抱歉，暂无该专业的推荐信息，请尝试其他热门专业';
      default:
        return '暂无推荐结果，请检查搜索条件';
    }
  };

  // 获取分组显示顺序
  const getGroupOrder = (): string[] => {
    if (scenario === 'A') {
      return ['province_score_match', 'national_score_match'];
    } else if (scenario === 'B') {
      return ['province_match', 'national_match'];
    } else {
      return ['national_match'];
    }
  };

  const groupOrder = getGroupOrder();

  return (
    <div className="space-y-8">
      {/* 场景说明 */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center mb-2">
          <span className="text-2xl mr-3">
            {scenario === 'A' ? '🎯' : scenario === 'B' ? '📍' : '🌟'}
          </span>
          <h3 className="text-lg font-semibold text-gray-900">
            场景{scenario}推荐
          </h3>
        </div>
        <p className="text-gray-700">{getScenarioDescription()}</p>
      </div>

      {/* 分组结果 */}
      {Object.keys(groups).length > 0 ? (
        groupOrder.map(groupKey => {
          const group = groups[groupKey];
          if (!group || group.universities.length === 0) {
            return null;
          }

          return (
            <div key={groupKey} className="bg-white rounded-lg shadow-md overflow-hidden">
              {/* 分组标题 */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-xl mr-2">{group.name}</span>
                    <span className="text-sm text-gray-500">({group.count}所大学)</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="mr-1">📊</span>
                    <span>匹配度优先</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-2">{group.description}</p>
              </div>

              {/* 大学列表 */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {group.universities.map((university) => (
                    <UniversityCard
                      key={university.id}
                      university={university}
                      onViewDetail={onViewDetail}
                    />
                  ))}
                </div>
              </div>
            </div>
          );
        }).filter(Boolean)
      ) : (
        /* 空状态 */
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">暂无推荐结果</h3>
          <p className="text-gray-600 mb-4">{getEmptyStateMessage()}</p>
          <div className="text-sm text-gray-500">
            <p>建议：</p>
            <ul className="mt-2 space-y-1 text-left inline-block">
              <li>• 尝试调整分数范围（±50分）</li>
              <li>• 选择相关专业（如：人工智能 → 计算机科学与技术）</li>
              <li>• 填写更多省份信息</li>
            </ul>
          </div>
        </div>
      )}

      {/* 推荐统计 */}
      {Object.keys(groups).length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">📈 推荐统计</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            {groupOrder.map(groupKey => {
              const group = groups[groupKey];
              return (
                <div key={groupKey} className="bg-gray-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-blue-600">
                    {group ? group.count : 0}
                  </div>
                  <div className="text-sm text-gray-600">
                    {group ? group.name.split(' ')[1] : '无数据'}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default UniversityGroups;