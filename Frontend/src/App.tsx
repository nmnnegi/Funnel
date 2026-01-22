import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Provider } from 'react-redux';
import { store } from './store';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { LeadsPage } from './pages/leads/LeadsPage';
import { StagesPage } from './pages/stages/StagesPage';
import { SettingsPage } from './pages/settings/SettingsPage';
import { LoginPage } from './pages/auth/LoginPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { useAppDispatch } from './hooks/useRedux';
import { setConfigs } from './store/slices/configsSlice';
import { configsApi } from './services/configs';

console.log('App.tsx loaded');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    console.log('AppContent mounted, loading configs...');
    // Load configs on app start
    configsApi.getAll()
      .then((configs) => {
        console.log('Configs loaded:', configs);
        dispatch(setConfigs(configs));
      })
      .catch((error) => {
        console.error('Failed to load configs:', error);
        // Initialize with empty array if API fails
        dispatch(setConfigs([]));
      });
  }, [dispatch]);

  console.log('AppContent rendering...');

  try {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/leads" element={
            <ProtectedRoute>
              <Layout>
                <LeadsPage />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/stages" element={
            <ProtectedRoute>
              <Layout>
                <StagesPage />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Layout>
                <SettingsPage />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    );
  } catch (error) {
    console.error('Error rendering AppContent:', error);
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h1>Error loading content</h1>
        <pre>{String(error)}</pre>
      </div>
    );
  }
}

function App() {
  console.log('App component rendering...');
  
  try {
    return (
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <AppContent />
        </QueryClientProvider>
      </Provider>
    );
  } catch (error) {
    console.error('Error rendering App:', error);
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h1>Error loading app</h1>
        <pre>{String(error)}</pre>
      </div>
    );
  }
}

export default App;
