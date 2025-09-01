import React, { useState } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Paper, Chip } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

// Datos de ejemplo
const mockLearnings = [
  {
    id: 'l1',
    concept: 'Computación Cuántica Adiabática',
    timestamp: 'Hace 5 minutos',
    source: 'Investigación Autónoma',
  },
  {
    id: 'l2',
    concept: 'Redes Neuronales Convolucionales (CNN)',
    timestamp: 'Hace 2 horas',
    source: 'Análisis de Documento',
  },
  {
    id: 'l3',
    concept: 'Algoritmo de consenso Raft',
    timestamp: 'Hace 1 día',
    source: 'Interacción con Enjambre',
  },
];

const LearningFeed: React.FC = () => {
  const [learnings, setLearnings] = useState(mockLearnings);

  return (
    <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Nuevos Aprendizajes
      </Typography>
      <List dense>
        {learnings.map(learning => (
          <ListItem key={learning.id} secondaryAction={<Chip label={learning.source} size="small" />}>
            <SchoolIcon sx={{ mr: 1.5, color: 'primary.main' }} />
            <ListItemText 
              primary={learning.concept} 
              secondary={learning.timestamp} 
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default LearningFeed;
