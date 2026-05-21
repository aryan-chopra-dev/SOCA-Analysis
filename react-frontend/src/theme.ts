import { createTheme } from '@mui/material/styles';
import type { ThemeOptions } from '@mui/material/styles';

const themeOptions: ThemeOptions = {
  palette: {
    mode: 'dark',
    primary: {
      main: '#8b5cf6', // Vibrant Violet
      light: '#a78bfa',
      dark: '#6d28d9',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#ec4899', // Hot Pink
      light: '#f472b6',
      dark: '#be185d',
      contrastText: '#ffffff',
    },
    warning: {
      main: '#f59e0b', // Amber/Gold
      light: '#fbbf24',
      dark: '#b45309',
    },
    success: {
      main: '#10b981', // Emerald
      light: '#34d399',
      dark: '#047857',
    },
    background: {
      default: '#0b0c10', // Deep Space Background
      paper: '#12131a', // Dark Glassmorphism Base
    },
    text: {
      primary: '#f3f4f6',
      secondary: '#9ca3af',
    },
  },
  typography: {
    fontFamily: '"Outfit", "Inter", "Segoe UI", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 800,
      letterSpacing: '-0.03em',
      lineHeight: 1.2,
      background: 'linear-gradient(135deg, #ffffff 30%, #a78bfa 90%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h2: {
      fontSize: '1.875rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: '0.01em',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '50px',
          padding: '10px 28px',
          fontSize: '0.975rem',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 4px 12px rgba(139, 92, 246, 0.15)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 24px rgba(139, 92, 246, 0.3)',
          },
        },
      },
    },

    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '24px',
          backgroundColor: '#12131a',
          backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0))',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(20px)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          height: 12,
          borderRadius: 6,
        },
        rail: {
          opacity: 0.15,
          backgroundColor: '#ffffff',
        },
        track: {
          border: 'none',
          background: 'linear-gradient(90deg, #8b5cf6, #ec4899)',
        },
        thumb: {
          height: 24,
          width: 24,
          backgroundColor: '#ffffff',
          border: '4px solid #8b5cf6',
          boxShadow: '0 0 12px rgba(139, 92, 246, 0.5)',
          '&:focus, &:hover, &.Mui-active, &.Mui-focusVisible': {
            boxShadow: '0 0 0 8px rgba(139, 92, 246, 0.16)',
          },
        },
      },
    },
  },
};

const theme = createTheme(themeOptions);

export default theme;
