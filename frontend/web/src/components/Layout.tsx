import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from './ThemeToggle';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { theme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const themeClasses = {
    light: {
      bg: 'bg-gray-50',
      navbar: 'bg-white shadow-sm',
      footer: 'bg-white border-t',
      text: 'text-gray-600',
      hover: 'hover:text-primary-600',
      mobileBg: 'bg-white',
    },
    dark: {
      bg: 'bg-gray-900',
      navbar: 'bg-gray-800 shadow-lg',
      footer: 'bg-gray-800 border-t border-gray-700',
      text: 'text-gray-300',
      hover: 'hover:text-primary-400',
      mobileBg: 'bg-gray-800',
    },
  };

  const t = themeClasses[theme];

  const navLinks = [
    { to: '/', label: '首页' },
    { to: '/chat', label: '智能助手' },
    { to: '/majors', label: '专业推荐' },
    { to: '/analytics', label: '数据分析' },
    { to: '/profile', label: '个人中心' },
  ];

  return (
    <div className={`min-h-screen ${t.bg} transition-colors duration-300`}>
      {/* 顶部导航 */}
      <nav className={`${t.navbar} transition-colors duration-300 sticky top-0 z-50`}>
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-14 sm:h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <span className="text-xl sm:text-2xl">🎯</span>
                <span className={`text-sm sm:text-xl font-bold ${theme === 'dark' ? 'text-primary-400' : 'text-primary-600'}`}>
                  专业指导
                </span>
              </Link>
            </div>

            {/* 桌面端导航 */}
            <div className="hidden md:flex items-center space-x-4 lg:space-x-8">
              {navLinks.map((link) => (
                <NavLink key={link.to} to={link.to} theme={theme} hover={t.hover}>
                  {link.label}
                </NavLink>
              ))}
              <ThemeToggle />
            </div>

            {/* 移动端菜单按钮 */}
            <div className="flex items-center md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <span className="text-2xl">{mobileMenuOpen ? '✕' : '☰'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* 移动端菜单 */}
        {mobileMenuOpen && (
          <div className={`md:hidden ${t.mobileBg} border-t ${theme === 'dark' ? 'border-gray-700' : 'border-gray-100'}`}>
            <div className="px-4 py-3 space-y-2">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block py-2 px-3 rounded-lg ${theme === 'dark' ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  {link.label}
                </Link>
              ))}
              <div className="pt-2 border-t dark:border-gray-700">
                <ThemeToggle />
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 py-4 sm:py-8">
        {children}
      </main>

      {/* 底部 */}
      <footer className={`${t.footer} transition-colors duration-300 mt-8 sm:mt-12`}>
        <div className="max-w-7xl mx-auto px-4 py-6 sm:py-8">
          <p className={`text-center text-xs sm:text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
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
    className={`${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'} ${hover} transition-colors text-sm lg:text-base font-medium`}
  >
    {children}
  </Link>
);

export default Layout;
