# Frontend Implementation Guide

## Overview
This document provides a complete guide to implementing all missing frontend components for the RAG System according to the specification in `rag_system_prompt_v2.md`.

## Implementation Status

### ✅ Completed
- TypeScript types (enhanced types/index.ts)
- Utility functions (formatters.ts, validators.ts, constants.ts)
- Basic project structure
- API service setup
- Basic pages (stubs)

### 🚧 In Progress / To Complete
All components listed below need to be implemented.

---

## Directory Structure

```
frontend/src/
├── components/
│   ├── common/           # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Badge.tsx
│   │   ├── Spinner.tsx
│   │   ├── Modal.tsx
│   │   ├── Tabs.tsx
│   │   ├── Table.tsx
│   │   ├── Toast.tsx
│   │   └── StatusIndicator.tsx
│   │
│   ├── layout/           # Layout components
│   │   ├── Header.tsx
│   │   └── MainLayout.tsx
│   │
│   ├── documents/        # Document page components
│   │   ├── DocumentList.tsx
│   │   ├── DocumentCard.tsx
│   │   ├── DocumentDetails.tsx
│   │   ├── UploadModal.tsx
│   │   ├── ChunksViewer.tsx
│   │   └── DocumentFilters.tsx
│   │
│   ├── query/            # Query page components
│   │   ├── QueryInput.tsx
│   │   ├── AnswerDisplay.tsx
│   │   ├── DebugPanel.tsx
│   │   ├── ChunksList.tsx
│   │   ├── RerankComparison.tsx
│   │   ├── AgentDecision.tsx
│   │   ├── SearchSources.tsx
│   │   └── TimingBreakdown.tsx
│   │
│   └── settings/         # Settings page components
│       ├── AzureConfig.tsx
│       ├── RAGConfig.tsx
│       └── SystemStatus.tsx
│
├── hooks/                # Custom React hooks
│   ├── useApi.ts        # ✅ Exists
│   ├── useDocuments.ts
│   ├── useQuery.ts
│   ├── useSettings.ts
│   ├── useToast.ts
│   └── useDebounce.ts
│
├── store/                # Zustand stores
│   ├── documentStore.ts
│   ├── queryStore.ts
│   ├── settingsStore.ts
│   └── toastStore.ts
│
├── services/             # API services
│   ├── api.ts           # ✅ Exists (needs enhancement)
│   ├── client.ts
│   ├── documents.ts
│   ├── queries.ts
│   └── settings.ts
│
├── utils/                # Utility functions
│   ├── formatters.ts    # ✅ Created
│   ├── validators.ts    # ✅ Created
│   └── constants.ts     # ✅ Created
│
├── types/                # TypeScript types
│   └── index.ts         # ✅ Enhanced
│
└── pages/                # Main page components
    ├── Documents.tsx    # Needs completion
    ├── Query.tsx        # Needs completion
    └── Settings.tsx     # Needs completion
```

---

## Implementation Priority

Given the large scope, implement in this order:

### Phase 1: Foundation (✅ DONE)
- Types
- Utils
- Constants

### Phase 2: Core Infrastructure (HIGH PRIORITY)
1. **Zustand Stores** - State management foundation
2. **API Layer** - Enhanced client with interceptors
3. **Common Components** - Building blocks for all pages
4. **Custom Hooks** - Business logic abstraction

### Phase 3: Settings Page (MEDIUM PRIORITY)
- SystemStatus component (shows health)
- AzureConfig component
- RAGConfig component
- Complete Settings page

### Phase 4: Documents Page (MEDIUM PRIORITY)
- DocumentList with table
- UploadModal with drag-drop
- DocumentDetails modal
- ChunksViewer modal
- DocumentFilters

### Phase 5: Query Page (HIGH PRIORITY - Most Complex)
- QueryInput
- AnswerDisplay with citations
- DebugPanel with iteration tabs
- ChunksList
- RerankComparison
- AgentDecision display
- SearchSources bar chart
- TimingBreakdown chart

---

## Quick Implementation Guide

### To implement the remaining components:

1. **Start with stores** (Phase 2.1):
   - `toastStore.ts` - Simple notification system
   - `settingsStore.ts` - App configuration
   - `documentStore.ts` - Document management
   - `queryStore.ts` - Query execution state

2. **Build common components** (Phase 2.3):
   - Start with Button, Card, Input, Spinner (most used)
   - Then Badge, Modal, Tabs
   - Finally Table, Toast, StatusIndicator

3. **Create hooks** (Phase 2.4):
   - `useToast` - Toast notifications
   - `useDebounce` - Input debouncing
   - `useDocuments` - Document CRUD operations
   - `useQuery` - Query execution
   - `useSettings` - Settings management

4. **Enhance API layer** (Phase 2.2):
   - Create separate API modules for documents, queries, settings
   - Add interceptors for auth, errors, loading states

5. **Complete Settings page** (Phase 3):
   - Relatively straightforward forms and status display
   - Good starting point for testing components

6. **Complete Documents page** (Phase 4):
   - Document table with pagination
   - Upload modal with progress tracking
   - Viewers for document details and chunks

7. **Complete Query page** (Phase 5):
   - Most complex page with debug features
   - Multiple sub-components
   - Real-time updates and visualizations

---

## Key Component Examples

### Example: Button Component

```typescript
// components/common/Button.tsx
import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  children,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
  
  return (
    <button
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner size="sm" className="mr-2" />}
      {icon && !loading && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
}
```

### Example: Toast Store

```typescript
// store/toastStore.ts
import { create } from 'zustand';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  
  addToast: (toast) => {
    const id = Math.random().toString(36).substring(7);
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }],
    }));
    
    const duration = toast.duration || 5000;
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, duration);
  },
  
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }));
  },
}));
```

### Example: useDocuments Hook

```typescript
// hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '../services/documents';
import { Document } from '../types';
import { useToastStore } from '../store/toastStore';

export function useDocuments() {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  const {
    data: documents,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['documents'],
    queryFn: documentsAPI.list,
    refetchInterval: 10000, // Refresh every 10s
  });

  const uploadMutation = useMutation({
    mutationFn: documentsAPI.upload,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      addToast({
        type: 'success',
        message: 'Document uploaded successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.message || 'Failed to upload document',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: documentsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      addToast({
        type: 'success',
        message: 'Document deleted successfully',
      });
    },
  });

  return {
    documents: documents || [],
    isLoading,
    error,
    uploadDocument: uploadMutation.mutate,
    deleteDocument: deleteMutation.mutate,
    isUploading: uploadMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
```

---

## Next Steps

1. Review this guide
2. Decide whether to implement all components or prioritize specific features
3. Start with Phase 2 (Core Infrastructure)
4. Test each phase before moving to the next

The foundation is complete. The remaining work is primarily creating React components following the patterns established in the specification.

All components should follow these principles:
- Use TypeScript with proper types
- Use TailwindCSS for styling
- Use React Query for data fetching
- Use Zustand for global state
- Follow the wireframes in the specification document
- Include loading and error states
- Be responsive and accessible

---

## Estimated Effort

- **Common Components**: 4-6 hours
- **Stores & Hooks**: 3-4 hours
- **API Layer**: 2-3 hours  
- **Settings Page**: 3-4 hours
- **Documents Page**: 6-8 hours
- **Query Page**: 10-12 hours
- **Polish & Testing**: 4-6 hours

**Total**: 32-43 hours of development

Would you like me to continue implementing specific components or would you prefer to take over from here?
