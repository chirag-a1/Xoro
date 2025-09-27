import React, { useState, useEffect } from 'react';
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Box, Stack } from '@mui/material';
import api from './api';

interface PortfolioHolding {
  symbol: string;
  qty: number;
  avgPrice: number;
  lastPrice: number;
  dayChange: number;
  totalChange: number;
  fees: number;
}

function mapBackendHoldings(holdings: any[]): PortfolioHolding[] {
  // Map backend holdings to frontend format
  return holdings.map(h => ({
    symbol: h.symbol,
    qty: h.quantity,
    avgPrice: h.averagePrice,
    lastPrice: h.currentPrice,
    dayChange: 0, // Placeholder, backend does not provide
    totalChange: 0, // Placeholder
    fees: 0 // Placeholder
  }));
}

function downloadCSV(data: any[]) {
  const header = Object.keys(data[0]).join(',');
  const rows = data.map(row => Object.values(row).join(','));
  const csv = [header, ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'portfolio.csv';
  a.click();
  URL.revokeObjectURL(url);
}

const PortfolioDashboard: React.FC = () => {
  const [holdings, setHoldings] = useState<PortfolioHolding[]>([]);
  const [balance, setBalance] = useState(0);
  const [totalValue, setTotalValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPortfolio() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get('/portfolio/');
        if (res.data && res.data.success) {
          const data = res.data.data;
          setHoldings(mapBackendHoldings(data.holdings));
          setBalance(data.balance);
          setTotalValue(data.total_value);
        } else {
          setError(res.data?.error || 'Failed to fetch portfolio');
        }
      } catch (err: any) {
        setError(err?.response?.data?.error || err.message || 'Failed to fetch portfolio');
      }
      setLoading(false);
    }
    fetchPortfolio();
  }, []);

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>Portfolio Dashboard</Typography>
      {error && <Typography color="error">{error}</Typography>}
      <Stack direction="row" spacing={4} sx={{ mb: 2 }}>
        <Box><Typography variant="body2">Cash Balance</Typography><Typography>${balance.toFixed(2)}</Typography></Box>
        <Box><Typography variant="body2">Total Value</Typography><Typography>${totalValue.toFixed(2)}</Typography></Box>
      </Stack>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell align="right">Qty</TableCell>
              <TableCell align="right">Avg Price</TableCell>
              <TableCell align="right">Last Price</TableCell>
              <TableCell align="right">Day Change</TableCell>
              <TableCell align="right">Total Change</TableCell>
              <TableCell align="right">Fees</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={7}>Loading...</TableCell></TableRow>
            ) : holdings.length === 0 ? (
              <TableRow><TableCell colSpan={7}>No holdings found.</TableCell></TableRow>
            ) : holdings.map(h => (
              <TableRow key={h.symbol}>
                <TableCell>{h.symbol}</TableCell>
                <TableCell align="right">{h.qty}</TableCell>
                <TableCell align="right">${h.avgPrice.toFixed(2)}</TableCell>
                <TableCell align="right">${h.lastPrice.toFixed(2)}</TableCell>
                <TableCell align="right" style={{ color: h.dayChange >= 0 ? 'green' : 'red' }}>{h.dayChange >= 0 ? '+' : ''}{h.dayChange}</TableCell>
                <TableCell align="right" style={{ color: h.totalChange >= 0 ? 'green' : 'red' }}>{h.totalChange >= 0 ? '+' : ''}{h.totalChange}</TableCell>
                <TableCell align="right">${h.fees.toFixed(2)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Button sx={{ mt: 2 }} variant="outlined" onClick={() => downloadCSV(holdings)}>
        Export CSV
      </Button>
    </Paper>
  );
};

export default PortfolioDashboard;