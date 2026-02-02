import React from 'react';
import { Navigate } from 'react-router-dom';
import * as types from '../types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  isAuthenticated: boolean;
  isLoading: boolean;
  requiredRoles?: types.User['role'][];
  userRole?: types.User['role'];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  isAuthenticated,
  isLoading,
  requiredRoles,
  userRole,
}) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRoles && userRole && !requiredRoles.includes(userRole)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-4xl font-bold text-red-600 mb-4">Access Denied</h1>
        <p className="text-gray-600 mb-8">You don't have permission to access this page.</p>
        <Navigate to="/dashboard" replace />
      </div>
    );
  }

  return <>{children}</>;
};
