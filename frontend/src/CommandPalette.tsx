import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, TextField, List, ListItem, ListItemText, Typography, Box } from '@mui/material';

const MOCK_COMMANDS = [
  { label: 'Go to Quotes', action: 'quotes' },
  { label: 'Go to Portfolio', action: 'portfolio' },
  { label: 'Go to Orders', action: 'orders' },
  { label: 'Go to Watchlists', action: 'watchlists' },
  { label: 'Go to Charts', action: 'charts' },
  { label: 'New Order', action: 'new_order' },
  { label: 'Export Portfolio CSV', action: 'export_csv' },
];

function fuzzyMatch(query: string, options: { label: string; action: string }[]) {
  if (!query) return options;
  const q = query.toLowerCase();
  return options.filter(opt => opt.label.toLowerCase().includes(q));
}

const RECENTS_KEY = 'command_palette_recents';

const CommandPalette: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  const [query, setQuery] = useState('');
  const [recents, setRecents] = useState<{ label: string; action: string }[]>([]);
  const [results, setResults] = useState(MOCK_COMMANDS);

  useEffect(() => {
    if (open) {
      setQuery('');
      setResults(MOCK_COMMANDS);
      const stored = localStorage.getItem(RECENTS_KEY);
      setRecents(stored ? JSON.parse(stored) : []);
    }
  }, [open]);

  useEffect(() => {
    setResults(fuzzyMatch(query, MOCK_COMMANDS));
  }, [query]);

  const handleSelect = (cmd: { label: string; action: string }) => {
    // Save to recents
    const newRecents = [cmd, ...recents.filter(r => r.action !== cmd.action)].slice(0, 5);
    setRecents(newRecents);
    localStorage.setItem(RECENTS_KEY, JSON.stringify(newRecents));
    onClose();
    // TODO: trigger navigation or actions
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          label="Search or Command (Cmd/Ctrl+K)"
          value={query}
          onChange={e => setQuery(e.target.value)}
          sx={{ mb: 2 }}
        />
        {recents.length > 0 && !query && (
          <Box sx={{ mb: 1 }}>
            <Typography variant="caption" color="text.secondary">Recent</Typography>
            <List dense>
              {recents.map(cmd => (
                <ListItem component="button" key={cmd.action} onClick={() => handleSelect(cmd)}>
                  <ListItemText primary={cmd.label} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
        <List dense>
          {results.map(cmd => (
            <ListItem component="button" key={cmd.action} onClick={() => handleSelect(cmd)}>
              <ListItemText primary={cmd.label} />
            </ListItem>
          ))}
        </List>
      </DialogContent>
    </Dialog>
  );
};

export default CommandPalette;