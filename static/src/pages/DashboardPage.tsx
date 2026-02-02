import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { LogOut, Users, FileText, Clock, DollarSign, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();

  const stats = [
    { label: 'Total Revenue', value: '$125,000', icon: DollarSign, color: 'bg-green-500' },
    { label: 'Active Projects', value: '8', icon: FileText, color: 'bg-blue-500' },
    { label: 'Billable Hours', value: '1,240', icon: Clock, color: 'bg-purple-500' },
    { label: 'Utilization Rate', value: '78%', icon: BarChart3, color: 'bg-orange-500' },
  ];

  const quickActions = [
    { label: 'View Clients', path: '/clients', icon: Users },
    { label: 'Create Project', path: '/projects', icon: FileText },
    { label: 'Log Time', path: '/timesheets', icon: Clock },
    { label: 'View Invoices', path: '/invoices', icon: DollarSign },
    { label: 'View Reports', path: '/reports', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 text-sm mt-1">
              Welcome back, <span className="font-semibold">{user?.full_name}</span>!
            </p>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm font-medium">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg text-white`}>
                    <Icon size={24} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Link
                  key={index}
                  to={action.path}
                  className="flex flex-col items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition"
                >
                  <Icon className="text-purple-600 mb-2" size={24} />
                  <span className="text-sm font-medium text-gray-700 text-center">{action.label}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* User Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Your Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-gray-600 text-sm">Full Name</p>
              <p className="text-gray-900 font-semibold mt-1">{user?.full_name}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Email</p>
              <p className="text-gray-900 font-semibold mt-1">{user?.email}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Username</p>
              <p className="text-gray-900 font-semibold mt-1">{user?.username}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Role</p>
              <p className="text-gray-900 font-semibold mt-1 capitalize">
                {user?.role.replace('_', ' ')}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
