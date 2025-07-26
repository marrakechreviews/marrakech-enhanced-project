import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import HomePage from './pages/HomePage';
import ArticlesPageSimple from './pages/ArticlesPageSimple';
import ArticleDetailPage from './pages/ArticleDetailPage';
import ReviewsPageSimple from './pages/ReviewsPageSimple';
import AddReviewPage from './pages/AddReviewPage';
import ContactPage from './pages/ContactPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AdminDashboard from './pages/AdminDashboard';
import UserDashboard from './pages/UserDashboard';
import MediaLibrary from './pages/MediaLibrary';
import AboutPage from './pages/AboutPage';
import ServicesPage from './pages/ServicesPage';
import GalleryPage from './pages/GalleryPage';
import BlogPage from './pages/BlogPage';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Placeholder components for missing pages
const SettingsPage = () => <div className="container mx-auto px-4 py-8"><h1 className="text-3xl font-bold">Settings Page</h1><p>Coming soon...</p></div>;
const UnauthorizedPage = () => (
  <div className="container mx-auto px-4 py-8 text-center">
    <h1 className="text-3xl font-bold mb-4">Unauthorized</h1>
    <p className="text-muted-foreground">You don't have permission to access this page.</p>
  </div>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Auth routes (without layout) */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            
            {/* Main routes (with layout) */}
            <Route path="/*" element={
              <Layout>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/articles" element={<ArticlesPageSimple />} />
                  <Route path="/articles/:id" element={<ArticleDetailPage />} />
                  <Route path="/reviews" element={<ReviewsPageSimple />} />
                  <Route path="/reviews/add" element={<AddReviewPage />} />
                  <Route path="/contact" element={<ContactPage />} />
                  <Route path="/about" element={<AboutPage />} />
                  <Route path="/services" element={<ServicesPage />} />
                  <Route path="/gallery" element={<GalleryPage />} />
                  <Route path="/blog" element={<BlogPage />} />
                  
                  {/* Protected Admin Routes */}
                  <Route path="/admin" element={
                    <ProtectedRoute requiredRole="admin">
                      <AdminDashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/admin/*" element={
                    <ProtectedRoute requiredRole="admin">
                      <AdminDashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/media" element={
                    <ProtectedRoute requiredRole="moderator">
                      <MediaLibrary />
                    </ProtectedRoute>
                  } />
                  
                  {/* Protected User Routes */}
                  <Route path="/dashboard" element={
                    <ProtectedRoute>
                      <UserDashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/settings" element={
                    <ProtectedRoute>
                      <SettingsPage />
                    </ProtectedRoute>
                  } />
                  
                  {/* 404 Route */}
                  <Route path="*" element={
                    <div className="container mx-auto px-4 py-8 text-center">
                      <h1 className="text-3xl font-bold mb-4">404 - Page Not Found</h1>
                      <p className="text-muted-foreground">The page you're looking for doesn't exist.</p>
                    </div>
                  } />
                </Routes>
              </Layout>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;

