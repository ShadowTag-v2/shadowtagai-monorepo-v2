# Frontend Development Guidelines

**Purpose:** Enforce React 19 + TypeScript + TanStack patterns for ShadowTagAi frontends
**Enforcement:** `"suggest"`
**Priority:** `"high"`
**Version:** 1.0.0

---

## Overview

This skill provides best practices for building modern, performant React applications using ShadowTagAi's frontend stack.

**Tech Stack:**
- **Framework:** React 19 with TypeScript 5+
- **Data Fetching:** TanStack Query v5
- **Routing:** TanStack Router
- **UI Components:** MUI v7 (Material-UI)
- **Forms:** React Hook Form + Zod validation
- **Package Manager:** pnpm
- **Build Tool:** Vite

---

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── common/       # Shared across app (Button, Input, etc.)
│   │   └── features/     # Feature-specific components
│   ├── pages/            # Route components
│   │   ├── Dashboard.tsx
│   │   └── Settings.tsx
│   ├── hooks/            # Custom React hooks
│   │   └── useAuth.ts
│   ├── services/         # API clients
│   │   └── api.ts
│   ├── types/            # TypeScript interfaces
│   │   └── user.types.ts
│   ├── utils/            # Helper functions
│   │   └── formatDate.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## Component Patterns

### Functional Components (TypeScript)

```typescript
// src/components/UserCard.tsx
import { FC } from 'react';
import { Card, CardContent, Typography } from '@mui/material';

interface UserCardProps {
  userId: string;
  name: string;
  email: string;
  onEdit?: () => void;
}

export const UserCard: FC<UserCardProps> = ({ userId, name, email, onEdit }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{name}</Typography>
        <Typography variant="body2" color="text.secondary">
          {email}
        </Typography>
        {onEdit && (
          <Button onClick={onEdit} variant="outlined">
            Edit
          </Button>
        )}
      </CardContent>
    </Card>
  );
};
```

---

## Data Fetching (TanStack Query)

### API Client Setup

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Query Hooks

```typescript
// src/hooks/useUser.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { User } from '../types/user.types';

export const useUser = (userId: string) => {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const { data } = await api.get<User>(`/users/${userId}`);
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000 // 10 minutes (formerly cacheTime)
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, updates }: { userId: string; updates: Partial<User> }) => {
      const { data } = await api.put<User>(`/users/${userId}`, updates);
      return data;
    },
    onSuccess: (data) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['user', data.id] });
    }
  });
};
```

### Usage in Component

```typescript
// src/pages/UserProfile.tsx
import { FC } from 'react';
import { useParams } from '@tanstack/react-router';
import { useUser, useUpdateUser } from '../hooks/useUser';
import { CircularProgress, Alert } from '@mui/material';

export const UserProfile: FC = () => {
  const { userId } = useParams({ from: '/users/$userId' });
  const { data: user, isLoading, error } = useUser(userId);
  const updateUser = useUpdateUser();

  if (isLoading) return <CircularProgress />;
  if (error) return <Alert severity="error">Failed to load user</Alert>;
  if (!user) return <Alert severity="info">User not found</Alert>;

  const handleUpdate = async () => {
    await updateUser.mutateAsync({
      userId: user.id,
      updates: { name: 'New Name' }
    });
  };

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <Button onClick={handleUpdate}>Update</Button>
    </div>
  );
};
```

---

## Form Handling

### React Hook Form + Zod

```typescript
// src/components/RegisterForm.tsx
import { FC } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { TextField, Button, Box } from '@mui/material';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  name: z.string().min(2, 'Name must be at least 2 characters')
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterForm: FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema)
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await api.post('/users/register', data);
      // Handle success (redirect, show message, etc.)
    } catch (error) {
      // Handle error
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ maxWidth: 400 }}>
      <TextField
        {...register('email')}
        label="Email"
        type="email"
        fullWidth
        margin="normal"
        error={!!errors.email}
        helperText={errors.email?.message}
      />

      <TextField
        {...register('password')}
        label="Password"
        type="password"
        fullWidth
        margin="normal"
        error={!!errors.password}
        helperText={errors.password?.message}
      />

      <TextField
        {...register('name')}
        label="Name"
        fullWidth
        margin="normal"
        error={!!errors.name}
        helperText={errors.name?.message}
      />

      <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
        Register
      </Button>
    </Box>
  );
};
```

---

## State Management

### React Context (for Global State)

```typescript
// src/context/AuthContext.tsx
import { createContext, useContext, useState, FC, ReactNode } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const { data } = await api.post('/auth/login', { email, password });
    setUser(data.user);
    localStorage.setItem('authToken', data.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('authToken');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## Routing (TanStack Router)

```typescript
// src/routes.tsx
import { createRootRoute, createRoute, createRouter } from '@tanstack/react-router';
import { Dashboard } from './pages/Dashboard';
import { UserProfile } from './pages/UserProfile';
import { Settings } from './pages/Settings';

const rootRoute = createRootRoute();

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: Dashboard
});

const userRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/users/$userId',
  component: UserProfile
});

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: Settings
});

const routeTree = rootRoute.addChildren([indexRoute, userRoute, settingsRoute]);

export const router = createRouter({ routeTree });
```

---

## MUI Theming

```typescript
// src/theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2'
    },
    secondary: {
      main: '#dc004e'
    }
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif'
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none' // Disable uppercase
        }
      }
    }
  }
});

// src/App.tsx
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from './theme';

export const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Your app */}
    </ThemeProvider>
  );
};
```

---

## Testing

```typescript
// src/components/__tests__/UserCard.test.tsx
import { render, screen } from '@testing-library/react';
import { UserCard } from '../UserCard';

describe('UserCard', () => {
  it('renders user information', () => {
    render(
      <UserCard
        userId="123"
        name="John Doe"
        email="john@example.com"
      />
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('shows edit button when onEdit provided', () => {
    const handleEdit = jest.fn();

    render(
      <UserCard
        userId="123"
        name="John Doe"
        email="john@example.com"
        onEdit={handleEdit}
      />
    );

    const editButton = screen.getByRole('button', { name: /edit/i });
    expect(editButton).toBeInTheDocument();
  });
});
```

---

## Best Practices Checklist

- [ ] Use TypeScript strict mode
- [ ] All components are functional (no class components)
- [ ] Use TanStack Query for server state
- [ ] Use React Context for global client state
- [ ] Form validation with Zod
- [ ] Error boundaries for graceful error handling
- [ ] Loading states for async operations
- [ ] Responsive design (mobile-first)
- [ ] Accessibility (ARIA labels, keyboard navigation)
- [ ] Test coverage ≥98%
- [ ] Use pnpm (not npm/yarn)

---

**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi Frontend Team
**Stack:** React 19 + TypeScript 5 + TanStack + MUI v7 + Vite