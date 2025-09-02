import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, Chip, Grid } from '@mui/material';
import KeyIcon from '@mui/icons-material/Key';
import BarChartIcon from '@mui/icons-material/BarChart';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import UserManagementPanel from './UserManagementPanel';

const ClientDashboard: React.FC = () => {
  const [licenseKey, setLicenseKey] = useState('XXXX-XXXX-XXXX-XXXX');
  const [licenseStatus, setLicenseStatus] = useState('Inactiva');

  const handleActivateLicense = () => {
    if (licenseKey.length > 0) {
      setLicenseStatus('Activa');
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Portal del Cliente
      </Typography>

      {/* Sección de Licencia */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <KeyIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6">Gestión de Licencia</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <Box sx={{ flexGrow: 1, minWidth: '250px' }}>
            <TextField
              fullWidth
              label="Clave de Licencia"
              variant="outlined"
              value={licenseKey}
              onChange={(e) => setLicenseKey(e.target.value)}
            />
          </Box>
          <Box>
            <Button fullWidth variant="contained" onClick={handleActivateLicense} sx={{ height: '56px' }}>
              Activar
            </Button>
          </Box>
          <Box>
            <Chip 
              label={licenseStatus}
              color={licenseStatus === 'Activa' ? 'success' : 'error'}
              sx={{ width: '100px', height: '56px' }}
            />
          </Box>
        </Box>
      </Paper>

      {/* Sección de Estadísticas */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <BarChartIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6">Estadísticas de Uso</Typography>
        </Box>
        <Typography variant="body1">Consultas a la API este mes: <strong>1,234,567</strong></Typography>
        <Typography variant="body1">Nodos activos en el enjambre: <strong>10</strong></Typography>
        <Typography variant="body1">Uso de memoria de conocimiento: <strong>78.5 GB</strong></Typography>
      </Paper>

      {/* Sección de Soporte */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <SupportAgentIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6">Soporte Técnico</Typography>
        </Box>
        <Typography variant="body1">¿Necesitas ayuda? Contacta a tu gestor de cuenta en <strong>support@mea-core.com</strong> o abre un ticket en nuestro portal de soporte.</Typography>
        <Button variant="outlined" sx={{ mt: 2 }}>Abrir Ticket</Button>
      </Paper>

      {/* Sección de Gestión de Usuarios */}
      <UserManagementPanel />
    </Box>
  );
};

export default ClientDashboard;
