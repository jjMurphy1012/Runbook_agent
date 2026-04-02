/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#102033",
        mist: "#edf2f7",
        signal: "#ff6b35",
        trace: "#2a9d8f"
      }
    }
  },
  plugins: []
};
