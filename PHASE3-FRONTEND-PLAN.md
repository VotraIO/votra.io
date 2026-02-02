# Phase 3: Frontend Integration - Implementation Plan

## Completed Work (Foundation Ready ✅)

### Backend API (Tasks 5.x Complete)
- ✅ **Task 5.1:** Invoice Service (9 unit tests)
- ✅ **Task 5.2:** Invoice Router (10 HTTP integration tests)
- ✅ **Task 5.3:** Reports/Analytics Router (13 HTTP integration tests)
- ✅ **All API Endpoints:** 6 core resources fully implemented (clients, sows, projects, timesheets, invoices, reports)
- ✅ **RBAC:** Role-based access control enforced across all endpoints
- ✅ **Static Files:** FastAPI configured to serve SPA from `/static/`
- ✅ **Test Coverage:** 49 critical tests passing (auth, health, invoices, reports)

## Phase 3 Tasks (Frontend Development)

### Task 6.1: Initialize React Frontend
**Status:** Not Started
**Dependencies:** Node.js 18+ installed
**Estimated Duration:** 30 minutes

#### Subtasks:
1. **Setup React Project**
   ```bash
   cd /Users/jasonmiller/GitHub/votraio/votra.io/static
   
   # Option A: Create React App (longer setup)
   npx create-react-app . --template typescript
   
   # Option B: Vite (recommended - faster, modern)
   npm create vite@latest . -- --template react-ts
   ```

2. **Install Core Dependencies**
   ```bash
   npm install react-router-dom axios zustand @tanstack/react-query
   npm install -D tailwindcss postcss autoprefixer
   ```

3. **Initialize Tailwind CSS** (optional but recommended)
   ```bash
   npx tailwindcss init -p
   ```

4. **Create Frontend Directory Structure**
   ```
   src/
   ├── components/
   │   ├── layout/
   │   │   ├── Header.tsx
   │   │   ├── Sidebar.tsx
   │   │   └── Layout.tsx
   │   ├── auth/
   │   │   ├── LoginForm.tsx
   │   │   ├── RegisterForm.tsx
   │   │   └── ProtectedRoute.tsx
   │   └── common/
   │       ├── Button.tsx
   │       ├── Card.tsx
   │       └── LoadingSpinner.tsx
   ├── pages/
   │   ├── DashboardPage.tsx
   │   ├── LoginPage.tsx
   │   ├── ClientsPage.tsx
   │   ├── ProjectsPage.tsx
   │   ├── TimesheetsPage.tsx
   │   ├── InvoicesPage.tsx
   │   └── ReportsPage.tsx
   ├── services/
   │   ├── api.ts                # Axios instance + interceptors
   │   ├── authService.ts        # Auth API calls
   │   ├── clientService.ts      # Client CRUD
   │   ├── projectService.ts     # Project CRUD
   │   ├── timesheetService.ts   # Timesheet CRUD
   │   ├── invoiceService.ts     # Invoice operations
   │   └── reportService.ts      # Reports queries
   ├── hooks/
   │   ├── useAuth.ts           # Auth state management
   │   ├── useFetch.ts          # Data fetching with error handling
   │   └── useApi.ts            # API wrapper
   ├── types/
   │   ├── index.ts             # All TypeScript types
   │   └── api.ts               # API response types
   ├── App.tsx                  # Main router setup
   └── main.tsx                 # Entry point
   ```

5. **Verify Build Output**
   ```bash
   npm run build
   # Check that build/ or dist/ directory is created with assets
   ```

#### Success Criteria:
- [ ] React project initializes successfully
- [ ] `npm start` runs dev server on port 3000
- [ ] `npm run build` creates production build
- [ ] TypeScript compiles without errors
- [ ] Tailwind CSS (if used) properly configured

---

### Task 6.2: Create API Client Service
**Status:** Not Started
**Dependencies:** Task 6.1 completed
**Estimated Duration:** 45 minutes

#### File: `static/src/services/api.ts`
```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor - add JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired - attempt refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('/api/v1/auth/refresh', { 
            refresh_token: refreshToken 
          });
          localStorage.setItem('access_token', response.data.access_token);
          // Retry original request
          return api.request(error.config!);
        } catch {
          // Refresh failed - redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### Implementation Files:
1. **authService.ts** - POST /auth/login, /auth/register, /auth/refresh
2. **clientService.ts** - GET/POST/PUT/DELETE /clients
3. **projectService.ts** - GET/POST/PUT/DELETE /projects
4. **timesheetService.ts** - GET/POST/PUT/DELETE /timesheets
5. **invoiceService.ts** - GET/POST, /invoices/{id}/send, /invoices/{id}/mark-paid
6. **reportService.ts** - GET /reports/revenue, /reports/utilization, /reports/overdue-invoices

#### Success Criteria:
- [ ] API client initialized with proper base URL
- [ ] JWT token added to all requests
- [ ] Token refresh interceptor working
- [ ] All service files created with proper TypeScript types
- [ ] No axios warnings or errors

---

### Task 6.3: Authentication UI & Flows
**Status:** Not Started
**Dependencies:** Task 6.1, 6.2 completed
**Estimated Duration:** 60 minutes

#### Components to Create:

1. **LoginForm.tsx**
   - Email and password inputs with validation
   - "Remember me" checkbox
   - Error message display
   - Loading state during submission
   - Link to register page

2. **RegisterForm.tsx**
   - Full name, email, password, confirm password inputs
   - Password strength indicator
   - Role selection dropdown
   - Terms & conditions checkbox
   - Error handling

3. **ProtectedRoute.tsx**
   - Check if user is authenticated
   - Redirect to login if not
   - Check user roles for RBAC
   - Show unauthorized message if insufficient permissions

4. **useAuth.ts (Hook)**
   - Manage auth state (user, token, loading)
   - Login/logout/register functions
   - Auto-login on app startup (from localStorage)
   - Track user roles and permissions

#### Authentication Flow:
1. User visits `/login`
2. Enters credentials → POST /auth/login
3. Receive `access_token` and `refresh_token`
4. Store tokens in localStorage
5. Redirect to dashboard
6. All API calls include Authorization header

#### Success Criteria:
- [ ] Login page functional with credentials submission
- [ ] Tokens stored securely in localStorage
- [ ] API calls include Authorization header
- [ ] Token refresh works on 401 response
- [ ] Unauthorized users redirected to login
- [ ] Protected routes check user roles

---

### Task 6.4: Dashboard & Core Navigation
**Status:** Not Started
**Dependencies:** Tasks 6.1-6.3 completed
**Estimated Duration:** 90 minutes

#### Layout Components:

1. **Header.tsx**
   - Votra.io logo/branding
   - User profile dropdown
   - Logout button
   - Breadcrumb navigation (optional)

2. **Sidebar.tsx** (or bottom nav for mobile)
   - Navigation links to all resource pages
   - Icons for visual hierarchy
   - Active link highlighting
   - Collapsible on mobile

3. **Layout.tsx**
   - Wrapper component combining Header + Sidebar + Content
   - Responsive grid layout
   - Mobile-friendly hamburger menu

#### Dashboard Page:

1. **Key Metrics (Cards)**
   - Total revenue (current month/year)
   - Billable hours ratio
   - Overdue invoices count
   - Active projects count

2. **Quick Actions**
   - Create new project
   - Start timesheet entry
   - View recent invoices

3. **Recent Activity**
   - Last 5 transactions
   - Recent project updates
   - Pending approvals

4. **Charts**
   - Revenue trend (line chart)
   - Utilization rate (bar chart)
   - Client breakdown (pie chart)

#### Page Stubs to Create:
- ClientsPage.tsx
- ProjectsPage.tsx
- TimesheetsPage.tsx
- InvoicesPage.tsx
- ReportsPage.tsx

#### Success Criteria:
- [ ] Dashboard displays key metrics
- [ ] Navigation works between pages
- [ ] Layout responsive on mobile/tablet/desktop
- [ ] User info displayed in header
- [ ] Logout function works
- [ ] Protected routes enforced

---

## Testing Strategy

### Frontend Testing (to implement after UI complete)

1. **Unit Tests** (Jest + React Testing Library)
   - Component rendering
   - Props handling
   - Event handlers

2. **Integration Tests**
   - API service calls
   - Form submissions
   - Navigation flows

3. **E2E Tests** (Cypress or Playwright)
   - Full user workflows
   - Login → Dashboard → Resource management

### Test Coverage Goals
- ≥ 80% for components
- ≥ 90% for services
- Critical paths 100%

---

## Development Workflow

### Local Development (Two Terminals)

**Terminal 1: Backend API**
```bash
cd /Users/jasonmiller/GitHub/votraio/votra.io
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# API available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Terminal 2: Frontend Dev Server**
```bash
cd /Users/jasonmiller/GitHub/votraio/votra.io/static
npm install
npm start
# React dev server at http://localhost:3000
# Automatically proxies API to http://localhost:8000
```

### Production Build

```bash
# Build frontend
cd static
npm run build

# Backend serves built files + API from single process
uvicorn app.main:app
# http://localhost:8000 serves both frontend and API
```

---

## API Endpoint Quick Reference

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Current user info

### Clients
- `GET /api/v1/clients` - List clients (paginated)
- `POST /api/v1/clients` - Create new client
- `GET /api/v1/clients/{id}` - Get client details
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Timesheets
- `GET /api/v1/timesheets` - List timesheets
- `POST /api/v1/timesheets` - Create timesheet entry
- `GET /api/v1/timesheets/{id}` - Get timesheet details
- `PUT /api/v1/timesheets/{id}` - Update timesheet
- `DELETE /api/v1/timesheets/{id}` - Delete timesheet

### Invoices
- `GET /api/v1/invoices` - List invoices
- `POST /api/v1/invoices` - Generate invoice
- `GET /api/v1/invoices/{id}` - Get invoice details
- `POST /api/v1/invoices/{id}/send` - Send invoice
- `POST /api/v1/invoices/{id}/mark-paid` - Mark invoice as paid

### Reports
- `GET /api/v1/reports/revenue` - Revenue breakdown
- `GET /api/v1/reports/utilization` - Utilization metrics
- `GET /api/v1/reports/overdue-invoices` - Overdue invoice tracking

---

## Security Considerations

1. **JWT Tokens**
   - Access token: 30 minutes validity
   - Refresh token: 7 days validity
   - Store in localStorage (httpOnly not available in browser)

2. **CORS**
   - Configured for development
   - Update for production domains in `app/config.py`

3. **Request Validation**
   - Frontend: Client-side validation with feedback
   - Backend: Server-side validation enforced
   - Never trust client data

4. **Sensitive Data**
   - Never store passwords
   - Clear tokens on logout
   - Use HTTPS in production

5. **API Security**
   - Rate limiting: 30 req/min for reads, 10/min for writes
   - RBAC enforced on backend
   - All endpoints protected by authentication

---

## Monitoring & Debugging

### Browser DevTools
- Network tab: Monitor API requests/responses
- Console: Check for errors and logs
- Application: Verify token storage

### API Documentation
- Backend: http://localhost:8000/docs (Swagger UI)
- Frontend: Network requests in DevTools

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| CORS errors | Verify backend is running, check CORS config |
| 401 Unauthorized | Token expired, check token refresh logic |
| API 404 | Verify endpoint path and backend running |
| Blank page | Check browser console for JavaScript errors |
| Tokens not persisting | Check localStorage in DevTools Application tab |

---

## Success Metrics

- [ ] React app initializes and builds successfully
- [ ] Frontend components render without console errors
- [ ] API calls working with proper authentication
- [ ] All dashboard pages load correctly
- [ ] Navigation between pages functional
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] User can login, view data, and logout
- [ ] Form validation working on client and server
- [ ] Error messages display appropriately
- [ ] No sensitive data logged or exposed

---

## Next Phase: Task 6.1 - Initialize React Frontend

Ready to begin? The next immediate step is:

```bash
cd /Users/jasonmiller/GitHub/votraio/votra.io/static
npm create vite@latest . -- --template react-ts
npm install react-router-dom axios zustand
npm run dev
```

This will take about 30 minutes and give us a working React dev environment ready for Task 6.2 (API Client Service).

