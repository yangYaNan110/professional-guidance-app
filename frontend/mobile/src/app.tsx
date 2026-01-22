import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux-redux';
import Taro from '@tarojs/taro';
import './app.scss';

const store = {
  getState: () => ({}),
  subscribe: () => {},
  dispatch: () => {}
};

Taro.addResourceLoader({
  loader: () => Promise.resolve(),
  loaded: () => {}
});

const App: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Provider store={store as any}>
      {children}
    </Provider>
  );
};

const root = ReactDOM.createRoot(
  document.getElementById('app') as HTMLElement
);

root.render(
  <App>
    <HomePage />
  </App>
);

export default App;
