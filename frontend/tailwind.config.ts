import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#1c1917',
          light: '#292524',
        },
        gold: {
          DEFAULT: '#b45309',
          light: '#d97706',
          pale: '#fef3c7',
        },
      },
    },
  },
  plugins: [],
}

export default config
