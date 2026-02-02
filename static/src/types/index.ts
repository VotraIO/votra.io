// API Response Types
export interface ApiResponse<T> {
  data: T;
  message: string;
  status: number;
}

// Authentication
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role: 'admin' | 'project_manager' | 'consultant' | 'client' | 'accountant';
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

// Client
export interface Client {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  address: string | null;
  industry: string | null;
  contact_person: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate extends Omit<Client, 'id' | 'created_at' | 'updated_at'> {}
export interface ClientUpdate extends Partial<ClientCreate> {}

// Project
export interface Project {
  id: string;
  client_id: string;
  name: string;
  description: string | null;
  status: 'planning' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled';
  start_date: string;
  end_date: string | null;
  budget: number | null;
  actual_cost: number | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate extends Omit<Project, 'id' | 'created_at' | 'updated_at' | 'actual_cost'> {}
export interface ProjectUpdate extends Partial<ProjectCreate> {}

// Timesheet
export interface Timesheet {
  id: string;
  project_id: string;
  user_id: string;
  date: string;
  hours: number;
  description: string | null;
  is_billable: boolean;
  rate_per_hour: number | null;
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface TimesheetCreate extends Omit<Timesheet, 'id' | 'created_at' | 'updated_at'> {}
export interface TimesheetUpdate extends Partial<TimesheetCreate> {}

// Invoice
export interface Invoice {
  id: string;
  invoice_number: string;
  client_id: string;
  project_id: string | null;
  total_amount: number;
  tax_amount: number;
  net_amount: number;
  status: 'draft' | 'sent' | 'viewed' | 'paid' | 'overdue' | 'cancelled';
  issue_date: string;
  due_date: string;
  paid_date: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface InvoiceCreate extends Omit<Invoice, 'id' | 'invoice_number' | 'created_at' | 'updated_at'> {}

// Reports
export interface RevenueReport {
  period: string;
  client_name: string;
  total_revenue: number;
  tax_amount: number;
  net_revenue: number;
  invoice_count: number;
}

export interface UtilizationReport {
  period: string;
  consultant_name: string;
  billable_hours: number;
  non_billable_hours: number;
  total_hours: number;
  utilization_rate: number;
}

export interface OverdueInvoice {
  invoice_id: string;
  invoice_number: string;
  client_name: string;
  amount: number;
  due_date: string;
  days_overdue: number;
  status: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
