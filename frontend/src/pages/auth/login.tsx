import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, Loader2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/hooks/use-auth'
import { useToast } from '@/hooks/use-toast'
import { LoginForm } from '@/types'
import { cn } from '@/utils'

export function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>()

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      const user = await login(data.email, data.password)
      toast({
        title: 'Welcome back!',
        description: 'You have been successfully logged in.',
        variant: 'success',
      })
      
      // Role-based redirection
      if (user.role === 'founder') {
        navigate('/submit', { replace: true })
      } else {
        navigate('/dashboard', { replace: true })
      }

    } catch (error) {
      toast({
        title: 'Login failed',
        description: error instanceof Error ? error.message : 'Invalid credentials',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold tracking-tight">Sign in to your account</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Welcome back! Please enter your credentials to continue.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email address</Label>
          <Input
            id="email"
            type="email"
            placeholder="Enter your email"
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Please enter a valid email address',
              },
            })}
            className={cn(errors.email && 'border-destructive')}
          />
          {errors.email && (
            <p className="text-sm text-destructive">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters',
                },
              })}
              className={cn(errors.password && 'border-destructive', 'pr-10')}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4 text-muted-foreground" />
              ) : (
                <Eye className="h-4 w-4 text-muted-foreground" />
              )}
            </Button>
          </div>
          {errors.password && (
            <p className="text-sm text-destructive">{errors.password.message}</p>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <input
              id="remember"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <Label htmlFor="remember" className="text-sm">
              Remember me
            </Label>
          </div>
          <Link
            to="/auth/forgot-password"
            className="text-sm text-primary hover:underline"
          >
            Forgot password?
          </Link>
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Sign in
        </Button>
      </form>

      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          Don't have an account?{' '}
          <Link to="/auth/register" className="text-primary hover:underline font-medium">
            Sign up
          </Link>
        </p>
      </div>

      {/* Demo credentials */}
      <div className="mt-8 p-4 bg-muted rounded-lg">
        <h3 className="text-sm font-medium mb-2">Demo Credentials</h3>
        <div className="space-y-1 text-xs text-muted-foreground">
          <p><strong>Investor:</strong> investor@demo.com / password123</p>
          <p><strong>Founder:</strong> founder@demo.com / password123</p>
        </div>
      </div>
    </div>
  )
}
