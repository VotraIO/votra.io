import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as types from '../types';
import { authService } from '../services/api';

interface AuthContextType {
  user: types.User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuth = (): AuthContextType => {
  const [user, setUser] = useState<types.User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Load user from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);

    // Listen for logout events from other tabs
    const handleLogout = () => {
      setUser(null);
      localStorage.removeItem('user');
    };

    window.addEventListener('auth-logout', handleLogout);
    return () => window.removeEventListener('auth-logout', handleLogout);
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authService.login({ username, password });
      const { access_token, refresh_token } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Fetch current user info
      const userResponse = await authService.me();
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      setUser(userResponse.data);

      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string,
    fullName: string
  ) => {
    setIsLoading(true);
    try {
      const response = await authService.register({
        username,
        email,
        password,
        full_name: fullName,
      });
      const { access_token, refresh_token } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Fetch current user info
      const userResponse = await authService.me();
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      setUser(userResponse.data);

      navigate('/dashboard');
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/login');
  };

  const refreshToken = async () => {
    const refreshTokenValue = localStorage.getItem('refresh_token');
    if (!refreshTokenValue) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await authService.refresh(refreshTokenValue);
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
    } catch (error) {
      logout();
      throw error;
    }
  };

  return {
    user,
    isLoading,
    isAuthenticated: !!user && !!localStorage.getItem('access_token'),
    login,
    register,
    logout,
    refreshToken,
  };
};
