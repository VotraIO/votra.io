import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Search } from 'lucide-react';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: any, item: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  onRowClick?: (item: T) => void;
  searchable?: boolean;
  searchFields?: (keyof T)[];
  actions?: {
    label: string;
    onClick: (item: T) => void;
    className?: string;
  }[];
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  };
}

export const DataTable = React.forwardRef<HTMLDivElement, DataTableProps<any>>(
  (
    {
      columns,
      data,
      isLoading = false,
      onRowClick,
      searchable = false,
      searchFields = [],
      actions = [],
      pagination,
    },
    ref
  ) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

    // Filter data based on search term
    const filteredData = searchable && searchTerm && searchFields.length > 0
      ? data.filter(item =>
          searchFields.some(field => {
            const value = item[field];
            return value?.toString().toLowerCase().includes(searchTerm.toLowerCase());
          })
        )
      : data;

    // Sort data
    const sortedData = sortKey
      ? [...filteredData].sort((a, b) => {
          const aVal = a[sortKey as keyof typeof a];
          const bVal = b[sortKey as keyof typeof b];
          const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
          return sortOrder === 'asc' ? comparison : -comparison;
        })
      : filteredData;

    const handleSort = (key: string) => {
      if (sortKey === key) {
        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
      } else {
        setSortKey(key);
        setSortOrder('asc');
      }
    };

    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      );
    }

    return (
      <div ref={ref} className="space-y-4">
        {/* Search Bar */}
        {searchable && (
          <div className="flex items-center gap-2">
            <Search size={18} className="text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto border border-gray-200 rounded-lg">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {columns.map(column => (
                  <th
                    key={String(column.key)}
                    className="px-6 py-3 text-left text-sm font-semibold text-gray-700"
                    onClick={() => column.sortable && handleSort(String(column.key))}
                    style={column.width ? { width: column.width } : {}}
                  >
                    <div className="flex items-center gap-2 cursor-pointer hover:text-purple-600">
                      <span>{column.label}</span>
                      {column.sortable && sortKey === String(column.key) && (
                        <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                ))}
                {actions.length > 0 && (
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Actions
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {sortedData.length === 0 ? (
                <tr>
                  <td colSpan={columns.length + (actions.length > 0 ? 1 : 0)} className="px-6 py-8 text-center text-gray-500">
                    No data available
                  </td>
                </tr>
              ) : (
                sortedData.map((item, index) => (
                  <tr
                    key={index}
                    className="border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition"
                    onClick={() => onRowClick?.(item)}
                  >
                    {columns.map(column => (
                      <td key={String(column.key)} className="px-6 py-4 text-sm text-gray-900">
                        {column.render
                          ? column.render(item[column.key], item)
                          : String(item[column.key] || '-')}
                      </td>
                    ))}
                    {actions.length > 0 && (
                      <td className="px-6 py-4 text-sm space-x-2 flex">
                        {actions.map((action, idx) => (
                          <button
                            key={idx}
                            onClick={(e) => {
                              e.stopPropagation();
                              action.onClick(item);
                            }}
                            className={`px-3 py-1 rounded text-xs font-medium transition ${
                              action.className ||
                              'bg-blue-100 text-blue-700 hover:bg-blue-200'
                            }`}
                          >
                            {action.label}
                          </button>
                        ))}
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              Page {pagination.currentPage} of {pagination.totalPages}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
                disabled={pagination.currentPage === 1}
                className="p-2 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={18} />
              </button>
              <button
                onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
                disabled={pagination.currentPage === pagination.totalPages}
                className="p-2 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }
);

DataTable.displayName = 'DataTable';
