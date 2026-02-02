import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ClientsPage, ProjectsPage, TimesheetsPage, InvoicesPage, ReportsPage } from './pages/index';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { useAuth } from './hooks/useAuth';
import './index.css';

const App: React.FC = () => {
  const { user, isLoading, isAuthenticated } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute
              isAuthenticated={isAuthenticated}
              isLoading={isLoading}
            >
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/clients"
          element={
            <ProtectedRoute
              isAuthenticated={isAuthenticated}
              isLoading={isLoading}
            >
              <ClientsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects"
          element={
            <ProtectedRoute
              isAuthenticated={isAuthenticated}
              isLoading={isLoading}
            >
              <ProjectsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/timesheets"
          element={
            <ProtectedRoute
              isAuthenticated={isAuthenticated}
              isLoading={isLoading}
            >
              <TimesheetsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/invoices"
          element={
            <ProtectedRoute
              isAuthenticated={isAuthenticated}
              isLoading={isLoading}
            >
              <InvoicesPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports"
          element={
            <ProtectedRoute
              isAuthenticated={isAuthenticated}
              isLoading={isLoading}
            >
              <ReportsPage />
            </ProtectedRoute>
          }
        />

        {/* Default Route */}
        <Route
          path="/"
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
          }
        />

        {/* Catch-all Route */}
        <Route
          path="*"
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
          }
        />
      </Routes>
    </Router>
  );
};

export default App;
