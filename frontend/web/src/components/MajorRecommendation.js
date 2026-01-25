import React, { useState, useEffect } from 'react';
import './MajorRecommendation.css';

const MajorRecommendation = () => {
  const [majors, setMajors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('heat_index');
  const [sortOrder, setSortOrder] = useState('desc');
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    totalCount: 0,
    totalPages: 0,
    hasNext: false,
    hasPrev: false
  });
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedMajor, setSelectedMajor] = useState(null);

  // API基础URL
  const API_BASE_URL = 'http://localhost:8002/api/v1';

  // 加载专业分类
  useEffect(() => {
    fetchCategories();
  }, []);

  // 加载专业推荐列表
  useEffect(() => {
    fetchMajors(1, false);
  }, [selectedCategory, sortBy, sortOrder]);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/categories`);
      const result = await response.json();
      
      if (result.success) {
        setCategories(result.data);
      } else {
        console.error('获取分类失败:', result.error);
      }
    } catch (error) {
      console.error('获取分类网络错误:', error);
    }
  };

  const fetchMajors = async (page = 1, isLoadMore = false) => {
    try {
      if (isLoadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }

      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pagination.pageSize.toString(),
        sort_by: sortBy,
        sort_order: sortOrder
      });

      if (selectedCategory) {
        params.append('category_id', selectedCategory);
      }

      const response = await fetch(`${API_BASE_URL}/recommendations?${params}`);
      const result = await response.json();

      if (result.success && result.data.success) {
        const newMajors = result.data.data;
        const newPagination = result.data.pagination;

        if (isLoadMore) {
          setMajors(prev => [...prev, ...newMajors]);
        } else {
          setMajors(newMajors);
        }

        setPagination(newPagination);
        setError('');
      } else {
        setError(result.message || '获取推荐失败');
      }
    } catch (error) {
      setError('网络错误，请稍后重试');
      console.error('获取推荐网络错误:', error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleLoadMore = () => {
    if (pagination.hasNext && !loadingMore) {
      fetchMajors(pagination.page + 1, true);
    }
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleMajorClick = async (major) => {
    try {
      const response = await fetch(`${API_BASE_URL}/majors/${major.id}`);
      const result = await response.json();

      if (result.success) {
        setSelectedMajor(result.data);
        setShowModal(true);
      } else {
        alert('获取专业详情失败: ' + result.message);
      }
    } catch (error) {
      console.error('获取专业详情错误:', error);
      alert('获取专业详情失败，请稍后重试');
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedMajor(null);
  };

  const renderHeatIndex = (heatIndex) => {
    if (!heatIndex) return '暂无数据';
    
    let color = '#666';
    if (heatIndex >= 80) color = '#ff4757';
    else if (heatIndex >= 60) color = '#ffa502';
    else if (heatIndex >= 40) color = '#ffdd59';
    
    return <span style={{ color, fontWeight: 'bold' }}>{heatIndex.toFixed(1)}</span>;
  };

  const renderEmploymentRate = (rate) => {
    if (!rate) return '暂无数据';
    
    let color = '#666';
    if (rate >= 95) color = '#26de81';
    else if (rate >= 85) color = '#20bf6b';
    else if (rate >= 75) color = '#0fb9b1';
    
    return <span style={{ color, fontWeight: 'bold' }}>{rate}%</span>;
  };

  const renderSalary = (salary) => {
    if (!salary) return '暂无数据';
    
    let color = '#666';
    if (salary >= 15000) color = '#26de81';
    else if (salary >= 12000) color = '#20bf6b';
    else if (salary >= 10000) color = '#0fb9b1';
    
    return <span style={{ color, fontWeight: 'bold' }}>¥{salary.toLocaleString()}</span>;
  };

  return (
    <div className="major-recommendation">
      <header className="header">
        <h1>🎓 专业推荐</h1>
        <p>基于热度指数、就业率、薪资水平等多维度智能推荐</p>
      </header>

      <div className="filters">
        <div className="filter-group">
          <label htmlFor="category">专业分类:</label>
          <select 
            id="category" 
            value={selectedCategory} 
            onChange={handleCategoryChange}
          >
            <option value="">所有分类</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>排序方式:</label>
          <div className="sort-buttons">
            <button
              className={sortBy === 'heat_index' ? 'active' : ''}
              onClick={() => handleSortChange('heat_index')}
            >
              热度指数
            </button>
            <button
              className={sortBy === 'employment_rate' ? 'active' : ''}
              onClick={() => handleSortChange('employment_rate')}
            >
              就业率
            </button>
            <button
              className={sortBy === 'avg_salary' ? 'active' : ''}
              onClick={() => handleSortChange('avg_salary')}
            >
              平均薪资
            </button>
            <button
              className={sortBy === 'future_prospects' ? 'active' : ''}
              onClick={() => handleSortChange('future_prospects')}
            >
              发展前景
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="majors-container">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>加载中...</p>
          </div>
        ) : majors.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📚</div>
            <h3>暂无专业数据</h3>
            <p>请稍后再试或联系管理员</p>
          </div>
        ) : (
          <>
            <div className="majors-grid">
              {majors.map((major, index) => (
                <div 
                  key={major.id} 
                  className="major-card"
                  onClick={() => handleMajorClick(major)}
                >
                  <div className="major-header">
                    <h3 className="major-name">{major.name}</h3>
                    <span className="major-category">{major.category_name}</span>
                  </div>
                  
                  <div className="major-stats">
                    <div className="stat-item">
                      <span className="stat-label">热度指数</span>
                      <span className="stat-value">
                        {renderHeatIndex(major.heat_index)}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">就业率</span>
                      <span className="stat-value">
                        {renderEmploymentRate(major.employment_rate)}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">平均薪资</span>
                      <span className="stat-value">
                        {renderSalary(major.avg_salary)}
                      </span>
                    </div>
                  </div>

                  {major.talent_shortage && (
                    <div className="talent-shortage">
                      🔥 人才紧缺
                    </div>
                  )}

                  <div className="major-footer">
                    <span className="data-period">{major.data_period}</span>
                    <button className="view-details-btn">
                      查看详情 →
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {pagination.hasNext && (
              <div className="load-more-container">
                <button 
                  className="load-more-btn"
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                >
                  {loadingMore ? (
                    <>
                      <div className="small-spinner"></div>
                      加载中...
                    </>
                  ) : (
                    '加载更多'
                  )}
                </button>
              </div>
            )}

            <div className="pagination-info">
              <span>
                显示 {majors.length} / {pagination.totalCount} 个专业
              </span>
              <span>
                第 {pagination.page} / {pagination.totalPages} 页
              </span>
            </div>
          </>
        )}
      </div>

      {/* 专业详情模态框 */}
      {showModal && selectedMajor && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedMajor.name}</h2>
              <button className="close-btn" onClick={closeModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="major-info">
                <div className="info-row">
                  <span className="label">专业代码:</span>
                  <span className="value">{selectedMajor.code || '暂无'}</span>
                </div>
                <div className="info-row">
                  <span className="label">学科分类:</span>
                  <span className="value">{selectedMajor.category_name}</span>
                </div>
                <div className="info-row">
                  <span className="label">学制年限:</span>
                  <span className="value">{selectedMajor.study_period || 4}年</span>
                </div>
                <div className="info-row">
                  <span className="label">授予学位:</span>
                  <span className="value">{selectedMajor.degree_awarded || '暂无'}</span>
                </div>
                {selectedMajor.national_key_major && (
                  <div className="info-row highlight">
                    <span className="label">🏆 国家重点专业</span>
                  </div>
                )}
              </div>

              {selectedMajor.description && (
                <div className="section">
                  <h3>专业介绍</h3>
                  <p>{selectedMajor.description}</p>
                </div>
              )}

              {selectedMajor.training_objective && (
                <div className="section">
                  <h3>培养目标</h3>
                  <p>{selectedMajor.training_objective}</p>
                </div>
              )}

              {selectedMajor.main_courses && selectedMajor.main_courses.length > 0 && (
                <div className="section">
                  <h3>主干课程</h3>
                  <div className="courses">
                    {selectedMajor.main_courses.map((course, index) => (
                      <span key={index} className="course-tag">
                        {course}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedMajor.employment_direction && (
                <div className="section">
                  <h3>就业方向</h3>
                  <p>{selectedMajor.employment_direction}</p>
                </div>
              )}

              {selectedMajor.market_data && (
                <div className="section market-data">
                  <h3>📊 市场行情</h3>
                  <div className="market-stats">
                    <div className="market-stat">
                      <span className="market-label">就业率</span>
                      <span className="market-value">
                        {renderEmploymentRate(selectedMajor.market_data.employment_rate)}
                      </span>
                    </div>
                    <div className="market-stat">
                      <span className="market-label">平均薪资</span>
                      <span className="market-value">
                        {renderSalary(selectedMajor.market_data.avg_salary)}
                      </span>
                    </div>
                    <div className="market-stat">
                      <span className="market-label">热度指数</span>
                      <span className="market-value">
                        {renderHeatIndex(selectedMajor.market_data.heat_index)}
                      </span>
                    </div>
                    <div className="market-stat">
                      <span className="market-label">行业需求</span>
                      <span className="market-value">
                        {selectedMajor.market_data.industry_demand_score || 0}/10
                      </span>
                    </div>
                    <div className="market-stat">
                      <span className="market-label">发展前景</span>
                      <span className="market-value">
                        {selectedMajor.market_data.future_prospects_score || 0}/10
                      </span>
                    </div>
                  </div>
                  
                  {selectedMajor.market_data.talent_shortage && (
                    <div className="talent-shortage-banner">
                      🔥 该专业目前人才紧缺，就业前景良好
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MajorRecommendation;