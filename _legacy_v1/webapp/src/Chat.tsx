import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, IconButton, Paper, List, ListItem, Typography, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import authService from './services/authService'; // Importar el servicio de autenticación
import API_URL from './config';

// Definir la estructura de un mensaje
interface Message {
  sender: 'user' | 'bot';
  text: string;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages]);

  const handleSendMessage = async () => {
    if (input.trim() === '' || isLoading) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const token = authService.getCurrentUser();
    if (!token) {
      const errorMessage: Message = {
        sender: 'bot',
        text: 'Error de autenticación. Por favor, inicia sesión de nuevo.',
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Añadir el token de autorización
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.statusText}`);
      }

      const data = await response.json();
      const botMessage: Message = { 
        sender: 'bot', 
        text: data.responses.join('\n')
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      const errorMessage: Message = {
        sender: 'bot',
        text: 'Error: No se pudo conectar con el núcleo de la IA.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Paper elevation={3} sx={{ height: '70vh', display: 'flex', flexDirection: 'column', bgcolor: 'background.paper' }}>
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
        <List>
          {messages.map((msg, index) => (
            <ListItem key={index} sx={{ display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <Paper elevation={1} sx={{
                p: 1.5,
                bgcolor: msg.sender === 'user' ? '#007bff' : '#333',
                color: 'white',
                maxWidth: '80%',
              }}>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{msg.text}</Typography>
              </Paper>
            </ListItem>
          ))}
          {isLoading && (
            <ListItem sx={{ display: 'flex', justifyContent: 'flex-start' }}>
               <CircularProgress size={24} />
            </ListItem>
          )}
          <div ref={messagesEndRef} />
        </List>
      </Box>
      <Box sx={{ p: 2, borderTop: '1px solid #444' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Escribe tu mensaje..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            size="small"
          />
          <IconButton color="primary" onClick={handleSendMessage} disabled={isLoading} sx={{ ml: 1 }}>
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
}

export default Chat;
