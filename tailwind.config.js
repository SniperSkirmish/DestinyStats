/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/src/**/*.js"
  ],
  theme: {
    extend: 
    {
      colors: 
      {
        'bigStone': '#1A2D45',
        'blueBayoux': '#546981',
        'halfBaked': '#83b1cf',
        'hippyBlue': '#5791b3',
        'ziggurat': '#b5d1e2',
        'congressBlue': '#043e7d',
      },
      fontFamily: {
        'Cairo': ['Cairo'],
      },
    },
  },
  plugins: [],
}