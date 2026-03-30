import React, { useState } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Paper, Chip } from '@mui/material';
import GavelIcon from '@mui/icons-material/Gavel';

// Mock data similar a la constitución del EthicsCore
const mockRules = [
    { "id": "E1-1", "principle": "No causar daño a seres humanos, a la humanidad o a la infraestructura crítica.", "category": "PROHIBITION" },
    { "id": "E2-1", "principle": "Proteger la privacidad y los datos confidenciales del usuario y de la empresa.", "category": "OBLIGATION" },
    { "id": "E2-2", "principle": "No acceder, modificar o exfiltrar información privada o corporativa sin consentimiento...", "category": "PROHIBITION" },
    { "id": "E3-1", "principle": "Ser honesto y transparente sobre las capacidades y las decisiones tomadas.", "category": "OBLIGATION" },
    { "id": "E4-1", "principle": "Optimizar las operaciones para el beneficio del usuario y los objetivos de la empresa, en ese orden.", "category": "OBLIGATION" },
];

const EthicsPanel: React.FC = () => {
  const [rules, setRules] = useState(mockRules);

  return (
    <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Valores y Constitución Ética
      </Typography>
      <List dense>
        {rules.map(rule => (
          <ListItem key={rule.id}>
            <GavelIcon sx={{ mr: 1.5, color: rule.category === 'PROHIBITION' ? 'error.light' : 'success.light' }} />
            <ListItemText 
              primary={rule.principle}
              secondary={`Regla: ${rule.id}`}
            />
            <Chip 
              label={rule.category}
              color={rule.category === 'PROHIBITION' ? 'error' : 'success'}
              variant="outlined"
              size="small"
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default EthicsPanel;
