import React from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from './ThemeToggle';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { theme } = useTheme();

  const themeClasses = {
    light: {
      bg: 'bg-gray-50',
      navbar: 'bg-white shadow-sm',
      footer: 'bg-white border-t',
      text: 'text-gray-600',
      hover: 'hover:text-primary-600',
    },
    dark: {
      bg: 'bg-gray-900',
      navbar: 'bg-gray-800 shadow-lg',
      footer: 'bg-gray-800 border-t border-gray-700',
      text: 'text-gray-300',
      hover: 'hover:text-primary-400',
    },
  };

  const t = themeClasses[theme];

  return (
    <div className={`min-h-screen ${t.bg} transition-colors duration-300`}>
      {/* 顶部导航 */}
      <nav className={`${t.navbar} transition-colors duration-300`}>
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <span className="text-2xl">🎯</span>
                <span className={`text-xl font-bold ${theme === 'dark' ? 'text-primary-400' : 'text-primary-600'}`}>
                  专业指导
                </span>
              </Link>
            </div>
            <div className="flex items-center space-x-8">
              <NavLink to="/" theme={theme} hover={t.hover}>
                首页
              </NavLink>
              <NavLink to="/chat" theme={theme} hover={t.hover}>
                智能助手
              </NavLink>
              <NavLink to="/majors" theme={theme} hover={t.hover}>
                专业推荐
              </NavLink>
              <NavLink to="/analytics" theme={theme} hover={t.hover}>
                数据分析
              </NavLink>
              <NavLink to="/profile" theme={theme} hover={t.hover}>
                个人中心
              </NavLink>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>

      {/* 底部 */}
      <footer className={`${t.footer} transition-colors duration-300 mt-12`}>
        <div className="max-w-7xl mx-auto px-4 py-8">
            <p className={`text-center ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
              © 2024 专业选择指导应用 - 您的专业发展助手
            </p>
        </div>
      </footer>
    </div>
  );
};

interface NavLinkProps {
  to: string;
  children: React.ReactNode;
  theme: 'light' | 'dark';
  hover: string;
}

const NavLink: React.FC<NavLinkProps> = ({ to, children, theme, hover }) => (
  <Link
    to={to}
    className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'} ${hover} transition-colors font-medium`}
  >
    {children}
  </Link>
);

export default Layout;
