import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User } from '@/types'
import { authApi } from '@/services/api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<User>
  register: (userData: any) => Promise<void>
  logout: () => Promise<void>
  updateUser: (userData: Partial<User>) => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on app start
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('minerva_token')
      if (token) {
        const userData = await authApi.getCurrentUser()
        setUser(userData)
      }
    } catch (error) {
      // Token might be expired or invalid
      localStorage.removeItem('minerva_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string): Promise<User> => {
    try {
      const response = await authApi.login({ email, password })
      localStorage.setItem('minerva_token', response.access_token)
      const userData = await authApi.getCurrentUser()
      setUser(userData)
      return userData
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: any) => {
    try {
      const response = await authApi.register(userData)
      localStorage.setItem('minerva_token', response.access_token)
      const user = await authApi.getCurrentUser()
      setUser(user)
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      // Continue with logout even if API call fails
    } finally {
      localStorage.removeItem('minerva_token')
      setUser(null)
    }
  }

  const updateUser = async (userData: Partial<User>) => {
    try {
      const updatedUser = await authApi.updateProfile(userData)
      setUser(updatedUser)
    } catch (error) {
      throw error
    }
  }

  const value = {
    user,
    isLoading,
    login,
    register,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
