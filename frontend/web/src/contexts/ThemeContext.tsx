import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    // 优先读取本地存储
    const saved = localStorage.getItem('theme') as Theme;
    if (saved) return saved;
    // 其次检测系统偏好
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    // 应用主题到html元素
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);
    // 设置主题色
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// 主题样式常量
export const themeStyles = {
  light: {
    bg: 'bg-gray-50',
    bgCard: 'bg-white',
    text: 'text-gray-900',
    textSecondary: 'text-gray-600',
    border: 'border-gray-200',
    primary: 'bg-primary-500',
    hover: 'hover:bg-primary-600',
    navbar: 'bg-white',
    footer: 'bg-gray-100',
    input: 'bg-white border-gray-300',
    shadow: 'shadow-sm',
  },
  dark: {
    bg: 'bg-gray-900',
    bgCard: 'bg-gray-800',
    text: 'text-gray-100',
    textSecondary: 'text-gray-400',
    border: 'border-gray-700',
    primary: 'bg-primary-600',
    hover: 'hover:bg-primary-500',
    navbar: 'bg-gray-800',
    footer: 'bg-gray-900',
    input: 'bg-gray-700 border-gray-600',
    shadow: 'shadow-lg',
  },
};
