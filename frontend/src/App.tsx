import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthProvider } from '@/contexts/AuthContext'
import { useAuth } from '@/contexts/AuthContext'

// Layout components
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { AuthLayout } from '@/components/layout/auth-layout'

// Page components
import { LandingPage } from '@/pages/landing/landing'
import { LoginPage } from '@/pages/auth/login'
import { RegisterPage } from '@/pages/auth/register'
import { DashboardPage } from '@/pages/dashboard/dashboard'
import { StartupListPage } from '@/pages/startups/startup-list'
import { StartupDetailPage } from '@/pages/startups/startup-detail'
import { SubmissionPage } from '@/pages/submission/submission-new'
import { AnalysisPage } from '@/pages/analysis/analysis'
import { ProfilePage } from '@/pages/profile/profile'
import { SettingsPage } from '@/pages/settings/settings'
import { NotFoundPage } from '@/pages/not-found'

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/auth/login" replace />
  }

  return <>{children}</>
}

// Public route wrapper (redirect to dashboard if authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

// Landing route wrapper (show landing for non-authenticated, dashboard for authenticated)
function LandingRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  return <LandingPage />
}

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="minerva-ui-theme">
      <AuthProvider>
        <div className="min-h-screen">
          <Routes>
            {/* Landing page */}
            <Route path="/" element={<LandingRoute />} />
            
            {/* Auth routes */}
            <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
            <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
            <Route
              path="/auth/login"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />
            <Route
              path="/auth/*"
              element={
                <PublicRoute>
                  <AuthLayout>
                    <Routes>
                      <Route path="register" element={<RegisterPage />} />
                      <Route path="*" element={<Navigate to="/auth/login" replace />} />
                    </Routes>
                  </AuthLayout>
                </PublicRoute>
              }
            />

            {/* Protected routes */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <Routes>
                      {/* Dashboard */}
                      <Route path="dashboard" element={<DashboardPage />} />
                      
                      {/* Startups */}
                      <Route path="startups" element={<StartupListPage />} />
                      <Route path="startups/:id" element={<StartupDetailPage />} />
                      <Route path="startups/:id/analysis" element={<AnalysisPage />} />
                      
                      {/* Submission (Founder Portal) */}
                      <Route path="submit" element={<SubmissionPage />} />
                      
                      {/* User */}
                      <Route path="profile" element={<ProfilePage />} />
                      <Route path="settings" element={<SettingsPage />} />
                      
                      {/* 404 */}
                      <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
          </Routes>

          <Toaster />
        </div>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
