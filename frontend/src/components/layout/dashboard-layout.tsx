import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Building2,
  Home,
  Menu,
  Settings,
  Upload,
  X,
  Bell,
  LogOut,
  Moon,
  Sun,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { AuroraBackground } from '@/components/ui/aurora-background'
import { useAuth } from '@/hooks/use-auth'
import { useTheme } from '@/components/theme-provider'
import { cn } from '@/utils'
import { NotificationBell } from '@/components/notifications/notification-bell'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const userNavigation = [
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, signOut, loading } = useAuth()
  const { theme, setTheme } = useTheme()

  const isFounder = user?.role === 'founder'

  const founderNav = [
    { name: 'Your Submissions', href: '/startups', icon: Building2 },
    { name: 'Submit Startup', href: '/submit', icon: Upload },
  ]

  const otherNav = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Startups', href: '/startups', icon: Building2 },
    // { name: 'Analytics', href: '/analytics', icon: BarChart3 }, // Disabled for now
  ]

  const navigation = isFounder ? founderNav : otherNav

  useEffect(() => {
    if (!loading && user) {
      if (isFounder && (location.pathname === '/dashboard' || location.pathname === '/analytics')) {
        navigate('/submit', { replace: true })
      }
      if (!isFounder && location.pathname === '/submit') {
        navigate('/dashboard', { replace: true })
      }
    }
  }, [loading, user, isFounder, location.pathname, navigate])


  const handleLogout = async () => {
    try {
      await signOut()
      navigate('/auth/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo Section */}
      <div className="flex items-center justify-between p-6">
        <div className="flex items-center gap-3">
          <img 
            src="/logo.png" 
            alt="Younicorns Logo" 
            className="w-10 h-10 object-contain"
          />
          <span className="font-bold text-xl text-foreground">Younicorns</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden text-foreground hover:bg-white/20 dark:hover:bg-white/10"
          onClick={() => setSidebarOpen(false)}
        >
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Separator Line */}
      <div className="border-t border-gray-300 dark:border-white/20 mx-4"></div>

      {/* User Details Section */}
      <div className="p-4">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-white/10 dark:bg-white/5">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
            <span className="text-white text-base font-medium">
              {user?.displayName?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-foreground truncate">{user?.displayName || user?.email}</p>
            <p className="text-xs text-muted-foreground capitalize">
              {user?.role}
            </p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="px-4 pb-4">
        <div className="flex items-center gap-2">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={toggleTheme}
            className="flex-1 text-foreground hover:bg-white/20 dark:hover:bg-white/10 justify-start gap-2"
          >
            {theme === 'light' ? (
              <>
                <Moon className="w-4 h-4" />
                Dark Mode
              </>
            ) : (
              <>
                <Sun className="w-4 h-4" />
                Light Mode
              </>
            )}
          </Button>
          
          <NotificationBell />
        </div>
      </div>

      {/* Another Separator */}
      <div className="border-t border-gray-300 dark:border-white/20 mx-4"></div>

      {/* Navigation Section */}
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = location.pathname.startsWith(item.href)
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/20 dark:hover:bg-white/10"
              )}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Section */}
      <div className="border-t border-gray-300 dark:border-white/20 p-4 space-y-1">
        {/* User Navigation */}
        {userNavigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/20 dark:hover:bg-white/10"
              )}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          )
        })}
        
        <button
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-white/20 dark:hover:bg-white/10 w-full transition-colors"
          onClick={handleLogout}
        >
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </div>
    </div>
  )

  return (
    <AuroraBackground>
      <div className="min-h-screen relative">
      {/* Mobile sidebar */}
      <div className={cn(
        "fixed inset-0 z-50 lg:hidden",
        sidebarOpen ? "block" : "hidden"
      )}>
        <div className="fixed inset-0 bg-black/20" onClick={() => setSidebarOpen(false)} />
        <div className={cn(
          "fixed inset-y-0 left-0 w-64 border-r shadow-lg backdrop-blur-sm",
          isFounder ? "bg-white/20 dark:bg-black/20" : "bg-white/30 dark:bg-black/30"
        )}>
          {sidebarContent}
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 lg:block">
        <div className={cn(
          "flex flex-col h-full border-r backdrop-blur-sm",
          isFounder ? "bg-white/20 dark:bg-black/20" : "bg-white/30 dark:bg-black/30"
        )}>
          {sidebarContent}
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Simplified Top bar */}
        <div className="sticky top-0 z-40 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-white/20 lg:hidden">
          <div className="flex items-center justify-between px-4 py-3">
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          {children}
        </main>
      </div>
      </div>
    </AuroraBackground>
  )
}
