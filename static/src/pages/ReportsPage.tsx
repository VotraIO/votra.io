import React, { useState, useEffect } from 'react';
import { AlertCircle, TrendingUp, Users, DollarSign, Clock } from 'lucide-react';
import { reportService, clientService } from '../../services/api';
import { Report, Client } from '../../types';
import { DataTable } from '../../components/common/DataTable';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<Report | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'revenue' | 'utilization' | 'overdue'>('revenue');
  const [clients, setClients] = useState<Client[]>([]);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    loadReports();
    loadClients();
  }, [dateRange]);

  const loadReports = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Revenue Report
      const revenueResponse = await reportService.getRevenueByClient({
        start_date: dateRange.start_date,
        end_date: dateRange.end_date,
      });

      // Utilization Report
      const utilizationResponse = await reportService.getUtilizationByConsultant({
        start_date: dateRange.start_date,
        end_date: dateRange.end_date,
      });

      // Overdue Invoices
      const overdueResponse = await reportService.getOverdueInvoices();

      setReports({
        revenue_by_client: revenueResponse.data || [],
        utilization_by_consultant: utilizationResponse.data || [],
        overdue_invoices: overdueResponse.data || [],
        total_revenue: 0,
        average_project_value: 0,
        total_consultants: 0,
        average_utilization: 0,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load reports');
    } finally {
      setIsLoading(false);
    }
  };

  const loadClients = async () => {
    try {
      const { data } = await clientService.list({ page: 1, page_size: 100 });
      setClients(data.items || []);
    } catch (err) {
      console.error('Failed to load clients:', err);
    }
  };

  const handleDateChange = (field: string, value: string) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="text-gray-600 mt-4">Loading reports...</p>
        </div>
      </div>
    );
  }

  const totalRevenue = reports?.revenue_by_client?.reduce((sum, item: any) => sum + (item.revenue || 0), 0) || 0;
  const totalBillableHours = reports?.utilization_by_consultant?.reduce((sum, item: any) => sum + (item.billable_hours || 0), 0) || 0;
  const totalOverdueAmount = reports?.overdue_invoices?.reduce((sum, item: any) => sum + (item.total_amount || 0), 0) || 0;

  const revenueColumns = [
    { key: 'client_name' as const, label: 'Client', sortable: true },
    { 
      key: 'revenue' as const, 
      label: 'Revenue',
      render: (value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    },
    { 
      key: 'invoice_count' as const, 
      label: 'Invoices',
      render: (value: number) => value || 0
    },
  ];

  const utilizationColumns = [
    { key: 'consultant_name' as const, label: 'Consultant', sortable: true },
    { 
      key: 'billable_hours' as const, 
      label: 'Billable Hours',
      render: (value: number) => `${value.toFixed(1)}h`
    },
    { 
      key: 'total_hours' as const, 
      label: 'Total Hours',
      render: (value: number) => `${value.toFixed(1)}h`
    },
    { 
      key: 'utilization_rate' as const, 
      label: 'Utilization %',
      render: (value: number) => `${(value * 100).toFixed(1)}%`
    },
  ];

  const overdueColumns = [
    { key: 'invoice_number' as const, label: 'Invoice #', sortable: true },
    { key: 'client_name' as const, label: 'Client' },
    { 
      key: 'total_amount' as const, 
      label: 'Amount',
      render: (value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    },
    { 
      key: 'due_date' as const, 
      label: 'Days Overdue',
      render: (value: string) => {
        const daysOverdue = Math.floor((Date.now() - new Date(value).getTime()) / (1000 * 60 * 60 * 24));
        return daysOverdue > 0 ? `${daysOverdue} days` : 'Due today';
      }
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-gray-600 text-sm mt-1">Business metrics and performance insights</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={18} />
            <div>
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Date Range Filter */}
        <div className="bg-white rounded-lg shadow p-4 mb-8">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={dateRange.start_date}
                onChange={(e) => handleDateChange('start_date', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={dateRange.end_date}
                onChange={(e) => handleDateChange('end_date', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <DollarSign className="text-green-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Total Revenue</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  ${totalRevenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <Clock className="text-blue-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Billable Hours</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {totalBillableHours.toFixed(0)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="text-red-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Overdue Amount</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  ${totalOverdueAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <TrendingUp className="text-purple-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Active Clients</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {clients.filter(c => c.is_active).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200 bg-white rounded-lg shadow">
          <div className="flex">
            {(['revenue', 'utilization', 'overdue'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 font-medium border-b-2 transition ${
                  activeTab === tab
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab === 'revenue' && 'Revenue by Client'}
                {tab === 'utilization' && 'Consultant Utilization'}
                {tab === 'overdue' && 'Overdue Invoices'}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow">
          {activeTab === 'revenue' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue by Client</h3>
              <DataTable
                columns={revenueColumns}
                data={reports?.revenue_by_client || []}
                isLoading={isLoading}
                searchable={true}
                searchFields={['client_name']}
              />
              {(!reports?.revenue_by_client || reports.revenue_by_client.length === 0) && !isLoading && (
                <p className="text-center text-gray-600 py-8">No revenue data available for the selected period.</p>
              )}
            </div>
          )}

          {activeTab === 'utilization' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Consultant Utilization</h3>
              <DataTable
                columns={utilizationColumns}
                data={reports?.utilization_by_consultant || []}
                isLoading={isLoading}
                searchable={true}
                searchFields={['consultant_name']}
              />
              {(!reports?.utilization_by_consultant || reports.utilization_by_consultant.length === 0) && !isLoading && (
                <p className="text-center text-gray-600 py-8">No utilization data available for the selected period.</p>
              )}
            </div>
          )}

          {activeTab === 'overdue' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Overdue Invoices</h3>
              {reports?.overdue_invoices && reports.overdue_invoices.length > 0 && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={18} />
                  <div>
                    <h4 className="font-semibold text-red-900">⚠️ Immediate Action Required</h4>
                    <p className="text-red-700 text-sm">
                      {reports.overdue_invoices.length} invoice{reports.overdue_invoices.length !== 1 ? 's' : ''} are overdue. 
                      Total outstanding: ${totalOverdueAmount.toFixed(2)}
                    </p>
                  </div>
                </div>
              )}
              <DataTable
                columns={overdueColumns}
                data={reports?.overdue_invoices || []}
                isLoading={isLoading}
                searchable={true}
                searchFields={['invoice_number', 'client_name']}
              />
              {(!reports?.overdue_invoices || reports.overdue_invoices.length === 0) && !isLoading && (
                <p className="text-center text-gray-600 py-8 text-lg">✓ No overdue invoices. Great work!</p>
              )}
            </div>
          )}
        </div>

        {/* Legend / Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Revenue Insights</h4>
            <p className="text-blue-700 text-sm">
              Track revenue by client to identify top earners and growth opportunities.
            </p>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 className="font-semibold text-purple-900 mb-2">📊 Utilization Metrics</h4>
            <p className="text-purple-700 text-sm">
              Monitor consultant utilization rates to optimize resource allocation.
            </p>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-semibold text-red-900 mb-2">⏰ Payment Status</h4>
            <p className="text-red-700 text-sm">
              Stay on top of overdue invoices and follow up with clients promptly.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};
