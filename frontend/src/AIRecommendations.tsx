import React, { useState } from 'react';
import { Paper, Typography, Button, TextField, CircularProgress, Alert, Box } from '@mui/material';
import api from './api';

const TYPES = [
  { value: 'general', label: 'General' },
  { value: 'buy', label: 'Buy Ideas' },
  { value: 'sell', label: 'Sell Ideas' },
  { value: 'portfolio', label: 'Portfolio Review' },
];

const AIRecommendations: React.FC = () => {
  const [type, setType] = useState('general');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.post('/ai/recommendations', { type, input });
      if (res.data && res.data.success) {
        setResult(res.data.recommendations);
      } else {
        setError(res.data?.error || 'Failed to get recommendations');
      }
    } catch (err: any) {
      setError(err?.response?.data?.error || err.message || 'Failed to get recommendations');
    }
    setLoading(false);
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>AI Recommendations</Typography>
      <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
        <TextField
          select
          label="Type"
          value={type}
          onChange={e => setType(e.target.value)}
          sx={{ mr: 2, minWidth: 160 }}
        >
          {TYPES.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </TextField>
        <TextField
          label="Custom Input (optional)"
          value={input}
          onChange={e => setInput(e.target.value)}
          sx={{ mr: 2, minWidth: 240 }}
        />
        <Button type="submit" variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Get Recommendations'}
        </Button>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      {result && <Alert severity="success" sx={{ whiteSpace: 'pre-line' }}>{result}</Alert>}
    </Paper>
  );
};

export default AIRecommendations;
