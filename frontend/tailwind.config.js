/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        studio: {
          bg: "#060911",
          card: "rgba(13, 19, 33, 0.75)",
        }
      }
    },
  },
  plugins: [],
}
