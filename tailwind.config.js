/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "eshop/templates/**/*.html",
  ],
  theme: {
    screens: {
      sm: "640px",
      md: "768px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1536px",
    },
    fontFamily: {
      display: ["Source Serif Pro", "Georgia", "serif"],
      body: ["Synonym", "system-ui", "sans-serif"],
      mono: ["JetBrains Mono", "monospace"], // Adding JetBrains Mono for monospaced text
      sans: ['Inter', 'system-ui', 'sans-serif']
    },
    extend: {
      colors: {
        'orange': {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      fontSize: {
        h1: "36", // Adjust as needed
        h2: "2rem", // Adjust as needed
        h3: "1.75rem", // Adjust as needed
        h4: "1.5rem", // Adjust as needed
        h5: "1.25rem", // Adjust as needed
        h6: "1rem", // Adjust as needed
      },
      fontWeight: {
        h1: "700", // Adjust as needed
        h2: "600", // Adjust as needed
        h3: "500", // Adjust as needed
        h4: "400", // Adjust as needed
        h5: "300", // Adjust as needed
        h6: "200", // Adjust as needed
      },
      zIndex: {
        41: "41",
        45: "45",
        51: "51",
        55: "55",
        60: "60",
        65: "65",
        70: "70",
        75: "75",
        80: "80",
        85: "85",
        90: "90",
        95: "95",
        100: "100",
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [],
};
