import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Settings as SettingsIcon, FileText, MessageSquare } from 'lucide-react';
import Settings from './pages/Settings';
import Documents from './pages/Documents';
import Query from './pages/Query';
import { ToastContainer } from './components/common/Toast';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-100">
          <nav className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-6">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center gap-8">
                  <h1 className="text-xl font-bold text-gray-900">RAG System</h1>
                  <div className="flex gap-4">
                    <NavLink to="/query" icon={<MessageSquare className="w-5 h-5" />} text="Query" />
                    <NavLink to="/documents" icon={<FileText className="w-5 h-5" />} text="Documents" />
                    <NavLink to="/settings" icon={<SettingsIcon className="w-5 h-5" />} text="Settings" />
                  </div>
                </div>
              </div>
            </div>
          </nav>
          
          <main className="py-6">
            <Routes>
              <Route path="/" element={<Navigate to="/query" replace />} />
              <Route path="/query" element={<Query />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
          <ToastContainer />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

function NavLink({ to, icon, text }: { to: string; icon: React.ReactNode; text: string }) {
  return (
    <Link
      to={to}
      className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
    >
      {icon}
      <span className="font-medium">{text}</span>
    </Link>
  );
}

export default App;
