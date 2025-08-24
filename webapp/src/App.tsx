import React from 'react';
import Chat from './Chat';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Un tema oscuro básico para la aplicación
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Chat />
    </ThemeProvider>
  );
}

export default App;
