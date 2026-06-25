/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'media',
  theme: {
    extend: {
      colors: {
        lavender: {
          50: '#F3EEFF',
          100: '#E8DDFF',
          200: '#D1BBFF',
          300: '#B999FF',
          400: '#A177FF',
          500: '#7C5CFC',
          600: '#6344E0',
          700: '#4A2DC4',
          800: '#3520A0',
          900: '#241880',
        },
        warm: {
          50: '#FFFBF5',
          100: '#FFF8F0',
          200: '#FFF1E0',
          300: '#FFE8CC',
          400: '#FFD9A8',
          500: '#FFC87A',
        },
        sky: {
          50: '#F0F9FF',
          100: '#E8F4FD',
          200: '#C9E8FB',
          300: '#A0D8F8',
          400: '#6CC2F2',
          500: '#38A8E8',
        },
      },
      borderRadius: {
        xl: '16px',
        '2xl': '20px',
        '3xl': '24px',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          '"PingFang SC"',
          '"Hiragino Sans GB"',
          '"Microsoft YaHei"',
          'sans-serif',
        ],
      },
      fontSize: {
        base: ['16px', '1.6'],
      },
    },
  },
  plugins: [],
}
