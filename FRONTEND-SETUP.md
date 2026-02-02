# Frontend Setup - Phase 3

## Overview

This directory is prepared for the React frontend of Votra.io. The FastAPI backend is now configured to serve static files and support single-page application (SPA) routing.

## Current Status

- ✅ Static file serving configured (`/static/` directory)
- ✅ SPA index.html available at root (`/`)
- ✅ API endpoints available at `/api/v1/*`
- ✅ API documentation at `/docs`
- ⏳ React frontend build files go here (when built)

## Directory Structure

```
static/
├── index.html          # Main HTML template for SPA
├── css/                # Stylesheets (to be populated by build)
├── js/                 # JavaScript bundles (to be populated by build)
└── assets/             # Images, fonts, etc.
```

## Next Steps

### 1. Generate React App (Choose one)

#### Using Create React App:
```bash
cd static
npx create-react-app . --template typescript
```

#### Using Vite (Recommended):
```bash
cd static
npm create vite@latest . -- --template react-ts
```

### 2. Install Frontend Dependencies

```bash
cd static
npm install react-router-dom axios zustand
```

### 3. Configure API Client

Create `src/services/api.ts`:
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 4. Build Frontend

```bash
cd static
npm run build
```

The build output should go into `static/build/` or similar, and the FastAPI app will serve it.

## Development Workflow

### Backend Development
```bash
# Terminal 1: Backend API
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs for API documentation
```

### Frontend Development
```bash
# Terminal 2: React dev server
cd static
npm start

# React dev server typically runs on http://localhost:3000
# API calls will proxy to http://localhost:8000
```

## API Integration

All API endpoints are available at `/api/v1/`:

- **Authentication**: `/api/v1/auth/*`
- **Clients**: `/api/v1/clients/*`
- **SOWs**: `/api/v1/sows/*`
- **Projects**: `/api/v1/projects/*`
- **Timesheets**: `/api/v1/timesheets/*`
- **Invoices**: `/api/v1/invoices/*`
- **Reports**: `/api/v1/reports/*`

## Security Headers

The backend enforces security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

## CORS Configuration

CORS is configured for development. Update `app/config.py` for production:

```python
cors_origins = [
    "https://votra.io",
    "https://dev.votra.io",
]
```

## Production Build

1. Build React app:
   ```bash
   cd static
   npm run build
   ```

2. Backend serves built files from `static/` directory

3. Deploy as single application with FastAPI serving both API and frontend

## Troubleshooting

### CORS Errors
- Ensure the API backend is running
- Check that requests use correct base URL (`/api/v1`)
- Verify `cors_origins` in `app/config.py`

### 404 on Refresh
- This is expected for SPA routes - the backend serves `index.html` for non-API routes
- React Router handles client-side navigation

### Static Files Not Loading
- Verify files exist in `static/` directory
- Check browser console for 404 errors
- Ensure file paths use `/static/` prefix

## Next Phase Tasks

- [ ] Initialize React project with TypeScript
- [ ] Create API client service
- [ ] Implement authentication UI (login, register)
- [ ] Build main dashboard and navigation
- [ ] Implement consulting workflow pages

