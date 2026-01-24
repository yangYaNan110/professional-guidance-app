// 大学推荐API服务
import { RecommendationRequest, RecommendationResponse } from '../types/university';

const API_BASE_URL = 'http://localhost:8002';

export class UniversityAPI {
  // 获取推荐大学列表
  static async getRecommendations(request: RecommendationRequest): Promise<RecommendationResponse> {
    try {
      const params = new URLSearchParams();
      params.append('major', request.major);
      
      if (request.province) {
        params.append('province', request.province);
      }
      
      if (request.score) {
        params.append('score', request.score.toString());
      }
      
      if (request.limit) {
        params.append('limit', request.limit.toString());
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/universities/recommend?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('获取推荐失败:', error);
      throw error;
    }
  }

  // 健康检查
  static async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('健康检查失败:', error);
      throw error;
    }
  }

  // 获取热门专业列表
  static async getPopularMajors(): Promise<string[]> {
    // 模拟热门专业数据，实际应该从API获取
    return [
      '人工智能',
      '计算机科学与技术',
      '软件工程',
      '数据科学',
      '电子信息工程',
      '自动化',
      '机械工程',
      '经济学',
      '金融学',
      '工商管理',
      '会计学',
      '法学',
      '临床医学',
      '口腔医学',
      '中医学'
    ];
  }

  // 获取省份列表
  static async getProvinces(): Promise<string[]> {
    // 模拟省份数据，实际应该从API获取
    return [
      '北京', '上海', '天津', '重庆', '江苏', '浙江', '广东', '山东',
      '湖北', '湖南', '河南', '四川', '陕西', '辽宁', '吉林', '黑龙江',
      '河北', '山西', '内蒙古', '安徽', '福建', '江西', '广西', '海南',
      '贵州', '云南', '西藏', '甘肃', '青海', '宁夏', '新疆'
    ];
  }
}