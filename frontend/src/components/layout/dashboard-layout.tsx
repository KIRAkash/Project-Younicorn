import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  BarChart3,
  Building2,
  FileText,
  Home,
  Menu,
  Settings,
  Upload,
  User,
  X,
  Bell,
  Search,
  LogOut,
  Moon,
  Sun,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/use-auth'
import { useTheme } from '@/components/theme-provider'
import { cn } from '@/utils'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const userNavigation = [
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, isLoading } = useAuth()
  const { theme, setTheme } = useTheme()

  const isFounder = user?.role === 'founder'

  const founderNav = [
    { name: 'Your Submissions', href: '/startups', icon: Building2 },
    { name: 'Submit Startup', href: '/submit', icon: Upload },
  ]

  const otherNav = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Startups', href: '/startups', icon: Building2 },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ]

  const navigation = isFounder ? founderNav : otherNav

  useEffect(() => {
    if (!isLoading && user) {
      if (isFounder && (location.pathname === '/dashboard' || location.pathname === '/analytics')) {
        navigate('/submit', { replace: true })
      }
      if (!isFounder && location.pathname === '/submit') {
        navigate('/dashboard', { replace: true })
      }
    }
  }, [isLoading, user, isFounder, location.pathname, navigate])


  const handleLogout = async () => {
    try {
      await logout()
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
      <div className="flex items-center justify-between p-4 border-b lg:p-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-minerva-500 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg">Minerva</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <X className="w-5 h-5" />
        </Button>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname.startsWith(item.href)
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              )}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          )
        })}
        <div className="!mt-auto border-t pt-4 space-y-2">
          {userNavigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </Link>
            )
          })}
          <button
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted w-full"
            onClick={handleLogout}
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      </nav>
    </div>
  )

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar */}
      <div className={cn(
        "fixed inset-0 z-50 lg:hidden",
        sidebarOpen ? "block" : "hidden"
      )}>
        <div className="fixed inset-0 bg-black/20" onClick={() => setSidebarOpen(false)} />
        <div className={cn(
          "fixed inset-y-0 left-0 w-64 border-r shadow-lg",
          isFounder ? "bg-muted/30" : "bg-card"
        )}>
          {sidebarContent}
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 lg:block">
        <div className={cn(
          "flex flex-col h-full border-r",
          isFounder ? "bg-muted/30" : "bg-card"
        )}>
          {sidebarContent}
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="w-5 h-5" />
              </Button>
              
              {!isFounder && (
                <div className="hidden sm:flex items-center gap-2 bg-muted rounded-lg px-3 py-2 min-w-[300px]">
                  <Search className="w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search startups, analyses..."
                    className="bg-transparent border-0 outline-none flex-1 text-sm placeholder:text-muted-foreground"
                  />
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" onClick={toggleTheme}>
                {theme === 'light' ? (
                  <Moon className="w-5 h-5" />
                ) : (
                  <Sun className="w-5 h-5" />
                )}
              </Button>
              
              <Button variant="ghost" size="icon">
                <Bell className="w-5 h-5" />
              </Button>

              <div className="flex items-center gap-2 ml-2">
                <div className="w-8 h-8 bg-minerva-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium">{user?.full_name}</p>
                  <p className="text-xs text-muted-foreground capitalize">
                    {user?.role}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  )
}
