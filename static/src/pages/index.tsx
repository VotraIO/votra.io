import React from 'react';
import { Link } from 'react-router-dom';

const PlaceholderPage: React.FC<{ title: string; description: string }> = ({ title, description }) => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Link to="/dashboard" className="text-purple-600 hover:text-purple-700 text-sm font-medium mb-2 block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="inline-block p-4 bg-blue-100 rounded-lg mb-4">
            <div className="text-4xl">🚧</div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Coming Soon</h2>
          <p className="text-gray-600 mb-6">{description}</p>
          <Link
            to="/dashboard"
            className="inline-block px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            Back to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
};

export const ClientsPage: React.FC = () => (
  <PlaceholderPage title="Clients" description="Manage your client profiles and contact information." />
);

export const ProjectsPage: React.FC = () => (
  <PlaceholderPage title="Projects" description="Create and manage consulting projects." />
);

export const TimesheetsPage: React.FC = () => (
  <PlaceholderPage title="Timesheets" description="Log billable and non-billable hours." />
);

export const InvoicesPage: React.FC = () => (
  <PlaceholderPage title="Invoices" description="Generate and manage client invoices." />
);

export const ReportsPage: React.FC = () => (
  <PlaceholderPage title="Reports" description="View revenue, utilization, and analytics." />
);
