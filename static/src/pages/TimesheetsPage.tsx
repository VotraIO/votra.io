import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, AlertCircle, Clock } from 'lucide-react';
import { timesheetService, projectService } from '../../services/api';
import { Timesheet, TimesheetCreate, Project } from '../../types';
import { DataTable } from '../../components/common/DataTable';
import { Modal } from '../../components/common/Modal';

export const TimesheetsPage: React.FC = () => {
  const [timesheets, setTimesheets] = useState<Timesheet[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTimesheet, setEditingTimesheet] = useState<Timesheet | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const [formData, setFormData] = useState<TimesheetCreate>({
    project_id: '',
    date: new Date().toISOString().split('T')[0],
    hours: 8,
    description: '',
    is_billable: true,
  });

  useEffect(() => {
    loadTimesheets();
    loadProjects();
  }, []);

  const loadTimesheets = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await timesheetService.list({ page: 1, page_size: 50 });
      setTimesheets(data.items || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load timesheets');
    } finally {
      setIsLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      const { data } = await projectService.list({ page: 1, page_size: 100 });
      setProjects(data.items || []);
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const handleOpenModal = (timesheet?: Timesheet) => {
    if (timesheet) {
      setEditingTimesheet(timesheet);
      setFormData({
        project_id: timesheet.project_id,
        date: timesheet.date,
        hours: timesheet.hours,
        description: timesheet.description || '',
        is_billable: timesheet.is_billable,
      });
    } else {
      setEditingTimesheet(null);
      setFormData({
        project_id: '',
        date: new Date().toISOString().split('T')[0],
        hours: 8,
        description: '',
        is_billable: true,
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingTimesheet(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (editingTimesheet) {
        await timesheetService.update(editingTimesheet.id, formData);
      } else {
        await timesheetService.create(formData);
      }
      handleCloseModal();
      loadTimesheets();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save timesheet entry');
    }
  };

  const handleDelete = async (id: string) => {
    setError(null);
    try {
      await timesheetService.delete(id);
      setDeleteConfirm(null);
      loadTimesheets();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete timesheet entry');
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target as any;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : 
              name === 'hours' ? parseFloat(value) || 0 : value,
    }));
  };

  const getProjectName = (projectId: string) => {
    return projects.find(p => p.id === projectId)?.name || 'Unknown Project';
  };

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    submitted: 'bg-blue-100 text-blue-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  };

  const tableColumns = [
    { key: 'date' as const, label: 'Date', sortable: true },
    { 
      key: 'project_id' as const, 
      label: 'Project', 
      render: (value: string) => getProjectName(value) 
    },
    { 
      key: 'hours' as const, 
      label: 'Hours',
      render: (value: number) => `${value.toFixed(1)}h`
    },
    { 
      key: 'is_billable' as const, 
      label: 'Billable',
      render: (value: boolean) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${value ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
          {value ? 'Yes' : 'No'}
        </span>
      ),
    },
    { 
      key: 'status' as const, 
      label: 'Status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[value] || 'bg-gray-100 text-gray-700'}`}>
          {value.charAt(0).toUpperCase() + value.slice(1)}
        </span>
      ),
    },
  ];

  const totalHours = timesheets.reduce((sum, ts) => sum + ts.hours, 0);
  const billableHours = timesheets.filter(ts => ts.is_billable).reduce((sum, ts) => sum + ts.hours, 0);
  const nonBillableHours = totalHours - billableHours;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Time Entries</h1>
            <p className="text-gray-600 text-sm mt-1">Track and manage your work hours</p>
          </div>
          <button
            onClick={() => handleOpenModal()}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            <Plus size={18} />
            New Entry
          </button>
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

        {/* Data Table */}
        <div className="bg-white rounded-lg shadow">
          <DataTable
            columns={tableColumns}
            data={timesheets}
            isLoading={isLoading}
            searchable={true}
            searchFields={['description']}
            onRowClick={(timesheet) => handleOpenModal(timesheet)}
            actions={[
              {
                label: 'Edit',
                onClick: (timesheet) => handleOpenModal(timesheet),
                className: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
              },
              {
                label: 'Delete',
                onClick: (timesheet) => setDeleteConfirm(timesheet.id),
                className: 'bg-red-100 text-red-700 hover:bg-red-200',
              },
            ]}
          />
        </div>

        {/* Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3">
              <Clock className="text-purple-600" size={24} />
              <div>
                <p className="text-gray-600 text-sm">Total Hours</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{totalHours.toFixed(1)}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Billable Hours</p>
            <p className="text-3xl font-bold text-green-600 mt-2">{billableHours.toFixed(1)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Non-Billable Hours</p>
            <p className="text-3xl font-bold text-orange-600 mt-2">{nonBillableHours.toFixed(1)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Billable %</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {totalHours > 0 ? ((billableHours / totalHours) * 100).toFixed(0) : 0}%
            </p>
          </div>
        </div>
      </main>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        title={editingTimesheet ? 'Edit Time Entry' : 'New Time Entry'}
        onClose={handleCloseModal}
        size="lg"
        footer={
          <>
            <button
              onClick={handleCloseModal}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              {editingTimesheet ? 'Update' : 'Create'} Entry
            </button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Project */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project *
            </label>
            <select
              name="project_id"
              value={formData.project_id}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Select a project</option>
              {projects.filter(p => p.status === 'in_progress').map(project => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date *
            </label>
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {/* Hours */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hours *
            </label>
            <input
              type="number"
              name="hours"
              value={formData.hours}
              onChange={handleInputChange}
              required
              min="0.5"
              max="24"
              step="0.5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="8.0"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="What did you work on?"
            />
          </div>

          {/* Billable Toggle */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              name="is_billable"
              checked={formData.is_billable}
              onChange={handleInputChange}
              className="w-4 h-4 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
            />
            <label className="text-sm font-medium text-gray-700">
              This work is billable to the client
            </label>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteConfirm}
        title="Delete Time Entry"
        onClose={() => setDeleteConfirm(null)}
        footer={
          <>
            <button
              onClick={() => setDeleteConfirm(null)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition"
            >
              Cancel
            </button>
            <button
              onClick={() => deleteConfirm && handleDelete(deleteConfirm)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Delete
            </button>
          </>
        }
      >
        <p className="text-gray-700">
          Are you sure you want to delete this time entry? This action cannot be undone.
        </p>
      </Modal>
    </div>
  );
};
