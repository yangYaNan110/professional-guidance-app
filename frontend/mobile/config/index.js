const config = {
  projectName: 'major-guidance-mobile',
  date: '2026-01-22',
  designWidth: 375,
  deviceRatio: {
    640: 2.34 / 2,
    750: 1,
    828: 1.81 / 2,
    375: 2 / 1
  },
  sourceRoot: 'src',
  outputRoot: 'dist',
  plugins: [],
  define: {
    'process.env.TARO_ENV': JSON.stringify(process.env.TARO_ENV || 'h5')
  },
  compiler: {
    type: 'webpack5',
    precompile: false
  },
  cache: {
    enable: false
  },
  framework: 'react',
  mini: {
    postcss: {
      pxtransform: {
        enable: true,
        config: {}
      },
      url: {
        enable: true,
        config: {
          limit: 10240
        }
      }
    }
  },
  h5: {
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
        config: {
          browsers: ['last 3 versions', 'Android >= 4.0', 'iOS >= 8']
        }
      }
    },
    devServer: {
      port: 3000,
      host: '0.0.0.0'
    }
  },
  rn: {
    appJson: {
      name: '专业选择指导',
      icon: './src/assets/icon.png',
      package: 'com.major.guidance'
    }
  }
};

module.exports = config;
