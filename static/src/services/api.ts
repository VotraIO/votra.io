import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import * as types from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor - add JWT token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle token refresh and errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Token expired - attempt refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          
          localStorage.setItem('access_token', response.data.access_token);
          
          // Update authorization header
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          
          // Retry original request
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          
          // Emit logout event for components to listen to
          window.dispatchEvent(new CustomEvent('auth-logout'));
          
          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth Service
export const authService = {
  login: (credentials: types.LoginRequest) =>
    apiClient.post<types.LoginResponse>('/auth/login', credentials),
  
  register: (data: types.RegisterRequest) =>
    apiClient.post<types.LoginResponse>('/auth/register', data),
  
  refresh: (refreshToken: string) =>
    apiClient.post<types.LoginResponse>('/auth/refresh', { refresh_token: refreshToken }),
  
  me: () =>
    apiClient.get<types.User>('/auth/me'),
};

// Client Service
export const clientService = {
  list: (params?: { page?: number; page_size?: number; is_active?: boolean }) =>
    apiClient.get<types.PaginatedResponse<types.Client>>('/clients', { params }),
  
  get: (id: string) =>
    apiClient.get<types.Client>(`/clients/${id}`),
  
  create: (data: types.ClientCreate) =>
    apiClient.post<types.Client>('/clients', data),
  
  update: (id: string, data: types.ClientUpdate) =>
    apiClient.put<types.Client>(`/clients/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/clients/${id}`),
};

// Project Service
export const projectService = {
  list: (params?: { page?: number; page_size?: number; status?: string; client_id?: string }) =>
    apiClient.get<types.PaginatedResponse<types.Project>>('/projects', { params }),
  
  get: (id: string) =>
    apiClient.get<types.Project>(`/projects/${id}`),
  
  create: (data: types.ProjectCreate) =>
    apiClient.post<types.Project>('/projects', data),
  
  update: (id: string, data: types.ProjectUpdate) =>
    apiClient.put<types.Project>(`/projects/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/projects/${id}`),
};

// Timesheet Service
export const timesheetService = {
  list: (params?: { 
    page?: number; 
    page_size?: number; 
    project_id?: string;
    user_id?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
  }) =>
    apiClient.get<types.PaginatedResponse<types.Timesheet>>('/timesheets', { params }),
  
  get: (id: string) =>
    apiClient.get<types.Timesheet>(`/timesheets/${id}`),
  
  create: (data: types.TimesheetCreate) =>
    apiClient.post<types.Timesheet>('/timesheets', data),
  
  update: (id: string, data: types.TimesheetUpdate) =>
    apiClient.put<types.Timesheet>(`/timesheets/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/timesheets/${id}`),
};

// Invoice Service
export const invoiceService = {
  list: (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    client_id?: string;
    start_date?: string;
    end_date?: string;
  }) =>
    apiClient.get<types.PaginatedResponse<types.Invoice>>('/invoices', { params }),
  
  get: (id: string) =>
    apiClient.get<types.Invoice>(`/invoices/${id}`),
  
  create: (data: types.InvoiceCreate) =>
    apiClient.post<types.Invoice>('/invoices', data),
  
  send: (id: string) =>
    apiClient.post(`/invoices/${id}/send`, {}),
  
  markPaid: (id: string) =>
    apiClient.post(`/invoices/${id}/mark-paid`, {}),
};

// Report Service
export const reportService = {
  revenueReport: (params?: {
    start_date?: string;
    end_date?: string;
    client_id?: string;
  }) =>
    apiClient.get<types.RevenueReport[]>('/reports/revenue', { params }),
  
  utilizationReport: (params?: {
    start_date?: string;
    end_date?: string;
    consultant_id?: string;
  }) =>
    apiClient.get<types.UtilizationReport[]>('/reports/utilization', { params }),
  
  overdueInvoices: (params?: {
    days_overdue?: number;
  }) =>
    apiClient.get<types.OverdueInvoice[]>('/reports/overdue-invoices', { params }),
};

export default apiClient;
