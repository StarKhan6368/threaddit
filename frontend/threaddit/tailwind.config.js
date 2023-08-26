/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "theme-orange": "#FF4500",
        "theme-gray-blue": "#EAF0F4",
        "theme-red-coral": "#ff4631",
        "theme-cultured": "#f4f7fa",
      },
    },
  },
  future: {
    hoverOnlyWhenSupported: true,
  },
  plugins: [],
};
