import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const AnalyticsPage: React.FC = () => {
  const salaryTrendData = {
    labels: ['2020', '2021', '2022', '2023', '2024', '2025'],
    datasets: [
      {
        label: '计算机类专业',
        data: [12000, 14000, 16000, 18000, 20000, 22000],
        borderColor: '#0ea5e9',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
      },
      {
        label: '人工智能专业',
        data: [15000, 18000, 21000, 24000, 28000, 32000],
        borderColor: '#d946ef',
        backgroundColor: 'rgba(217, 70, 239, 0.1)',
      }
    ]
  };

  const majorData = {
    labels: ['工学', '理学', '经济学', '管理学', '文学', '医学'],
    datasets: [{
      data: [30, 20, 15, 15, 10, 10],
      backgroundColor: [
        '#0ea5e9',
        '#d946ef',
        '#10b981',
        '#f59e0b',
        '#6b7280',
        '#ef4444'
      ]
    }]
  };

  const employmentRateData = {
    labels: ['计算机', '金融', '医学', '教育', '法律', '艺术'],
    datasets: [{
      label: '就业率',
      data: [95, 90, 98, 92, 88, 85],
      backgroundColor: '#0ea5e9'
    }]
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">📊 数据分析</h1>

      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* 薪资趋势 */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">💰 薪资趋势</h2>
          <Line
            data={salaryTrendData}
            options={{
              responsive: true,
              plugins: {
                legend: { position: 'top' as const }
              }
            }}
          />
        </div>

        {/* 专业分布 */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">🎓 专业门类分布</h2>
          <div className="flex justify-center">
            <div className="w-64">
              <Doughnut
                data={majorData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: { position: 'bottom' as const }
                  }
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">🔥 各专业就业率</h2>
        <Bar
          data={employmentRateData}
          options={{
            responsive: true,
            plugins: {
              legend: { display: false }
            }
          }}
        />
      </div>

      {/* 洞察建议 */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">💡 AI洞察</h2>
        <div className="space-y-4">
          <InsightCard
            type="趋势"
            title="AI相关专业持续热门"
            description="人工智能领域的薪资增长率达到15%，建议关注AI相关专业"
          />
          <InsightCard
            type="建议"
            title="计算机类专业就业前景好"
            description="计算机类专业就业率和薪资水平都处于高位，值得考虑"
          />
          <InsightCard
            type="机会"
            title="新兴专业机会增加"
            description="数据科学、大数据等专业是新兴热点，就业前景广阔"
          />
        </div>
      </div>
    </div>
  );
};

const InsightCard: React.FC<{ type: string; title: string; description: string }> = ({
  type,
  title,
  description
}) => (
  <div className="flex items-start space-x-4 p-4 bg-primary-50 rounded-lg">
    <span className={`px-2 py-1 rounded text-sm font-medium ${
      type === '趋势' ? 'bg-blue-100 text-blue-700' :
      type === '建议' ? 'bg-green-100 text-green-700' :
      'bg-yellow-100 text-yellow-700'
    }`}>
      {type}
    </span>
    <div>
      <h4 className="font-medium">{title}</h4>
      <p className="text-gray-600 text-sm mt-1">{description}</p>
    </div>
  </div>
);

export default AnalyticsPage;
