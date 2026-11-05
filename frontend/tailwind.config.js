/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        chess: {
          dark: '#1e293b',
          light: '#f8fafc',
          boardDark: '#769656',
          boardLight: '#eeeed2',
          accent: '#3b82f6',
          blunder: '#ef4444',
          mistake: '#f97316',
          inaccuracy: '#eab308',
          good: '#22c55e',
          best: '#10b981',
          brilliant: '#06b6d4',
        }
      }
    },
  },
  plugins: [],
}

