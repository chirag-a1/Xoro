

import React, { useState, useEffect, useMemo } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Container, Typography, BottomNavigation, BottomNavigationAction, Paper, Fab, Snackbar, Alert, Box, IconButton, useMediaQuery } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import SearchIcon from '@mui/icons-material/Search';
import CommandPalette from './CommandPalette';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import ListAltIcon from '@mui/icons-material/ListAlt';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import CandlestickChartIcon from '@mui/icons-material/CandlestickChart';
import FilterListIcon from '@mui/icons-material/FilterList';
import HistoryIcon from '@mui/icons-material/History';
import LiveQuotes from './LiveQuotes';
import OrderTicket from './OrderTicket';
import PortfolioDashboard from './PortfolioDashboard';
import Watchlists from './Watchlists';
import ChartView from './ChartView';
import StockScreener from './StockScreener';
import TradeHistory from './TradeHistory';
import AIRecommendations from './AIRecommendations';
import './App.css';


const getTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#9c27b0',
    },
    background: {
      default: mode === 'dark' ? '#181818' : '#fafafa',
      paper: mode === 'dark' ? '#232323' : '#fff',
    },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: { styleOverrides: { root: { minHeight: 48, fontSize: 16 } } },
    MuiBottomNavigationAction: { styleOverrides: { root: { minWidth: 0, padding: '8px 0', fontSize: 14 } } },
  },
});

function App() {
  // Global status state
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' | 'info' | 'warning' } | null>(null);
  const [socketStatus, setSocketStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('connected');
  const [marketOpen, setMarketOpen] = useState(true); // Simulate market open/close
  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly toggle socket status and market open/close
      if (Math.random() < 0.1) setSocketStatus(s => s === 'connected' ? 'reconnecting' : 'connected');
      if (Math.random() < 0.05) setMarketOpen(m => !m);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const [paletteOpen, setPaletteOpen] = useState(false);
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const [nav, setNav] = useState(0);
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState<'light' | 'dark'>(prefersDark ? 'dark' : 'light');
  const theme = useMemo(() => getTheme(mode), [mode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Socket status banner */}
      <Box sx={{ width: '100%', position: 'fixed', top: 0, left: 0, zIndex: 1300 }}>
        {socketStatus !== 'connected' && (
          <Alert severity={socketStatus === 'reconnecting' ? 'warning' : 'error'} sx={{ borderRadius: 0, justifyContent: 'center' }}>
            {socketStatus === 'reconnecting' ? 'Reconnecting to live quotes...' : 'Disconnected from server'}
          </Alert>
        )}
        {!marketOpen && (
          <Alert severity="info" sx={{ borderRadius: 0, justifyContent: 'center' }}>
            Market is currently closed. Trading is disabled.
          </Alert>
        )}
      </Box>
      <Container
        maxWidth="md"
        sx={{
          py: { xs: 1, sm: 4 },
          minHeight: { xs: 'calc(100vh - 120px)', sm: '80vh' },
          mt: socketStatus !== 'connected' || !marketOpen ? 8 : 0,
          px: { xs: 0.5, sm: 2 },
        }}
        tabIndex={0}
        aria-label="Main content"
      >
        <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
        <Fab color="primary" aria-label="search" sx={{ position: 'fixed', bottom: 80, right: 24, zIndex: 1200 }} onClick={() => setPaletteOpen(true)}>
          <SearchIcon />
        </Fab>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ flex: 1 }}>
            Paper Trading App
          </Typography>
          <IconButton aria-label="Toggle theme" onClick={() => setMode(m => (m === 'light' ? 'dark' : 'light'))} size="large">
            {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Box>
  {nav === 0 && <LiveQuotes />}
  {nav === 1 && <PortfolioDashboard />}
  {nav === 2 && <OrderTicket marketOpen={marketOpen} setToast={setToast} />}
  {nav === 3 && <Watchlists setToast={setToast} />}
  {nav === 4 && <ChartView />}
  {nav === 5 && <StockScreener setToast={setToast} />}
  {nav === 6 && <TradeHistory />}
  {nav === 7 && <AIRecommendations />}
      {/* Global Toasts */}
      <Snackbar open={!!toast} autoHideDuration={4000} onClose={() => setToast(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
  {toast ? <Alert onClose={() => setToast(null)} severity={toast.type} sx={{ width: '100%' }}>{toast.msg}</Alert> : undefined}
      </Snackbar>
  {/* nav === 1: Portfolio, nav === 2: Orders, nav === 3: Watchlists, nav === 4: Charts, etc. */}
      </Container>
      <Paper
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1201,
          borderTopLeftRadius: 16,
          borderTopRightRadius: 16,
          boxShadow: 4,
        }}
        elevation={3}
        role="navigation"
        aria-label="Bottom navigation"
      >
        <BottomNavigation
          showLabels
          value={nav}
          onChange={(_, newValue) => setNav(newValue)}
          sx={{
            height: { xs: 64, sm: 56 },
            '.Mui-selected': { fontWeight: 700 },
          }}
        >
          <BottomNavigationAction label="Quotes" icon={<ShowChartIcon fontSize="medium" />} />
          <BottomNavigationAction label="Portfolio" icon={<AccountBalanceWalletIcon fontSize="medium" />} />
          <BottomNavigationAction label="Orders" icon={<ListAltIcon fontSize="medium" />} />
          <BottomNavigationAction label="Watchlists" icon={<PlaylistAddCheckIcon fontSize="medium" />} />
          <BottomNavigationAction label="Charts" icon={<CandlestickChartIcon fontSize="medium" />} />
          <BottomNavigationAction label="Screener" icon={<FilterListIcon fontSize="medium" />} />
          <BottomNavigationAction label="History" icon={<HistoryIcon fontSize="medium" />} />
          <BottomNavigationAction label="AI" icon={<FilterListIcon fontSize="medium" />} />
        </BottomNavigation>
      </Paper>
      {/* Pull-to-refresh for mobile */}
      <script>
        {`
          if ('ontouchstart' in window) {
            let startY = 0;
            let refreshing = false;
            window.addEventListener('touchstart', e => { if (e.touches[0].clientY < 80) startY = e.touches[0].clientY; });
            window.addEventListener('touchmove', e => {
              if (startY && e.touches[0].clientY - startY > 120 && !refreshing) {
                refreshing = true;
                window.location.reload();
              }
            });
            window.addEventListener('touchend', () => { startY = 0; refreshing = false; });
          }
        `}
      </script>
    </ThemeProvider>
  );
}

export default App;
