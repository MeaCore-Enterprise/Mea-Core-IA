import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, IconButton, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface Message {
  sender: 'user' | 'assistant' | 'system';
  text: string;
}

const WEBSOCKET_URL = "ws://localhost:8000/ws/query";

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'assistant', text: 'Hola! Soy MEA-Core. ¿Cómo puedo ayudarte hoy?' },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isConnecting, setIsConnecting] = useState(true);
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    // Conectar al WebSocket
    ws.current = new WebSocket(WEBSOCKET_URL);
    setMessages((prev) => [...prev, {sender: 'system', text: 'Conectando al servidor...'}]);

    ws.current.onopen = () => {
      console.log("WebSocket Connected");
      setIsConnecting(false);
      setMessages((prev) => [...prev, {sender: 'system', text: 'Conexión establecida.'}]);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.responses) {
        const assistantMessage: Message = { sender: 'assistant', text: data.responses.join('\n') };
        setMessages((prevMessages) => [...prevMessages, assistantMessage]);
      } else if (data.error) {
        const errorMessage: Message = { sender: 'system', text: `Error: ${data.error}` };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
      }
    };

    ws.current.onerror = (event) => {
      console.error("WebSocket Error:", event);
      setMessages((prev) => [...prev, {sender: 'system', text: 'Error de conexión. Asegúrate de que el servidor esté corriendo.'}]);
    };

    ws.current.onclose = () => {
      console.log("WebSocket Disconnected");
      setIsConnecting(false);
      setMessages((prev) => [...prev, {sender: 'system', text: 'Desconectado del servidor.'}]);
    };

    // Limpiar la conexión al desmontar el componente
    return () => {
      ws.current?.close();
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim() && ws.current && ws.current.readyState === WebSocket.OPEN) {
      const userMessage: Message = { sender: 'user', text: inputValue };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      
      // Enviar mensaje al servidor a través de WebSocket
      ws.current.send(JSON.stringify({ text: inputValue }));

      setInputValue('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'grey.900', // Fondo más oscuro
      }}
    >
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Paper
              variant="outlined"
              sx={{
                p: 1.5,
                bgcolor: msg.sender === 'user' ? 'primary.main' : (msg.sender === 'assistant' ? 'grey.800' : 'error.dark'),
                color: msg.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                maxWidth: '70%',
                borderRadius: msg.sender === 'user' ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
              }}
            >
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{msg.text}</Typography>
            </Paper>
          </Box>
        ))}
        {isConnecting && <CircularProgress sx={{ display: 'block', margin: 'auto' }}/>}
        <div ref={messagesEndRef} />
      </Box>
      <Box sx={{ p: 2, bgcolor: 'grey.800' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Escribe tu mensaje..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            multiline
            maxRows={4}
            disabled={isConnecting || (ws.current && ws.current.readyState !== WebSocket.OPEN)}
          />
          <IconButton 
            color="primary" 
            onClick={handleSend} 
            sx={{ ml: 1 }}
            disabled={isConnecting || (ws.current && ws.current.readyState !== WebSocket.OPEN)}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default Chat;
