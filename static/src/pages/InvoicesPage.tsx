import React, { useState, useEffect } from 'react';
import { AlertCircle, Eye, FileText, Send, CheckCircle, DollarSign } from 'lucide-react';
import { invoiceService, clientService } from '../../services/api';
import { Invoice, Client } from '../../types';
import { DataTable } from '../../components/common/DataTable';
import { Modal } from '../../components/common/Modal';

export const InvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    loadInvoices();
    loadClients();
  }, []);

  const loadInvoices = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await invoiceService.list({ page: 1, page_size: 100 });
      setInvoices(data.items || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load invoices');
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

  const handleViewDetails = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setIsDetailModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsDetailModalOpen(false);
    setSelectedInvoice(null);
  };

  const handleSendInvoice = async (invoiceId: string) => {
    setError(null);
    try {
      await invoiceService.update(invoiceId, { status: 'sent' });
      loadInvoices();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send invoice');
    }
  };

  const handleMarkPaid = async (invoiceId: string) => {
    setError(null);
    try {
      await invoiceService.update(invoiceId, { status: 'paid' });
      loadInvoices();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to mark invoice as paid');
    }
  };

  const getClientName = (clientId: string) => {
    return clients.find(c => c.id === clientId)?.name || 'Unknown Client';
  };

  const getStatusBadgeColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-700',
      sent: 'bg-blue-100 text-blue-700',
      viewed: 'bg-purple-100 text-purple-700',
      paid: 'bg-green-100 text-green-700',
      overdue: 'bg-red-100 text-red-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactNode> = {
      draft: <FileText size={14} />,
      sent: <Send size={14} />,
      viewed: <Eye size={14} />,
      paid: <CheckCircle size={14} />,
      overdue: <AlertCircle size={14} />,
    };
    return icons[status] || null;
  };

  const filteredInvoices = statusFilter === 'all' 
    ? invoices 
    : invoices.filter(inv => inv.status === statusFilter);

  const tableColumns = [
    { key: 'invoice_number' as const, label: 'Invoice #', sortable: true },
    { 
      key: 'client_id' as const, 
      label: 'Client', 
      render: (value: string) => getClientName(value) 
    },
    { 
      key: 'invoice_date' as const, 
      label: 'Date',
      sortable: true,
      render: (value: string) => new Date(value).toLocaleDateString()
    },
    { 
      key: 'total_amount' as const, 
      label: 'Total',
      render: (value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    },
    { 
      key: 'status' as const, 
      label: 'Status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 w-fit ${getStatusBadgeColor(value)}`}>
          {getStatusIcon(value)}
          {value.charAt(0).toUpperCase() + value.slice(1)}
        </span>
      ),
    },
  ];

  const totalRevenue = invoices
    .filter(inv => inv.status === 'paid')
    .reduce((sum, inv) => sum + inv.total_amount, 0);

  const pendingPayments = invoices
    .filter(inv => ['sent', 'viewed'].includes(inv.status))
    .reduce((sum, inv) => sum + inv.total_amount, 0);

  const overdueInvoices = invoices.filter(inv => inv.status === 'overdue').length;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-gray-600 text-sm mt-1">Manage and track invoice payments</p>
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

        {/* Status Filter */}
        <div className="mb-6 flex gap-2 overflow-x-auto">
          {['all', 'draft', 'sent', 'viewed', 'paid', 'overdue'].map(status => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition ${
                statusFilter === status
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
              {status !== 'all' && (
                <span className="ml-2">
                  ({invoices.filter(inv => inv.status === status).length})
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Data Table */}
        <div className="bg-white rounded-lg shadow">
          <DataTable
            columns={tableColumns}
            data={filteredInvoices}
            isLoading={isLoading}
            searchable={true}
            searchFields={['invoice_number']}
            onRowClick={(invoice) => handleViewDetails(invoice)}
            actions={[
              {
                label: 'View',
                onClick: (invoice) => handleViewDetails(invoice),
                className: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
              },
            ]}
          />
        </div>

        {/* Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <DollarSign className="text-green-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Total Revenue</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  ${totalRevenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <FileText className="text-yellow-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Pending Payment</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  ${pendingPayments.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="text-red-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Overdue Invoices</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{overdueInvoices}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Invoices by Status */}
        {overdueInvoices > 0 && (
          <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="text-red-600" size={18} />
              <h3 className="font-semibold text-red-900">⚠️ Overdue Invoices Alert</h3>
            </div>
            <p className="text-red-700 text-sm">
              You have {overdueInvoices} overdue invoice{overdueInvoices !== 1 ? 's' : ''}. Please follow up with clients for payment.
            </p>
          </div>
        )}
      </main>

      {/* Invoice Detail Modal */}
      <Modal
        isOpen={isDetailModalOpen}
        title={selectedInvoice ? `Invoice ${selectedInvoice.invoice_number}` : 'Invoice Details'}
        onClose={handleCloseModal}
        size="lg"
        footer={
          selectedInvoice && (
            <>
              <button
                onClick={handleCloseModal}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition"
              >
                Close
              </button>
              {selectedInvoice.status === 'draft' && (
                <button
                  onClick={() => {
                    handleSendInvoice(selectedInvoice.id);
                    handleCloseModal();
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
                >
                  <Send size={16} />
                  Send Invoice
                </button>
              )}
              {['sent', 'viewed'].includes(selectedInvoice.status) && (
                <button
                  onClick={() => {
                    handleMarkPaid(selectedInvoice.id);
                    handleCloseModal();
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
                >
                  <CheckCircle size={16} />
                  Mark as Paid
                </button>
              )}
            </>
          )
        }
      >
        {selectedInvoice && (
          <div className="space-y-4">
            {/* Header */}
            <div className="pb-4 border-b">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="text-sm text-gray-600">Invoice Number</p>
                  <p className="text-2xl font-bold text-gray-900">{selectedInvoice.invoice_number}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2 ${getStatusBadgeColor(selectedInvoice.status)}`}>
                  {getStatusIcon(selectedInvoice.status)}
                  {selectedInvoice.status.charAt(0).toUpperCase() + selectedInvoice.status.slice(1)}
                </span>
              </div>
            </div>

            {/* Client & Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Client</p>
                <p className="font-semibold text-gray-900">{getClientName(selectedInvoice.client_id)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Invoice Date</p>
                <p className="font-semibold text-gray-900">
                  {new Date(selectedInvoice.invoice_date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Due Date</p>
                <p className="font-semibold text-gray-900">
                  {new Date(selectedInvoice.due_date).toLocaleDateString()}
                </p>
              </div>
            </div>

            {/* Line Items */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Line Items</h4>
              <div className="space-y-2 bg-gray-50 rounded p-3 max-h-64 overflow-y-auto">
                {selectedInvoice.line_items && selectedInvoice.line_items.length > 0 ? (
                  selectedInvoice.line_items.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-start text-sm pb-2 border-b last:border-b-0">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{item.description}</p>
                        <p className="text-gray-600 text-xs">
                          {item.quantity} × ${item.unit_price.toFixed(2)}
                        </p>
                      </div>
                      <p className="font-semibold text-gray-900">
                        ${(item.quantity * item.unit_price).toFixed(2)}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-600 text-sm">No line items</p>
                )}
              </div>
            </div>

            {/* Totals */}
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-semibold text-gray-900">
                  ${(selectedInvoice.total_amount - (selectedInvoice.tax || 0)).toFixed(2)}
                </span>
              </div>
              {selectedInvoice.tax && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span className="font-semibold text-gray-900">
                    ${selectedInvoice.tax.toFixed(2)}
                  </span>
                </div>
              )}
              <div className="flex justify-between pt-2 border-t">
                <span className="font-semibold text-gray-900">Total Due</span>
                <span className="text-2xl font-bold text-purple-600">
                  ${selectedInvoice.total_amount.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Notes */}
            {selectedInvoice.notes && (
              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <p className="text-sm text-blue-900">{selectedInvoice.notes}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};
