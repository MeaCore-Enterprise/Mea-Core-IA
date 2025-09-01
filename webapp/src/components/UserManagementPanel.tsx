import React, { useState } from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, IconButton, Button, TextField } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

// Datos de ejemplo
const mockUsers = [
  { id: 1, name: 'Alice', email: 'alice@cliente.com', role: 'admin' },
  { id: 2, name: 'Bob', email: 'bob@cliente.com', role: 'user' },
  { id: 3, name: 'Charlie', email: 'charlie@cliente.com', role: 'user' },
];

const UserManagementPanel: React.FC = () => {
  const [users, setUsers] = useState(mockUsers);

  const handleAddUser = () => {
    // Lógica para añadir un nuevo usuario (abrir un modal, etc.)
    alert('Funcionalidad para añadir nuevo usuario.');
  };

  const handleDeleteUser = (userId: number) => {
    setUsers(users.filter(user => user.id !== userId));
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Gestión de Usuarios</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddUser}>
          Añadir Usuario
        </Button>
      </Box>
      <List>
        {users.map(user => (
          <ListItem key={user.id} secondaryAction={
            <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteUser(user.id)}>
              <DeleteIcon />
            </IconButton>
          }>
            <ListItemText primary={user.name} secondary={`${user.email} - Rol: ${user.role}`} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default UserManagementPanel;
