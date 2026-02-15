import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "medical-blue": "#0066CC",
        "medical-green": "#00AA44",
        "medical-red": "#CC0000",
        "medical-orange": "#FF6600",
      },
      animation: {
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "token-flow": "token-flow 2s ease-in-out infinite",
      },
      keyframes: {
        "token-flow": {
          "0%, 100%": { opacity: "0", transform: "translateX(-10px)" },
          "50%": { opacity: "1", transform: "translateX(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
