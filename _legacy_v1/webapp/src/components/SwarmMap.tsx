import React, { useState } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Paper, Chip } from '@mui/material';
import HubIcon from '@mui/icons-material/Hub';

// Datos de ejemplo
const mockNodes = [
  {
    id: 'node-main-01',
    address: 'ws://192.168.1.10:8000',
    status: 'Online',
    isSelf: true,
  },
  {
    id: 'node-worker-02',
    address: 'ws://192.168.1.11:8000',
    status: 'Online',
    isSelf: false,
  },
  {
    id: 'node-worker-03',
    address: 'ws://192.168.1.12:8000',
    status: 'Offline',
    isSelf: false,
  },
];

const SwarmMap: React.FC = () => {
  const [nodes, setNodes] = useState(mockNodes);

  return (
    <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Mapa del Enjambre
      </Typography>
      <List dense>
        {nodes.map(node => (
          <ListItem key={node.id}>
            <HubIcon sx={{ mr: 1.5, color: node.status === 'Online' ? 'success.main' : 'error.main' }} />
            <ListItemText 
              primary={`${node.id}${node.isSelf ? ' (Este Nodo)' : ''}`}
              secondary={node.address}
            />
            <Chip 
              label={node.status}
              color={node.status === 'Online' ? 'success' : 'error'}
              size="small"
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default SwarmMap;
