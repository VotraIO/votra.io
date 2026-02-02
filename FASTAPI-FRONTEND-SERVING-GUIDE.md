# FastAPI Frontend Serving Integration Guide

**Purpose**: Configure FastAPI to serve both API and frontend (React/Vue SPA) from a single application instance - **no separate web server infrastructure needed**.

---

## Architecture

```
Browser Request
      ↓
FastAPI Application (Single Instance)
├── /api/v1/* → JSON API Responses
├── /static/* → Static Files (CSS, JS, Images)
└── /* → SPA index.html (Browser Routing)
      ↓
PostgreSQL Database
```

---

## Key Benefits

1. ✅ **Single Deployment**: One Docker container, one process
2. ✅ **No Extra Infrastructure**: No nginx, no separate frontend server
3. ✅ **Shared Sessions**: Frontend and API share JWT authentication
4. ✅ **CORS Built-in**: No cross-origin issues
5. ✅ **Easy Development**: Frontend and backend together
6. ✅ **Cost Effective**: Minimal infrastructure overhead

---

## Implementation

### Step 1: Update app/main.py

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Votra.io API",
    description="Consulting Business Portal",
    version="0.1.0"
)

# === MIDDLEWARE SETUP ===
# CORS, rate limiting, security headers
# (existing setup remains the same)

# === API ROUTERS ===
# Include all your API routers
from app.routers import auth, health, clients, sows, projects, timesheets, invoices

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(clients.router)
app.include_router(sows.router)
app.include_router(projects.router)
app.include_router(timesheets.router)
app.include_router(invoices.router)

# === STATIC FILES SETUP ===
# Serve frontend SPA

static_dir = Path(__file__).parent.parent / "static" / "build"

# Mount static files (CSS, JS, images)
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# === SPA ROUTING ===
# Serve index.html for all non-API routes
# This enables React Router, Vue Router, etc. to work correctly

@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """
    Serve SPA index.html for all non-API routes.
    
    This enables client-side routing in React/Vue/Angular.
    
    Routes that should NOT be handled here:
    - /api/* → Handled by API routers
    - /docs, /openapi.json → FastAPI automatic docs
    - /static/* → Handled by StaticFiles mount
    
    Everything else gets index.html, letting the SPA handle routing.
    """
    
    # Don't interfere with API routes
    if full_path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": f"API route not found: /{full_path}"}
        )
    
    # Don't interfere with FastAPI docs
    if full_path.startswith("docs") or full_path.startswith("openapi.json"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )
    
    # Serve index.html for SPA routing
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    # If no static files, return 404
    return JSONResponse(
        status_code=404,
        content={"detail": "Frontend not available"}
    )
```

### Step 2: Frontend Build Configuration

**Setup in static/ directory**:

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Output: static/build/ → served by FastAPI
```

**package.json configuration** (for React with Vite):

```json
{
  "name": "votra-io-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.18.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

**vite.config.ts**:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'build',  // Output to build/ (FastAPI will serve this)
    sourcemap: false, // Disable for production
  },
  server: {
    proxy: {
      // During development, proxy API calls to FastAPI
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### Step 3: Directory Structure

```
votra.io/
├── app/
│   ├── main.py                 # ← Modified for SPA serving
│   ├── config.py
│   ├── dependencies.py
│   ├── database/
│   ├── models/
│   ├── routers/                # All API endpoints
│   ├── services/
│   ├── utils/
│   └── __init__.py
│
├── static/                      # ← Frontend root
│   ├── src/                     # React source code
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.ts          # API client (see below)
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   └── favicon.ico
│   ├── index.html              # React entry point
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── build/                  # ← Generated by npm run build (served by FastAPI)
│       ├── index.html
│       ├── assets/
│       │   ├── index-*.js
│       │   └── index-*.css
│       └── favicon.ico
│
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

### Step 4: Frontend API Client

**Create static/src/services/api.ts**:

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

// Determine API base URL based on environment
const API_BASE_URL = (() => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Production: same origin, /api path
  if (process.env.NODE_ENV === 'production') {
    return '/api/v1';
  }
  
  // Development: proxy to localhost:8000
  return 'http://localhost:8000/api/v1';
})();

class ApiClient {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Include cookies if using session auth
    });
    
    // Request interceptor: Add JWT token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    // Response interceptor: Handle errors
    this.client.interceptors.response.use(
      response => response,
      async (error: AxiosError) => {
        // Handle 401 Unauthorized (token expired)
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          
          // Redirect to login
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
        
        // Handle other errors
        return Promise.reject(error);
      }
    );
  }
  
  // === Auth Endpoints ===
  
  login = (email: string, password: string) =>
    this.client.post('/auth/login', { email, password });
  
  register = (email: string, username: string, password: string, fullName?: string) =>
    this.client.post('/auth/register', {
      email,
      username,
      password,
      full_name: fullName,
    });
  
  refreshToken = (refreshToken: string) =>
    this.client.post('/auth/refresh', { refresh_token: refreshToken });
  
  getCurrentUser = () =>
    this.client.get('/auth/me');
  
  // === Client Endpoints ===
  
  getClients = (page = 1, perPage = 20) =>
    this.client.get('/clients', { params: { page, per_page: perPage } });
  
  getClient = (id: number) =>
    this.client.get(`/clients/${id}`);
  
  createClient = (data: ClientData) =>
    this.client.post('/clients', data);
  
  updateClient = (id: number, data: Partial<ClientData>) =>
    this.client.put(`/clients/${id}`, data);
  
  deleteClient = (id: number) =>
    this.client.delete(`/clients/${id}`);
  
  // === SOW Endpoints ===
  
  getSOWs = (status?: string, clientId?: number, page = 1, perPage = 20) =>
    this.client.get('/sows', {
      params: { status, client_id: clientId, page, per_page: perPage }
    });
  
  getSOW = (id: number) =>
    this.client.get(`/sows/${id}`);
  
  createSOW = (data: SOWData) =>
    this.client.post('/sows', data);
  
  updateSOW = (id: number, data: Partial<SOWData>) =>
    this.client.put(`/sows/${id}`, data);
  
  submitSOW = (id: number) =>
    this.client.post(`/sows/${id}/submit`);
  
  approveSOW = (id: number, approved: boolean, notes?: string) =>
    this.client.post(`/sows/${id}/approve`, { approved, notes });
  
  // === Project Endpoints ===
  
  getProjects = (page = 1, perPage = 20) =>
    this.client.get('/projects', { params: { page, per_page: perPage } });
  
  getProject = (id: number) =>
    this.client.get(`/projects/${id}`);
  
  createProject = (data: ProjectData) =>
    this.client.post('/projects', data);
  
  updateProject = (id: number, data: Partial<ProjectData>) =>
    this.client.put(`/projects/${id}`, data);
  
  closeProject = (id: number) =>
    this.client.post(`/projects/${id}/close`);
  
  // === Timesheet Endpoints ===
  
  getTimesheets = (
    projectId?: number,
    consultantId?: number,
    dateFrom?: string,
    dateTo?: string,
    page = 1,
    perPage = 20
  ) =>
    this.client.get('/timesheets', {
      params: {
        project_id: projectId,
        consultant_id: consultantId,
        date_from: dateFrom,
        date_to: dateTo,
        page,
        per_page: perPage,
      }
    });
  
  getTimesheet = (id: number) =>
    this.client.get(`/timesheets/${id}`);
  
  createTimesheet = (data: TimesheetData) =>
    this.client.post('/timesheets', data);
  
  updateTimesheet = (id: number, data: Partial<TimesheetData>) =>
    this.client.put(`/timesheets/${id}`, data);
  
  approveTimesheet = (id: number) =>
    this.client.post(`/timesheets/${id}/approve`);
  
  rejectTimesheet = (id: number, reason?: string) =>
    this.client.post(`/timesheets/${id}/reject`, { reason });
  
  // === Invoice Endpoints ===
  
  getInvoices = (status?: string, clientId?: number, page = 1, perPage = 20) =>
    this.client.get('/invoices', {
      params: { status, client_id: clientId, page, per_page: perPage }
    });
  
  getInvoice = (id: number) =>
    this.client.get(`/invoices/${id}`);
  
  createInvoice = (projectId: number, invoiceDate: string) =>
    this.client.post('/invoices', { project_id: projectId, invoice_date: invoiceDate });
  
  sendInvoice = (id: number) =>
    this.client.post(`/invoices/${id}/send`);
  
  markInvoicePaid = (id: number, paymentDate: string) =>
    this.client.post(`/invoices/${id}/mark-paid`, { payment_date: paymentDate });
}

export default new ApiClient();

// === Type Definitions ===

export interface ClientData {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  billing_address?: string;
  payment_terms?: number;
}

export interface SOWData {
  client_id: number;
  title: string;
  description?: string;
  start_date: string;
  end_date: string;
  rate: number;
  total_budget: number;
}

export interface ProjectData {
  sow_id: number;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  budget: number;
}

export interface TimesheetData {
  project_id: number;
  work_date: string;
  hours_logged: number;
  billing_rate: number;
  is_billable?: boolean;
  notes?: string;
}
```

### Step 5: React Router Configuration

**Create static/src/App.tsx**:

```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import SOWList from './pages/SOWs/SOWList';
import SOWDetail from './pages/SOWs/SOWDetail';
import ProjectList from './pages/Projects/ProjectList';
import TimesheetList from './pages/Timesheets/TimesheetList';
import InvoiceList from './pages/Invoices/InvoiceList';
import Layout from './components/Layout/Layout';

interface ProtectedRouteProps {
  component: React.ReactComponent;
}

const ProtectedRoute = ({ component: Component }: ProtectedRouteProps) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  
  return user ? <Component /> : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Protected Routes */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<ProtectedRoute component={Dashboard} />} />
          <Route path="/sows" element={<ProtectedRoute component={SOWList} />} />
          <Route path="/sows/:id" element={<ProtectedRoute component={SOWDetail} />} />
          <Route path="/projects" element={<ProtectedRoute component={ProjectList} />} />
          <Route path="/timesheets" element={<ProtectedRoute component={TimesheetList} />} />
          <Route path="/invoices" element={<ProtectedRoute component={InvoiceList} />} />
        </Route>
        
        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}

export default App;
```

---

## Development Workflow

### 1. Local Development Setup

**Terminal 1 - Backend**:
```bash
# Start FastAPI (serves API + frontend on localhost:8000)
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend Dev Server**:
```bash
cd static
npm run dev
# Runs on localhost:5173 with Vite dev server
# Proxies /api/* to localhost:8000 (see vite.config.ts)
```

### 2. Build and Run Together

```bash
# Build frontend
cd static
npm run build
cd ..

# Start FastAPI (serves both API and built frontend)
uvicorn app.main:app --reload
# Access at http://localhost:8000
```

### 3. Docker Deployment

**Dockerfile** (single-stage for simplicity):

```dockerfile
# Build stage would go here in multi-stage build
# For MVP, we'll keep it simple

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy backend
COPY app ./app

# Copy built frontend
COPY static/build ./static/build

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Run**:

```bash
# Build frontend first
cd static
npm run build
cd ..

# Build Docker image
docker build -t votra-io:latest .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/votraio" \
  -e SECRET_KEY="your-secret-key-here" \
  votra-io:latest
```

---

## Production Considerations

### 1. Static File Caching

```python
# app/main.py
from fastapi.staticfiles import StaticFiles

app.mount(
    "/static",
    StaticFiles(directory=static_dir, check_dir=False),
    name="static"
)

# Add cache headers for static files
@app.get("/static/{full_path:path}")
async def serve_static(full_path: str):
    # Serve with cache headers
    pass
```

### 2. Compression

```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

### 3. CORS for Production

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votra.io"],  # Not ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Security Headers

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## Troubleshooting

### Issue: Frontend not loading (404)

**Solution**: Ensure `static/build/` exists:
```bash
cd static
npm run build
cd ..
# Then start FastAPI
```

### Issue: API calls failing (CORS error)

**Solution**: Check that API client uses correct base URL:
```typescript
// In production, should be '/api/v1'
// In development, should proxy to localhost:8000
```

### Issue: Browser showing old content

**Solution**: Clear browser cache and rebuild:
```bash
cd static
rm -rf build/
npm run build
# Then refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
```

### Issue: JWT token not sent in requests

**Solution**: Ensure API client includes auth header:
```typescript
// Check that interceptor is adding Authorization header
const token = localStorage.getItem('access_token');
if (token) {
  config.headers.Authorization = `Bearer ${token}`;
}
```

---

## Summary

With this setup:

✅ **Single FastAPI instance** serves both API and frontend
✅ **No separate infrastructure** needed
✅ **Easy development** with hot reload for both backend and frontend
✅ **Simple deployment** - one Docker container
✅ **Unified authentication** via JWT
✅ **Client-side routing** works via SPA catch-all route

This is the MVP-appropriate solution for serving frontend from FastAPI without additional infrastructure complexity.
