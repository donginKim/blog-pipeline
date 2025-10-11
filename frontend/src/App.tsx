import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/hooks/useAuth';
import { Layout } from '@/components/Layout';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { KeywordsPage } from '@/pages/KeywordsPage';
import { BlogsPage } from '@/pages/BlogsPage';
import { TargetsPage } from '@/pages/TargetsPage';
import { ResultsPage } from '@/pages/ResultsPage';
import { CrawlRunsPage } from '@/pages/CrawlRunsPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { TestPage } from '@/pages/TestPage';
import { GeneratedPostsPage } from '@/pages/GeneratedPostsPage';
import { ProtectedRoute } from '@/components/ProtectedRoute';

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
      <Router>
        <AuthProvider>
          <div className="min-h-screen bg-background">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="test" element={<TestPage />} />
                <Route path="keywords" element={<KeywordsPage />} />
                <Route path="blogs" element={<BlogsPage />} />
                <Route path="targets" element={<TargetsPage />} />
                <Route path="results" element={<ResultsPage />} />
                <Route path="crawl-runs" element={<CrawlRunsPage />} />
                <Route path="generated-posts" element={<GeneratedPostsPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Routes>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                },
                error: {
                  duration: 5000,
                },
              }}
            />
          </div>
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
