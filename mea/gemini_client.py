"""
Gemini API Client - Integración con Google Gemini
Maneja la comunicación con la API de Gemini de forma segura.
"""
import os
import json
from typing import Dict, List, Optional


class GeminiClient:
    """Cliente para la API de Gemini (Google AI Studio)."""
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> str:
        """Genera texto usando Gemini."""
        if not self.api_key:
            return self._mock_generate(prompt)
        
        try:
            import httpx
            
            headers = {
                "Content-Type": "application/json"
            }
            
            contents = []
            if system_prompt:
                contents.append({
                    "role": "system",
                    "parts": [{"text": system_prompt}]
                })
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                else:
                    return f"[Error Gemini API: {response.status_code}]"
                    
        except Exception as e:
            return f"[Error: {e}]"
    
    async def chat(
        self,
        messages: List[Dict],
        system_prompt: str = None
    ) -> str:
        """Chat con historial de mensajes."""
        contents = []
        
        if system_prompt:
            contents.append({
                "role": "system",
                "parts": [{"text": system_prompt}]
            })
        
        for msg in messages:
            contents.append({
                "role": msg.get("role", "user"),
                "parts": [{"text": msg.get("content", "")}]
            })
        
        try:
            import httpx
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }
            
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                else:
                    return f"[Error: {response.status_code}]"
                    
        except Exception as e:
            return f"[Error: {e}]"
    
    def _mock_generate(self, prompt: str) -> str:
        """Mock para desarrollo sin API key."""
        return f"[Mock Response] Procesé: {prompt[:50]}..."
    
    def is_configured(self) -> bool:
        """Verifica si la API está configurada."""
        return bool(self.api_key)