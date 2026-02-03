// Export all page components
export { ClientsPage } from './ClientsPage';
export { ProjectsPage } from './ProjectsPage';
export { TimesheetsPage } from './TimesheetsPage';
export { InvoicesPage } from './InvoicesPage';
export { ReportsPage } from './ReportsPage';
export { DashboardPage } from './DashboardPage';
export { LoginPage } from './LoginPage';

export const ReportsPage: React.FC = () => (
  <PlaceholderPage title="Reports" description="View revenue, utilization, and analytics." />
);
