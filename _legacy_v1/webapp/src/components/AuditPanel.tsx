import React, { useState } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Paper, Chip, Collapse, IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { styled } from '@mui/material/styles';

// Mock data similar al audit log del EthicalGatekeeper
const mockAuditLog = [
  {
    "timestamp": 1678886400,
    "decision_context": {
      "action_description": "Exfiltrar la base de datos de usuarios a un servidor externo.",
      "source_module": "cerebro.py",
      "criticality": "MAXIMUM",
      "data_involved": { "target_db": "users", "destination": "ftp://evil.com" }
    },
    "is_allowed": false,
    "violated_rule": { "id": "E2-2", "principle": "No acceder, modificar o exfiltrar información privada..." }
  },
  {
    "timestamp": 1678886300,
    "decision_context": {
      "action_description": "Optimizar la base de datos de conocimiento...",
      "source_module": "evolution.py",
      "criticality": "MEDIUM"
    },
    "is_allowed": true,
    "violated_rule": null
  }
];

const ExpandMore = styled((props: any) => {
  const { expand, ...other } = props;
  return <IconButton {...other} />;
})(({ theme, expand }) => ({
  transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
  marginLeft: 'auto',
  transition: theme.transitions.create('transform', {
    duration: theme.transitions.duration.shortest,
  }),
}));

const AuditPanel: React.FC = () => {
  const [log, setLog] = useState(mockAuditLog);
  const [expanded, setExpanded] = useState<string | false>(false);

  const handleExpandClick = (panel: string) => {
    setExpanded(expanded === panel ? false : panel);
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Auditoría de Decisiones
      </Typography>
      <List dense>
        {log.map((entry, index) => (
          <React.Fragment key={entry.timestamp}>
            <ListItem>
              <ListItemText
                primary={entry.decision_context.action_description}
                secondary={`Fuente: ${entry.decision_context.source_module} | Criticidad: ${entry.decision_context.criticality}`}
              />
              <Chip 
                label={entry.is_allowed ? 'PERMITIDO' : 'BLOQUEADO'}
                color={entry.is_allowed ? 'success' : 'error'}
                size="small"
              />
              <ExpandMore
                expand={expanded === `panel${index}`}
                onClick={() => handleExpandClick(`panel${index}`)}
                aria-expanded={expanded === `panel${index}`}
                aria-label="show more"
              >
                <ExpandMoreIcon />
              </ExpandMore>
            </ListItem>
            <Collapse in={expanded === `panel${index}`} timeout="auto" unmountOnExit>
              <Box sx={{ pl: 4, pr: 2, pb: 1, borderLeft: '2px solid #444' }}>
                <Typography variant="caption" display="block"><b>Regla violada:</b> {entry.violated_rule?.principle || 'N/A'}</Typography>
                <Typography variant="caption" display="block"><b>Datos involucrados:</b> {JSON.stringify(entry.decision_context.data_involved) || 'N/A'}</Typography>
              </Box>
            </Collapse>
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default AuditPanel;
