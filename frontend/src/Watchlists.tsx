import React, { useState } from 'react';
import { Paper, Typography, Chip, IconButton, TextField, Button, Box, Grid, List, ListItem, ListItemText, ListItemSecondaryAction, Menu, MenuItem } from '@mui/material';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import AddAlertIcon from '@mui/icons-material/AddAlert';
import ColorLensIcon from '@mui/icons-material/ColorLens';

type WatchItem = {
  symbol: string;
  color: string;
  alert?: string;
};

const COLORS = ['primary', 'secondary', 'success', 'warning', 'error', 'info'];

const initialWatchlists = [
  {
    name: 'Tech',
    items: [
  { symbol: 'AAPL', color: 'primary', alert: undefined },
  { symbol: 'GOOG', color: 'secondary', alert: undefined },
    ],
  },
  {
    name: 'Auto',
    items: [
      { symbol: 'TSLA', color: 'success', alert: undefined },
    ],
  },
];

const Watchlists: React.FC<{ setToast?: (t: any) => void }> = ({ setToast }) => {
  const [watchlists, setWatchlists] = useState(initialWatchlists);
  const [newList, setNewList] = useState('');
  const [newSymbol, setNewSymbol] = useState('');
  const [selectedList, setSelectedList] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [colorMenuIdx, setColorMenuIdx] = useState<{list: number, item: number} | null>(null);

  // Drag-and-drop reorder (mock, not persistent)
  const moveItem = (from: number, to: number) => {
    if (from === to) return;
    setWatchlists(wl => wl.map((list, idx) =>
      idx === selectedList
        ? { ...list, items: reorder(list.items, from, to) }
        : list
    ));
  };
  function reorder(arr: any[], from: number, to: number) {
    const copy = [...arr];
    const [item] = copy.splice(from, 1);
    copy.splice(to, 0, item);
    return copy;
  }

  // Color tag menu
  const handleColorMenu = (event: React.MouseEvent<HTMLElement>, listIdx: number, itemIdx: number) => {
    setAnchorEl(event.currentTarget);
    setColorMenuIdx({ list: listIdx, item: itemIdx });
  };
  const handleColorSelect = (color: string) => {
    if (colorMenuIdx) {
      setWatchlists(wl => wl.map((list, lidx) =>
        lidx === colorMenuIdx.list
          ? { ...list, items: list.items.map((item, iidx) => iidx === colorMenuIdx.item ? { ...item, color } : item) }
          : list
      ));
    }
    setAnchorEl(null);
    setColorMenuIdx(null);
  };

  // Inline alert creation
  const handleAddAlert = (listIdx: number, itemIdx: number) => {
    const alert = prompt('Set alert for ' + watchlists[listIdx].items[itemIdx].symbol + ' (e.g. ">150")');
    if (alert) {
      setWatchlists(wl => wl.map((list, lidx) =>
        lidx === listIdx
          ? { ...list, items: list.items.map((item, iidx) => iidx === itemIdx ? { ...item, alert } : item) }
          : list
      ));
    }
  };

  // Add new watchlist
  const handleAddList = () => {
    if (newList.trim()) {
      setWatchlists([...watchlists, { name: newList.trim(), items: [] }]);
      setNewList('');
      setToast && setToast({ msg: 'Watchlist added!', type: 'success' });
    }
  };
  // Add new symbol
  const handleAddSymbol = () => {
    if (newSymbol.trim()) {
      setWatchlists(wl => wl.map((list, idx) =>
        idx === selectedList
          ? { ...list, items: [...list.items, { symbol: newSymbol.trim().toUpperCase(), color: 'primary' }] }
          : list
      ));
      setNewSymbol('');
      setToast && setToast({ msg: 'Symbol added to watchlist!', type: 'success' });
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>Watchlists</Typography>
      <Box sx={{ mb: 2 }}>
        <TextField label="New Watchlist" value={newList} onChange={e => setNewList(e.target.value)} size="small" sx={{ mr: 1 }} />
        <Button onClick={handleAddList} variant="outlined">Add List</Button>
      </Box>
      <Box sx={{ mb: 2 }}>
        <TextField
          select
          label="Select Watchlist"
          value={selectedList}
          onChange={e => setSelectedList(Number(e.target.value))}
          size="small"
          sx={{ mr: 1 }}
        >
          {watchlists.map((wl, idx) => (
            <MenuItem key={wl.name} value={idx}>{wl.name}</MenuItem>
          ))}
        </TextField>
        <TextField label="Add Symbol" value={newSymbol} onChange={e => setNewSymbol(e.target.value)} size="small" sx={{ mr: 1 }} />
        <Button onClick={handleAddSymbol} variant="outlined">Add Symbol</Button>
      </Box>
      <List>
        {watchlists[selectedList].items.map((item, idx) => (
          <ListItem key={item.symbol} sx={{ pl: 0 }}>
            <IconButton edge="start" size="small" sx={{ cursor: 'grab' }} onClick={() => moveItem(idx, Math.max(0, idx - 1))}><DragIndicatorIcon /></IconButton>
            <ListItemText primary={item.symbol} />
            <Chip label={item.color} color={item.color as any} size="small" sx={{ mx: 1 }} onClick={e => handleColorMenu(e, selectedList, idx)} icon={<ColorLensIcon />} />
            {item.alert && <Chip label={item.alert} color="warning" size="small" icon={<AddAlertIcon />} sx={{ mx: 1 }} />}
            <IconButton edge="end" size="small" onClick={() => handleAddAlert(selectedList, idx)}><AddAlertIcon /></IconButton>
            <IconButton edge="end" size="small" onClick={() => moveItem(idx, Math.min(watchlists[selectedList].items.length - 1, idx + 1))}><DragIndicatorIcon sx={{ transform: 'rotate(90deg)' }} /></IconButton>
          </ListItem>
        ))}
      </List>
      <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={() => setAnchorEl(null)}>
        {COLORS.map(color => (
          <MenuItem key={color} onClick={() => handleColorSelect(color)}>
            <Chip label={color} color={color as any} size="small" />
          </MenuItem>
        ))}
      </Menu>
    </Paper>
  );
};

export default Watchlists;