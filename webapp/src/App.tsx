import React, { useState } from 'react';
import { CssBaseline, Container, Box, Typography, createTheme, ThemeProvider, Button } from '@mui/material';
import Login from './components/Login';
import authService from './services/authService';
import ClientDashboard from './components/ClientDashboard';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#64ffda', // Un verde menta brillante
    },
    background: {
      default: '#0a192f',
      paper: '#1c2a45',
    },
    text: {
      primary: '#e6f1ff',
      secondary: '#a8b2d1',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
  },
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!authService.getCurrentUser());

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Login onLoginSuccess={handleLoginSuccess} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Mea-Core Enterprise
          </Typography>
          <Button variant="outlined" color="primary" onClick={handleLogout}>
            Cerrar Sesión
          </Button>
        </Box>

        <ClientDashboard />

      </Container>
    </ThemeProvider>
  );
}

export default App;
