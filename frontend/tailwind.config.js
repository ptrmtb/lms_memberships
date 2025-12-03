import frappeUIPreset from 'frappe-ui/tailwind'

export default {
  presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  safelist: [
    { pattern: /^grid-cols-/ },
  ],
  theme: {
    extend: {
      colors: {
        'brand-navy': '#1e3a5f',
        'brand-navy-light': '#2d4a6f',
        'brand-navy-dark': '#0f2847',
      },
    },
  },
  plugins: [],
}
