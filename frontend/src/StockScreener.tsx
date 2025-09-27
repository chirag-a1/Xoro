import React, { useState } from 'react';
import { Paper, Typography, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Box, Chip, TextField } from '@mui/material';

const MOCK_STOCKS = [
  { symbol: 'AAPL', price: 155, change: 2.1, volume: 1000000, mcap: 2_000_000_000_000 },
  { symbol: 'GOOG', price: 1190, change: -1.5, volume: 800000, mcap: 1_800_000_000_000 },
  { symbol: 'TSLA', price: 700, change: 5.2, volume: 2000000, mcap: 900_000_000_000 },
  { symbol: 'MSFT', price: 300, change: 0.5, volume: 1200000, mcap: 2_100_000_000_000 },
  { symbol: 'AMZN', price: 3300, change: -3.2, volume: 950000, mcap: 1_600_000_000_000 },
];

const SCREENS = [
  { label: 'Gainers', filter: (s: any) => s.change > 0 },
  { label: 'Losers', filter: (s: any) => s.change < 0 },
  { label: 'Volume', filter: (s: any) => s.volume > 1000000 },
  { label: 'Mcap', filter: (s: any) => s.mcap > 1_500_000_000_000 },
];

const StockScreener: React.FC<{ setToast?: (t: any) => void }> = ({ setToast }) => {
  const [tab, setTab] = useState(0);
  const [saved, setSaved] = useState<{ label: string; filter: (s: any) => boolean }[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [custom, setCustom] = useState('');

  const handleSave = () => {
    if (custom.trim()) {
      setSaved([...saved, { label: custom, filter: (s: any) => s.symbol.includes(custom.toUpperCase()) }]);
      setCustom('');
    }
  };

  const handleAddToWatchlist = (symbol: string) => {
    if (!watchlist.includes(symbol)) {
      setWatchlist([...watchlist, symbol]);
      setToast && setToast({ msg: `${symbol} added to quick watchlist!`, type: 'success' });
    }
  };

  const screens = [...SCREENS, ...saved];
  const filtered = MOCK_STOCKS.filter(screens[tab].filter);

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>Stock Screener</Typography>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        {screens.map((s, i) => (
          <Tab key={s.label} label={s.label} />
        ))}
      </Tabs>
      <Box sx={{ mb: 2 }}>
        <TextField label="Save Custom Screen (by symbol)" value={custom} onChange={e => setCustom(e.target.value)} size="small" sx={{ mr: 1 }} />
        <Button onClick={handleSave} variant="outlined">Save</Button>
      </Box>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Change</TableCell>
              <TableCell align="right">Volume</TableCell>
              <TableCell align="right">Mcap</TableCell>
              <TableCell align="center">Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.map(s => (
              <TableRow key={s.symbol}>
                <TableCell>{s.symbol}</TableCell>
                <TableCell align="right">${s.price.toFixed(2)}</TableCell>
                <TableCell align="right" style={{ color: s.change > 0 ? 'green' : 'red' }}>{s.change > 0 ? '+' : ''}{s.change.toFixed(2)}</TableCell>
                <TableCell align="right">{s.volume.toLocaleString()}</TableCell>
                <TableCell align="right">${(s.mcap / 1e9).toFixed(1)}B</TableCell>
                <TableCell align="center">
                  <Button size="small" variant="contained" onClick={() => handleAddToWatchlist(s.symbol)} disabled={watchlist.includes(s.symbol)}>
                    {watchlist.includes(s.symbol) ? 'Added' : 'Add to Watchlist'}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2">Quick Watchlist: {watchlist.join(', ') || 'None'}</Typography>
      </Box>
    </Paper>
  );
};

export default StockScreener;