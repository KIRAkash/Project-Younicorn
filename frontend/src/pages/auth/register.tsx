import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, Loader2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAuth } from '@/hooks/use-auth'
import { useToast } from '@/hooks/use-toast'
import { RegisterForm } from '@/types'
import { cn } from '@/utils'

export function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { register: registerUser } = useAuth()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<RegisterForm>()

  const password = watch('password')

  const onSubmit = async (data: RegisterForm) => {
    if (data.password !== data.confirm_password) {
      toast({
        title: 'Password mismatch',
        description: 'Passwords do not match. Please try again.',
        variant: 'destructive',
      })
      return
    }

    setIsLoading(true)
    try {
      await registerUser(data)
      toast({
        title: 'Account created!',
        description: 'Welcome to Project Minerva. Your account has been created successfully.',
        variant: 'success',
      })
      navigate('/dashboard')
    } catch (error) {
      toast({
        title: 'Registration failed',
        description: error instanceof Error ? error.message : 'Failed to create account',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold tracking-tight">Create your account</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Join Project Minerva to start your AI-powered due diligence journey.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full name</Label>
            <Input
              id="full_name"
              type="text"
              placeholder="Enter your full name"
              {...register('full_name', {
                required: 'Full name is required',
                minLength: {
                  value: 2,
                  message: 'Name must be at least 2 characters',
                },
              })}
              className={cn(errors.full_name && 'border-destructive')}
            />
            {errors.full_name && (
              <p className="text-sm text-destructive">{errors.full_name.message}</p>
            )}
          </div>

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
        </div>

        <div className="space-y-2">
          <Label htmlFor="role">Role</Label>
          <Select onValueChange={(value) => setValue('role', value as 'founder' | 'investor')}>
            <SelectTrigger>
              <SelectValue placeholder="Select your role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="founder">Startup Founder</SelectItem>
              <SelectItem value="investor">Investor</SelectItem>
            </SelectContent>
          </Select>
          {errors.role && (
            <p className="text-sm text-destructive">{errors.role.message}</p>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="company">Company (optional)</Label>
            <Input
              id="company"
              type="text"
              placeholder="Your company"
              {...register('company')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="title">Job title (optional)</Label>
            <Input
              id="title"
              type="text"
              placeholder="Your job title"
              {...register('title')}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a password"
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters',
                },
                pattern: {
                  value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                  message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number',
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

        <div className="space-y-2">
          <Label htmlFor="confirm_password">Confirm password</Label>
          <div className="relative">
            <Input
              id="confirm_password"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm your password"
              {...register('confirm_password', {
                required: 'Please confirm your password',
                validate: (value) =>
                  value === password || 'Passwords do not match',
              })}
              className={cn(errors.confirm_password && 'border-destructive', 'pr-10')}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-4 w-4 text-muted-foreground" />
              ) : (
                <Eye className="h-4 w-4 text-muted-foreground" />
              )}
            </Button>
          </div>
          {errors.confirm_password && (
            <p className="text-sm text-destructive">{errors.confirm_password.message}</p>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <input
            id="terms"
            type="checkbox"
            className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
            {...register('terms', {
              required: 'You must accept the terms and conditions',
            })}
          />
          <Label htmlFor="terms" className="text-sm">
            I agree to the{' '}
            <Link to="/terms" className="text-primary hover:underline">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link to="/privacy" className="text-primary hover:underline">
              Privacy Policy
            </Link>
          </Label>
        </div>
        {errors.terms && (
          <p className="text-sm text-destructive">{errors.terms.message}</p>
        )}

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Create account
        </Button>
      </form>

      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to="/auth/login" className="text-primary hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
