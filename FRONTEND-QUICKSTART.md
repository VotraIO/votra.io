# React Frontend - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Node.js 18+ and npm 11+
- Backend running on `http://localhost:8000`

### Start Frontend Dev Server

```bash
cd static
npm run dev
```

Opens browser at `http://localhost:5173`

### Login with Demo Account
- **Username**: `admin`
- **Password**: `SecurePass123!`

That's it! You now have:
- ✅ Working React app
- ✅ Connected to backend API
- ✅ Dashboard with metrics
- ✅ JWT authentication

---

## 📁 Project Structure

### Key Files
```
static/src/
├── App.tsx                    # Main router
├── pages/
│   ├── LoginPage.tsx         # Login form
│   ├── DashboardPage.tsx     # Dashboard with metrics
│   └── index.tsx             # Other pages
├── services/
│   └── api.ts                # API client (Axios)
├── hooks/
│   └── useAuth.ts            # Auth state management
├── components/
│   └── auth/
│       └── ProtectedRoute.tsx # Protected route wrapper
└── types/
    └── index.ts              # TypeScript definitions
```

---

## 🔧 Common Commands

### Development
```bash
npm run dev          # Start dev server on port 5173
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Check TypeScript + ESLint
```

### Debugging
```bash
# Open DevTools (F12 in browser)
# - Network: Monitor API calls
# - Console: View logs and errors
# - Storage: Check tokens in localStorage
```

---

## 🔌 API Integration

### Using API Services

```typescript
import { clientService, authService } from '../services/api';

// Get clients
const { data } = await clientService.list({ page: 1, page_size: 10 });

// Create invoice
const invoice = await invoiceService.create({
  client_id: 'abc123',
  total_amount: 1000,
  // ... other fields
});

// Get reports
const reports = await reportService.revenueReport({
  start_date: '2024-01-01',
  end_date: '2024-12-31'
});
```

### Authentication Flow

```typescript
import { useAuth } from '../hooks/useAuth';

const MyComponent = () => {
  const { user, login, logout, isAuthenticated } = useAuth();
  
  // Use in component
  if (!isAuthenticated) {
    return <Redirect to="/login" />;
  }
  
  return <div>Welcome, {user?.full_name}!</div>;
};
```

---

## 🎨 Tailwind CSS

### Example Components

```typescript
// Button
<button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
  Click me
</button>

// Card
<div className="bg-white rounded-lg shadow p-6">
  <h2 className="text-lg font-bold">Title</h2>
</div>

// Grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {items.map(item => <Item key={item.id} {...item} />)}
</div>

// Form
<form className="space-y-4">
  <input className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" />
  <button type="submit">Submit</button>
</form>
```

---

## 🧪 Testing

### Run Tests (when implemented)
```bash
npm run test          # Run Vitest
npm run test:ui       # UI mode
npm run test:coverage # Coverage report
```

### Test Example
```typescript
import { render, screen } from '@testing-library/react';
import { LoginPage } from '../pages/LoginPage';

test('renders login form', () => {
  render(<LoginPage />);
  expect(screen.getByText('Login')).toBeInTheDocument();
});
```

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to API"
**Solution**: Ensure backend is running on `http://localhost:8000`
```bash
cd ..
uvicorn app.main:app --reload
```

### Issue: "401 Unauthorized on every request"
**Solution**: Check localStorage for tokens
```javascript
// In browser console:
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
```

### Issue: "Blank page or white screen"
**Solution**: Check browser console for errors (F12 → Console tab)

### Issue: "Hot reload not working"
**Solution**: Restart dev server
```bash
npm run dev
```

### Issue: "TypeScript errors"
**Solution**: Run type check
```bash
npx tsc --noEmit
```

---

## 📦 Adding Dependencies

```bash
# Install package
npm install package-name

# Install as dev dependency
npm install --save-dev package-name

# Install specific version
npm install package-name@1.2.3

# Update all packages
npm update
```

### Recommended Packages
- `react-table` - Advanced tables
- `react-hook-form` - Form handling
- `zod` - Data validation
- `recharts` - Charts and graphs
- `date-fns` - Date utilities

---

## 🔐 Environment Variables

Create `static/.env.local`:
```env
REACT_APP_API_URL=/api/v1
REACT_APP_ENV=development
```

Access in code:
```typescript
const apiUrl = import.meta.env.REACT_APP_API_URL;
const env = import.meta.env.REACT_APP_ENV;
```

---

## 📝 Adding New Pages

### 1. Create Page Component
```typescript
// src/pages/NewPage.tsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';

export const NewPage: React.FC = () => {
  const { user } = useAuth();
  
  return (
    <div>
      <h1>New Page</h1>
      <p>Welcome, {user?.full_name}!</p>
    </div>
  );
};
```

### 2. Add to Router
```typescript
// App.tsx
import { NewPage } from './pages/NewPage';

<Route
  path="/new-page"
  element={
    <ProtectedRoute
      isAuthenticated={isAuthenticated}
      isLoading={isLoading}
    >
      <NewPage />
    </ProtectedRoute>
  }
/>
```

### 3. Add Navigation Link
```typescript
// DashboardPage.tsx
<Link to="/new-page">Go to New Page</Link>
```

---

## 🎯 Best Practices

### Component Structure
```typescript
import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

interface Props {
  id: string;
  onClose: () => void;
}

export const MyComponent: React.FC<Props> = ({ id, onClose }) => {
  const [data, setData] = useState(null);
  const { user } = useAuth();

  return (
    <div className="p-6">
      {/* Component content */}
    </div>
  );
};
```

### API Calls
```typescript
import { useEffect, useState } from 'react';
import { clientService } from '../services/api';

export const ClientList: React.FC = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const { data } = await clientService.list();
        setClients(data.items);
      } catch (err) {
        setError('Failed to load clients');
      } finally {
        setLoading(false);
      }
    };
    
    fetchClients();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  
  return (
    <div>
      {clients.map(client => (
        <div key={client.id}>{client.name}</div>
      ))}
    </div>
  );
};
```

---

## 🚢 Production Build

### Build
```bash
npm run build
```

### Output
- Optimized JavaScript bundles
- CSS minified
- Assets optimized
- Build time: ~10-30 seconds

### Deploy
1. Build frontend: `npm run build`
2. Backend serves built files from `/static/dist`
3. Single command to run: `uvicorn app.main:app`

---

## 📚 Resources

- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Axios Docs](https://axios-http.com)
- [Vite Docs](https://vitejs.dev)

---

## 💡 Tips

1. **Use React DevTools**: Browser extension for debugging
2. **Use TypeScript**: Strict mode catches errors early
3. **Component Testing**: Write tests as you build
4. **Performance**: Use React.memo for expensive renders
5. **Code Splitting**: Use lazy routes for large apps

---

## 🆘 Getting Help

Check:
1. Browser console (F12)
2. Network tab (API calls)
3. Backend logs
4. GitHub issues
5. Backend API docs: http://localhost:8000/docs

---

## Next Steps

1. ✅ Frontend running
2. ✅ Login working
3. ✅ Dashboard showing
4. ⏳ Build resource management pages (Task 6.2)
5. ⏳ Add charts and analytics (Task 6.3)
6. ⏳ Advanced features and testing (Task 6.4+)

Happy coding! 🎉
