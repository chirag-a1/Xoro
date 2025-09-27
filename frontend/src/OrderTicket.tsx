import React, { useState } from 'react';
import api from './api';
import {
  Paper, Typography, TextField, MenuItem, Button, InputAdornment, Box, Alert
} from '@mui/material';
import { Stack } from '@mui/material';

const ORDER_TYPES = [
  { value: 'MARKET', label: 'Market' },
  { value: 'LIMIT', label: 'Limit' },
  { value: 'SL', label: 'Stop Loss' },
  { value: 'SL-M', label: 'Stop Loss Market' },
];

const TICK_SIZE = 0.05;
const FEE_RATE = 0.001;

function validateTickSize(price: number) {
  return Math.abs(price / TICK_SIZE - Math.round(price / TICK_SIZE)) < 1e-6;
}

const OrderTicket: React.FC<{ marketOpen?: boolean; setToast?: (t: any) => void }> = ({ marketOpen = true, setToast }) => {
  const [symbol, setSymbol] = useState('AAPL');
  const [orderType, setOrderType] = useState('MARKET');
  const [qty, setQty] = useState(1);
  const [price, setPrice] = useState(100);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [lastPayload, setLastPayload] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    // Idempotency: prevent duplicate submissions
    const payload = { symbol, orderType, qty, price: orderType === 'MARKET' ? undefined : price };
    if (JSON.stringify(payload) === JSON.stringify(lastPayload)) {
      setError('Duplicate submission detected.');
      return;
    }
    if ((orderType === 'LIMIT' || orderType === 'SL' || orderType === 'SL-M') && !validateTickSize(price)) {
      setError(`Price must be a multiple of tick size (${TICK_SIZE})`);
      return;
    }
    if (!marketOpen) {
      setError('Market is closed. Cannot submit orders.');
      setToast && setToast({ msg: 'Market is closed. Cannot submit orders.', type: 'warning' });
      return;
    }
    setSubmitting(true);
    setLastPayload(payload);
    // Real API call
    try {
      const endpoint = orderType === 'SELL' ? '/trading/sell' : '/trading/buy';
      const res = await api.post(endpoint, {
        symbol,
        quantity: qty,
        price: orderType === 'MARKET' ? undefined : price,
        order_type: orderType,
      });
      setSubmitting(false);
      if (res.data && res.data.success) {
        setSuccess('Order submitted successfully!');
        setToast && setToast({ msg: 'Order submitted successfully!', type: 'success' });
      } else {
        setError(res.data?.error || 'Order failed.');
        setToast && setToast({ msg: res.data?.error || 'Order failed.', type: 'error' });
      }
    } catch (err: any) {
      setSubmitting(false);
      setError(err?.response?.data?.error || err.message || 'Order failed.');
      setToast && setToast({ msg: err?.response?.data?.error || err.message || 'Order failed.', type: 'error' });
    }
  };

  const cost = (orderType === 'MARKET' ? 100 : price) * qty;
  const fee = cost * FEE_RATE;

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>Order Ticket</Typography>
      <Box component="form" onSubmit={handleSubmit}>
        <Stack spacing={2}>
          <TextField
            label="Symbol"
            value={symbol}
            onChange={e => setSymbol(e.target.value.toUpperCase())}
            fullWidth
            required
          />
          <TextField
            select
            label="Order Type"
            value={orderType}
            onChange={e => setOrderType(e.target.value)}
            fullWidth
          >
            {ORDER_TYPES.map(opt => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
          <TextField
            label="Quantity"
            type="number"
            value={qty}
            onChange={e => setQty(Math.max(1, Number(e.target.value)))}
            fullWidth
            required
            inputProps={{ min: 1 }}
          />
          {(orderType === 'LIMIT' || orderType === 'SL' || orderType === 'SL-M') && (
            <TextField
              label="Price"
              type="number"
              value={price}
              onChange={e => setPrice(Number(e.target.value))}
              fullWidth
              required
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              error={!validateTickSize(price)}
              helperText={!validateTickSize(price) ? `Must be multiple of ${TICK_SIZE}` : ''}
            />
          )}
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2">Cost: ${cost.toFixed(2)}</Typography>
            <Typography variant="body2">Fee: ${fee.toFixed(2)}</Typography>
          </Box>
          <Button type="submit" variant="contained" color="primary" disabled={submitting} fullWidth>
            {submitting ? 'Submitting...' : 'Submit Order'}
          </Button>
        </Stack>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
      </Box>
    </Paper>
  );
};

export default OrderTicket;