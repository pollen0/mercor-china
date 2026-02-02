/**
 * Pathway Design Tokens
 * Modern Design System for US College Career Platform
 *
 * Design Philosophy:
 * - Generous whitespace (breathing room = premium feel)
 * - Soft, muted color palette (not saturated/aggressive)
 * - Restrained accent color usage
 * - Subtle depth (soft shadows, not harsh)
 * - Clean typography hierarchy
 * - Smooth, understated animations
 */

// =============================================================================
// COLORS
// =============================================================================

export const colors = {
  // Brand - Soft Jade/Sage Green
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

  // Warm Grays (slightly warmer than pure gray)
  gray: {
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

  // Status Colors - Muted versions
  status: {
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

  // Backgrounds
  background: {
    base: '#FAFAFA',
    subtle: '#F5F5F4',
    elevated: '#FFFFFF',
    dark: {
      base: '#0F0F0F',
      subtle: '#1A1A1A',
      elevated: '#262626',
    },
  },

  // Text Colors
  text: {
    primary: '#1A1A1A',
    secondary: '#525252',
    muted: '#A3A3A3',
    dark: {
      primary: '#F5F5F5',
      secondary: '#A3A3A3',
      muted: '#737373',
    },
  },

  // Border Colors
  border: {
    DEFAULT: '#E5E5E5',
    subtle: '#F5F5F4',
    dark: {
      DEFAULT: '#2A2A2A',
      subtle: '#1A1A1A',
    },
  },
} as const

// =============================================================================
// TYPOGRAPHY
// =============================================================================

export const typography = {
  // Font Families - Chinese-optimized system fonts
  fontFamily: {
    sans: '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: '"SF Mono", "Noto Sans Mono CJK SC", Menlo, Monaco, "Courier New", monospace',
  },

  // Font Sizes with line heights optimized for Chinese text
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1.5' }],    // 12px
    sm: ['0.875rem', { lineHeight: '1.6' }],   // 14px
    base: ['1rem', { lineHeight: '1.75' }],    // 16px
    lg: ['1.125rem', { lineHeight: '1.75' }],  // 18px
    xl: ['1.25rem', { lineHeight: '1.75' }],   // 20px
    '2xl': ['1.5rem', { lineHeight: '1.5' }],  // 24px
    '3xl': ['1.875rem', { lineHeight: '1.4' }], // 30px
    '4xl': ['2.25rem', { lineHeight: '1.3' }], // 36px
    '5xl': ['3rem', { lineHeight: '1.2' }],    // 48px
    '6xl': ['3.75rem', { lineHeight: '1.1' }], // 60px
  },

  // Font Weights
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },

  // Letter Spacing (tighter for Chinese)
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
  },
} as const

// =============================================================================
// SPACING (8px grid system)
// =============================================================================

export const spacing = {
  0: '0',
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  28: '7rem',       // 112px
  32: '8rem',       // 128px
  36: '9rem',       // 144px
  40: '10rem',      // 160px
  44: '11rem',      // 176px
  48: '12rem',      // 192px
  52: '13rem',      // 208px
  56: '14rem',      // 224px
  60: '15rem',      // 240px
  64: '16rem',      // 256px
  72: '18rem',      // 288px
  80: '20rem',      // 320px
  96: '24rem',      // 384px
} as const

// =============================================================================
// SHADOWS (3-tier elevation system with soft shadows)
// =============================================================================

export const shadows = {
  none: 'none',

  // Subtle shadow for cards at rest
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 3px 0 rgba(0, 0, 0, 0.05)',

  // Default shadow
  DEFAULT: '0 2px 4px -1px rgba(0, 0, 0, 0.04), 0 4px 8px -1px rgba(0, 0, 0, 0.06)',

  // Medium elevation (hover states, dropdowns)
  md: '0 4px 8px -2px rgba(0, 0, 0, 0.05), 0 8px 16px -2px rgba(0, 0, 0, 0.08)',

  // Large elevation (modals, popovers)
  lg: '0 8px 16px -4px rgba(0, 0, 0, 0.06), 0 16px 32px -4px rgba(0, 0, 0, 0.1)',

  // Extra large (floating elements)
  xl: '0 12px 24px -6px rgba(0, 0, 0, 0.08), 0 24px 48px -6px rgba(0, 0, 0, 0.12)',

  // Brand shadow (for primary buttons)
  brand: '0 4px 12px -2px rgba(74, 157, 124, 0.25)',
  brandHover: '0 8px 20px -4px rgba(74, 157, 124, 0.35)',

  // Inner shadow
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.04)',
} as const

// =============================================================================
// BORDER RADIUS
// =============================================================================

export const borderRadius = {
  none: '0',
  sm: '0.25rem',    // 4px
  DEFAULT: '0.5rem', // 8px
  md: '0.625rem',   // 10px
  lg: '0.75rem',    // 12px
  xl: '1rem',       // 16px
  '2xl': '1.25rem', // 20px
  '3xl': '1.5rem',  // 24px
  full: '9999px',
} as const

// =============================================================================
// ANIMATIONS
// =============================================================================

export const animations = {
  // Durations
  duration: {
    fast: '150ms',
    DEFAULT: '200ms',
    slow: '300ms',
    slower: '500ms',
  },

  // Easing functions
  easing: {
    DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)',
    linear: 'linear',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  // Keyframes
  keyframes: {
    fadeIn: {
      from: { opacity: '0' },
      to: { opacity: '1' },
    },
    fadeOut: {
      from: { opacity: '1' },
      to: { opacity: '0' },
    },
    slideUp: {
      from: { transform: 'translateY(10px)', opacity: '0' },
      to: { transform: 'translateY(0)', opacity: '1' },
    },
    slideDown: {
      from: { transform: 'translateY(-10px)', opacity: '0' },
      to: { transform: 'translateY(0)', opacity: '1' },
    },
    slideLeft: {
      from: { transform: 'translateX(10px)', opacity: '0' },
      to: { transform: 'translateX(0)', opacity: '1' },
    },
    slideRight: {
      from: { transform: 'translateX(-10px)', opacity: '0' },
      to: { transform: 'translateX(0)', opacity: '1' },
    },
    scaleIn: {
      from: { transform: 'scale(0.95)', opacity: '0' },
      to: { transform: 'scale(1)', opacity: '1' },
    },
    pulse: {
      '0%, 100%': { opacity: '1' },
      '50%': { opacity: '0.5' },
    },
    shimmer: {
      '0%': { transform: 'translateX(-100%)' },
      '100%': { transform: 'translateX(100%)' },
    },
  },
} as const

// =============================================================================
// BREAKPOINTS
// =============================================================================

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const

// =============================================================================
// Z-INDEX SCALE
// =============================================================================

export const zIndex = {
  auto: 'auto',
  0: '0',
  10: '10',
  20: '20',
  30: '30',
  40: '40',
  50: '50',
  dropdown: '100',
  sticky: '200',
  fixed: '300',
  modalBackdrop: '400',
  modal: '500',
  popover: '600',
  tooltip: '700',
} as const

// =============================================================================
// EXPORTED DEFAULT THEME
// =============================================================================

export const theme = {
  colors,
  typography,
  spacing,
  shadows,
  borderRadius,
  animations,
  breakpoints,
  zIndex,
} as const

export type Theme = typeof theme
