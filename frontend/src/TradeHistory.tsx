import React from 'react';
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Box, Chip } from '@mui/material';
import Grid from '@mui/material/Grid';

const MOCK_TRADES = [
  { id: 1, symbol: 'AAPL', side: 'BUY', qty: 10, price: 150, pnl: 20, date: '2023-09-01' },
  { id: 2, symbol: 'GOOG', side: 'SELL', qty: 5, price: 1200, pnl: -15, date: '2023-09-02' },
  { id: 3, symbol: 'TSLA', side: 'BUY', qty: 2, price: 700, pnl: 10, date: '2023-09-03' },
  { id: 4, symbol: 'AAPL', side: 'SELL', qty: 5, price: 155, pnl: 5, date: '2023-09-04' },
];

const winRate = () => {
  const wins = MOCK_TRADES.filter(t => t.pnl > 0).length;
  return (wins / MOCK_TRADES.length * 100).toFixed(1);
};
const avgReturn = () => {
  return (MOCK_TRADES.reduce((a, t) => a + t.pnl, 0) / MOCK_TRADES.length).toFixed(2);
};
const maxDrawdown = () => {
  let max = 0, sum = 0, peak = 0;
  for (const t of MOCK_TRADES) {
    sum += t.pnl;
    if (sum > peak) peak = sum;
    if (peak - sum > max) max = peak - sum;
  }
  return max.toFixed(2);
};
const streaks = () => {
  let maxWin = 0, maxLoss = 0, curWin = 0, curLoss = 0;
  for (const t of MOCK_TRADES) {
    if (t.pnl > 0) { curWin++; curLoss = 0; } else if (t.pnl < 0) { curLoss++; curWin = 0; }
    if (curWin > maxWin) maxWin = curWin;
    if (curLoss > maxLoss) maxLoss = curLoss;
  }
  return { maxWin, maxLoss };
};

const TradeHistory: React.FC = () => {
  const streak = streaks();
  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>Trade History & Analytics</Typography>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={6} sm={3}><Box><Typography variant="body2">Win Rate</Typography><Typography color="success.main">{winRate()}%</Typography></Box></Grid>
        <Grid item xs={6} sm={3}><Box><Typography variant="body2">Avg Return</Typography><Typography color="info.main">{avgReturn()}</Typography></Box></Grid>
        <Grid item xs={6} sm={3}><Box><Typography variant="body2">Max Drawdown</Typography><Typography color="error.main">{maxDrawdown()}</Typography></Box></Grid>
        <Grid item xs={6} sm={3}><Box><Typography variant="body2">Win Streak</Typography><Typography color="success.main">{streak.maxWin}</Typography></Box></Grid>
        <Grid item xs={6} sm={3}><Box><Typography variant="body2">Loss Streak</Typography><Typography color="error.main">{streak.maxLoss}</Typography></Box></Grid>
        <Grid item xs={6} sm={3}><Box><Typography variant="body2">Benchmarks</Typography><Chip label="NIFTY 50" color="primary" size="small" sx={{ mr: 1 }} /><Chip label="S&P 500" color="secondary" size="small" /></Box></Grid>
      </Grid>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Side</TableCell>
              <TableCell align="right">Qty</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">P&L</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {MOCK_TRADES.map(t => (
              <TableRow key={t.id}>
                <TableCell>{t.date}</TableCell>
                <TableCell>{t.symbol}</TableCell>
                <TableCell>{t.side}</TableCell>
                <TableCell align="right">{t.qty}</TableCell>
                <TableCell align="right">${t.price.toFixed(2)}</TableCell>
                <TableCell align="right" style={{ color: t.pnl > 0 ? 'green' : t.pnl < 0 ? 'red' : undefined }}>{t.pnl > 0 ? '+' : ''}{t.pnl}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default TradeHistory;