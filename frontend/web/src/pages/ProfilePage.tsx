import React from 'react';

const ProfilePage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">👤 个人中心</h1>

      <div className="grid md:grid-cols-3 gap-8">
        {/* 个人信息 */}
        <div className="card md:col-span-2">
          <h2 className="text-xl font-semibold mb-6">学生档案</h2>
          <div className="flex items-center space-x-6 mb-6">
            <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center text-3xl">
              👤
            </div>
            <div>
              <p className="font-medium text-lg">学生昵称</p>
              <p className="text-gray-500">student@example.com</p>
            </div>
          </div>

          <form className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">年级</label>
                <select className="input">
                  <option>高三</option>
                  <option>高二</option>
                  <option>高一</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">文理科</label>
                <select className="input">
                  <option>理科</option>
                  <option>文科</option>
                  <option>新高考选科</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">目标专业方向</label>
              <input type="text" className="input" placeholder="如：计算机科学、金融学、医学" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">优势学科</label>
              <input type="text" className="input" placeholder="数学、物理、英语" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">兴趣爱好</label>
              <input type="text" className="input" placeholder="编程、阅读、体育" />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">预估高考成绩</label>
                <input type="number" className="input" placeholder="500-650" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">目标城市</label>
                <input type="text" className="input" placeholder="北京、上海、杭州" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">专业选择困惑</label>
              <textarea
                className="input"
                rows={3}
                placeholder="描述您在专业选择上遇到的困惑..."
              />
            </div>

            <button type="submit" className="btn-primary">保存档案</button>
          </form>
        </div>

        {/* 侧边栏 */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold mb-4">📊 专业匹配指数</h3>
            <div className="text-center py-4">
              <div className="text-4xl font-bold text-primary-600">75</div>
              <p className="text-gray-500">综合评分</p>
            </div>
            <div className="space-y-2 mt-4">
              <ProgressBar label="专业了解度" value={60} />
              <ProgressBar label="兴趣匹配度" value={80} />
              <ProgressBar label="职业规划度" value={70} />
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold mb-4">📁 我的收藏专业</h3>
            <div className="space-y-3">
              <收藏Item title="计算机科学与技术" school="推荐院校：清华、北大" />
              <收藏Item title="人工智能" school="推荐院校：浙大、上交" />
              <收藏Item title="金融学" school="推荐院校：复旦、中财" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProgressBar: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div>
    <div className="flex justify-between text-sm mb-1">
      <span>{label}</span>
      <span>{value}%</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className="bg-primary-500 h-2 rounded-full"
        style={{ width: `${value}%` }}
      />
    </div>
  </div>
);

const 收藏Item: React.FC<{ title: string; school: string }> = ({ title, school }) => (
  <div className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
    <p className="font-medium text-sm">{title}</p>
    <p className="text-gray-500 text-xs">{school}</p>
  </div>
);

export default ProfilePage;
