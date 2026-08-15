export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        tblack: '#000000',
        tcard: '#121212',
        tinput: '#1e1e1e',
        tpink: '#FE2C55',
        tcyan: '#25F4EE'
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      borderRadius: { box: '12px' }
    }
  },
  plugins: []
}
