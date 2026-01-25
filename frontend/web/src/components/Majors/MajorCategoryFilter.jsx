import React, { useState, useEffect } from 'react';
import './MajorCategoryFilter.css';

/**
 * 专业分类筛选器组件
 * 提供专业分类筛选功能
 */
const MajorCategoryFilter = ({ selectedCategory, onCategoryChange, categories = [] }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 如果没有传入categories，则从API获取
    if (categories.length === 0) {
      fetchCategories();
    } else {
      setLoading(false);
    }
  }, [categories]);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8004/api/v1/majors/categories');
      const data = await response.json();
      
      if (data.success) {
        // 使用传入的onCategoryChange更新categories
        // 这里假设父组件会处理categories的更新
      } else {
        setError('获取专业分类失败');
      }
    } catch (err) {
      setError('网络错误');
      console.error('获取专业分类失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (categoryId) => {
    onCategoryChange(categoryId === selectedCategory ? null : categoryId);
  };

  const handleReset = () => {
    onCategoryChange(null);
  };

  if (loading) {
    return (
      <div className="category-filter loading">
        <div className="loading-spinner">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="category-filter error">
        <div className="error-message">{error}</div>
        <button onClick={fetchCategories} className="retry-btn">重试</button>
      </div>
    );
  }

  return (
    <div className="category-filter">
      <div className="filter-header">
        <h3>专业分类</h3>
        <button 
          onClick={handleReset} 
          className="reset-btn"
          disabled={!selectedCategory}
        >
          重置
        </button>
      </div>
      
      <div className="category-list">
        {categories.map((category) => (
          <div
            key={category.id}
            className={`category-item ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => handleCategoryClick(category.id)}
          >
            <div className="category-name">{category.name}</div>
            <div className="category-code">{category.code}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MajorCategoryFilter;