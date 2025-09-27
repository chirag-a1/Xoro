
import React, { useEffect, useRef, useState } from 'react';
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Box } from '@mui/material';
import api from './api';

type Quote = {
  symbol: string;
  price: number;
  change: number;
  updated: string; // ISO timestamp
  optimistic?: boolean;
};

function getRandomPrice(base: number) {
  return +(base + (Math.random() - 0.5) * 2).toFixed(2);
}

const useLiveQuotes = () => {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    async function fetchQuotes() {
      try {
        const res = await api.get('/market_data/demo-prices');
        if (res.data && res.data.success) {
          const data = res.data.data;
          setQuotes(Object.values(data).map((q: any) => ({
            symbol: q.symbol,
            price: q.price,
            change: q.change,
            updated: new Date(q.timestamp * 1000).toISOString(),
          })));
        }
      } catch (err) {
        // Optionally handle error
      }
    }
    fetchQuotes();
    timerRef.current = setInterval(fetchQuotes, 2000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);
  return quotes;
};

const LiveQuotes: React.FC = () => {
  const quotes = useLiveQuotes();
  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>Live Quotes</Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Change</TableCell>
              <TableCell align="right">Last Update</TableCell>
              <TableCell align="center">Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {quotes.map(q => (
              <TableRow key={q.symbol} hover>
                <TableCell>{q.symbol}</TableCell>
                <TableCell align="right">{q.price.toFixed(2)}</TableCell>
                <TableCell align="right" style={{ color: q.change > 0 ? 'green' : q.change < 0 ? 'red' : undefined }}>
                  {q.change > 0 ? '+' : ''}{q.change.toFixed(2)}
                </TableCell>
                <TableCell align="right">
                  <Box component="span" sx={{ fontSize: 12 }}>
                    {new Date(q.updated).toLocaleTimeString()}
                  </Box>
                </TableCell>
                <TableCell align="center">
                  {q.optimistic ? <Chip label="Optimistic" color="warning" size="small" /> : <Chip label="Live" color="success" size="small" />}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default LiveQuotes;