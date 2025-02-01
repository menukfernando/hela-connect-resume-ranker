module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}', // ✅ Ensures Tailwind scans all React components
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
