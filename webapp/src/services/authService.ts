import { UserCreate } from './schemas';

const API_URL = 'http://127.0.0.1:8000';

const authService = {
    login: async (username: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Usuario o contraseña incorrectos');
        }

        const data = await response.json();
        if (data.access_token) {
            localStorage.setItem('user_token', data.access_token);
        }
        return data;
    },

    register: async (userData: UserCreate) => {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al registrar el usuario');
        }

        return response.json();
    },

    logout: () => {
        localStorage.removeItem('user_token');
    },

    getCurrentUser: () => {
        return localStorage.getItem('user_token');
    },
};

export default authService;
