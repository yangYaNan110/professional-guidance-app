import React from 'react';
import Taro, { Component, Config } from '@tarojs/taro';
import HomePage from './pages/home';
import ChatPage from './pages/chat';
import MajorsPage from './pages/majors';

class App extends Component {
  config: Config = {
    pages: [
      'pages/home/index',
      'pages/chat/index',
      'pages/majors/index'
    ],
    window: {
      backgroundTextStyle: 'light',
      navigationBarBackgroundColor: '#fff',
      navigationBarTitleText: '专业选择指导',
      navigationBarTextStyle: 'black'
    },
    tabBar: {
      color: '#999999',
      selectedColor: '#0ea5e9',
      backgroundColor: '#ffffff',
      borderStyle: 'black',
      list: [
        {
          pagePath: 'pages/home/index',
          text: '首页',
          iconPath: './assets/home.png',
          selectedIconPath: './assets/home-active.png'
        },
        {
          pagePath: 'pages/chat/index',
          text: '助手',
          iconPath: './assets/chat.png',
          selectedIconPath: './assets/chat-active.png'
        },
        {
          pagePath: 'pages/majors/index',
          text: '专业',
          iconPath: './assets/major.png',
          selectedIconPath: './assets/major-active.png'
        }
      ]
    }
  };

  render() {
    return (
      <HomePage />
    );
  }
}

export default App;
