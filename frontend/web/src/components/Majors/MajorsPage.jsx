import React, { useState, useEffect } from 'react';
import MajorCategoryFilter from './MajorCategoryFilter';
import MajorList from './MajorList';
import MajorDetail from './MajorDetail';
import './MajorsPage.css';

/**
 * 专业选择页面主组件
 * 整合分类筛选、列表展示和详情查看功能
 */
const MajorsPage = () => {
  const [view, setView] = useState('list'); // 'list' | 'detail'
  const [selectedMajor, setSelectedMajor] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8004/api/v1/majors/categories');
      const data = await response.json();
      
      if (data.success) {
        setCategories(data.data);
      }
    } catch (error) {
      console.error('获取专业分类失败:', error);
    }
  };

  const handleCategoryChange = (categoryId) => {
    setSelectedCategory(categoryId);
    setView('list'); // 切换回列表视图
  };

  const handleMajorClick = (major) => {
    setSelectedMajor(major);
    setView('detail');
  };

  const handleBackToList = () => {
    setView('list');
    setSelectedMajor(null);
  };

  const handleSearchChange = (e) => {
    setSearchKeyword(e.target.value);
    setView('list'); // 搜索时切换回列表视图
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // 搜索逻辑已在MajorList组件中处理
  };

  const renderListView = () => (
    <div className="majors-page">
      {/* 搜索栏 */}
      <div className="search-section">
        <form onSubmit={handleSearchSubmit} className="search-form">
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="搜索专业名称或关键词..."
              value={searchKeyword}
              onChange={handleSearchChange}
              className="search-input"
            />
            <button type="submit" className="search-btn">
              🔍 搜索
            </button>
          </div>
          {searchKeyword && (
            <div className="search-clear">
              当前搜索: <strong>{searchKeyword}</strong>
              <button 
                onClick={() => setSearchKeyword('')}
                className="clear-btn"
              >
                ✕ 清除
              </button>
            </div>
          )}
        </form>
      </div>

      <div className="content-layout">
        {/* 左侧分类筛选 */}
        <aside className="sidebar">
          <MajorCategoryFilter
            selectedCategory={selectedCategory}
            onCategoryChange={handleCategoryChange}
            categories={categories}
          />
        </aside>

        {/* 右侧专业列表 */}
        <main className="main-content">
          <MajorList
            selectedCategory={selectedCategory}
            searchKeyword={searchKeyword}
            onMajorClick={handleMajorClick}
          />
        </main>
      </div>
    </div>
  );

  const renderDetailView = () => (
    <MajorDetail
      majorId={selectedMajor?.id}
      onBack={handleBackToList}
    />
  );

  return (
    <div className="page-container">
      {view === 'list' ? renderListView() : renderDetailView()}
    </div>
  );
};

export default MajorsPage;