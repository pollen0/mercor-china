/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './app/(auth)/**/*.{js,ts,jsx,tsx,mdx}',
    './app/(candidate)/**/*.{js,ts,jsx,tsx,mdx}',
    './app/(employer)/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      // HEYTEA-Inspired Color Palette
      colors: {
        // CSS variable-based colors (for shadcn/ui compatibility)
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },

        // Brand Colors - Soft Jade (HEYTEA-inspired)
        brand: {
          50: '#E8F5EE',
          100: '#D1EBE0',
          200: '#A7D4C0',
          300: '#7DBDA0',
          400: '#5CB896',
          500: '#4A9D7C', // Primary
          600: '#3D8468',
          700: '#2F6B53',
          800: '#22523F',
          900: '#14392A',
        },

        // Jade alias for semantic usage
        jade: {
          50: '#E8F5EE',
          100: '#D1EBE0',
          200: '#A7D4C0',
          300: '#7DBDA0',
          400: '#5CB896',
          500: '#4A9D7C',
          600: '#3D8468',
          700: '#2F6B53',
          800: '#22523F',
          900: '#14392A',
        },

        // Warm grays
        warm: {
          50: '#FAFAFA',
          100: '#F5F5F4',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#1A1A1A',
        },

        // Status colors - muted versions
        success: {
          light: '#E8F5EE',
          DEFAULT: '#4A9D7C',
          dark: '#3D8468',
        },
        warning: {
          light: '#FEF3E2',
          DEFAULT: '#D4A574',
          dark: '#B8915E',
        },
        error: {
          light: '#FEE8E6',
          DEFAULT: '#D4746A',
          dark: '#B85F55',
        },
        info: {
          light: '#E8F1FB',
          DEFAULT: '#6B9BD2',
          dark: '#5A85B8',
        },
      },

      // Chinese-optimized font families
      fontFamily: {
        sans: [
          '"PingFang SC"',
          '"Microsoft YaHei"',
          '"Noto Sans SC"',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          '"SF Mono"',
          '"Noto Sans Mono CJK SC"',
          'Menlo',
          'Monaco',
          '"Courier New"',
          'monospace',
        ],
      },

      // Optimized font sizes with line heights for Chinese
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.5' }],
        sm: ['0.875rem', { lineHeight: '1.6' }],
        base: ['1rem', { lineHeight: '1.75' }],
        lg: ['1.125rem', { lineHeight: '1.75' }],
        xl: ['1.25rem', { lineHeight: '1.75' }],
        '2xl': ['1.5rem', { lineHeight: '1.5' }],
        '3xl': ['1.875rem', { lineHeight: '1.4' }],
        '4xl': ['2.25rem', { lineHeight: '1.3' }],
        '5xl': ['3rem', { lineHeight: '1.2' }],
        '6xl': ['3.75rem', { lineHeight: '1.1' }],
      },

      // Border radius scale
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
        xl: '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
      },

      // Soft shadows
      boxShadow: {
        'soft-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 3px 0 rgba(0, 0, 0, 0.05)',
        'soft': '0 2px 4px -1px rgba(0, 0, 0, 0.04), 0 4px 8px -1px rgba(0, 0, 0, 0.06)',
        'soft-md': '0 4px 8px -2px rgba(0, 0, 0, 0.05), 0 8px 16px -2px rgba(0, 0, 0, 0.08)',
        'soft-lg': '0 8px 16px -4px rgba(0, 0, 0, 0.06), 0 16px 32px -4px rgba(0, 0, 0, 0.1)',
        'soft-xl': '0 12px 24px -6px rgba(0, 0, 0, 0.08), 0 24px 48px -6px rgba(0, 0, 0, 0.12)',
        'brand': '0 4px 12px -2px rgba(74, 157, 124, 0.25)',
        'brand-lg': '0 8px 20px -4px rgba(74, 157, 124, 0.35)',
      },

      // Animation keyframes
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'fade-out': {
          from: { opacity: '1' },
          to: { opacity: '0' },
        },
        'slide-up': {
          from: { transform: 'translateY(10px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          from: { transform: 'translateY(-10px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          from: { transform: 'scale(0.95)', opacity: '0' },
          to: { transform: 'scale(1)', opacity: '1' },
        },
        'shimmer': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },

      // Animations
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
        'fade-out': 'fade-out 0.2s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
        'shimmer': 'shimmer 2s infinite',
      },

      // Transition timing
      transitionDuration: {
        DEFAULT: '200ms',
        fast: '150ms',
        slow: '300ms',
        slower: '500ms',
      },

      // Z-index scale
      zIndex: {
        dropdown: '100',
        sticky: '200',
        fixed: '300',
        'modal-backdrop': '400',
        modal: '500',
        popover: '600',
        tooltip: '700',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
