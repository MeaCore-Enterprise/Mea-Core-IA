import React, { useState, useEffect } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Chip, Paper } from '@mui/material';

// Datos de ejemplo (mock data)
const mockGoals = [
  {
    id: 'g1',
    description: "Investigar y aprender sobre: 'física de partículas'",
    status: 'IN_PROGRESS',
    source: 'curiosity',
  },
  {
    id: 'g2',
    description: "Optimizar embeddings para consultas frecuentes sobre 'historia'",
    status: 'PENDING',
    source: 'system',
  },
  {
    id: 'g3',
    description: "Explorar el documento 'nuevas_especificaciones.pdf'",
    status: 'COMPLETED',
    source: 'user_request',
  },
];

const statusColors: { [key: string]: "success" | "warning" | "default" | "primary" } = {
  PENDING: 'warning',
  IN_PROGRESS: 'primary',
  COMPLETED: 'success',
};

const GoalsPanel: React.FC = () => {
  // En una implementación real, esto vendría de una llamada a la API
  const [goals, setGoals] = useState(mockGoals);

  return (
    <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Objetivos Activos
      </Typography>
      <List dense>
        {goals.map(goal => (
          <ListItem key={goal.id} disablePadding>
            <ListItemText 
              primary={goal.description} 
              secondary={`Fuente: ${goal.source}`}
            />
            <Chip 
              label={goal.status}
              color={statusColors[goal.status] || 'default'}
              size="small"
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default GoalsPanel;
