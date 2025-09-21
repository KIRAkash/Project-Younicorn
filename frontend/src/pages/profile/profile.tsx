import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { User, Mail, Building, Calendar, Edit, X, Save } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/hooks/use-auth'
import { useToast } from '@/hooks/use-toast'
import { formatDate, capitalizeFirst } from '@/utils'

export function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false)
  const { user, updateUser } = useAuth()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm({
    defaultValues: {
      full_name: user?.full_name || '',
      company: user?.company || '',
      title: user?.title || '',
      bio: user?.bio || '',
      email_notifications: user?.email_notifications ?? true,
      timezone: user?.timezone || 'UTC',
    },
  })

  const onSubmit = async (data: any) => {
    try {
      await updateUser(data)
      setIsEditing(false)
      toast({
        title: 'Profile updated',
        description: 'Your profile has been successfully updated.',
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Update failed',
        description: error instanceof Error ? error.message : 'Failed to update profile',
        variant: 'destructive',
      })
    }
  }

  const handleCancel = () => {
    reset()
    setIsEditing(false)
  }

  if (!user) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <User className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Profile not found</h3>
          <p className="text-muted-foreground">Unable to load your profile information.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences
          </p>
        </div>
        {!isEditing && (
          <Button onClick={() => setIsEditing(true)}>
            <Edit className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile Overview */}
        <Card className="lg:col-span-1">
          <CardHeader className="text-center">
            <div className="w-24 h-24 bg-minerva-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-12 h-12 text-minerva-600" />
            </div>
            <CardTitle>{user.full_name}</CardTitle>
            <CardDescription className="flex items-center justify-center gap-2">
              <Badge className="capitalize">
                {capitalizeFirst(user.role)}
              </Badge>
              <Badge variant="outline" className={
                user.status === 'active' ? 'text-success-600 border-success-200' : 
                user.status === 'pending' ? 'text-warning-600 border-warning-200' :
                'text-muted-foreground'
              }>
                {capitalizeFirst(user.status)}
              </Badge>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3 text-sm">
              <Mail className="w-4 h-4 text-muted-foreground" />
              <span>{user.email}</span>
            </div>
            {user.company && (
              <div className="flex items-center gap-3 text-sm">
                <Building className="w-4 h-4 text-muted-foreground" />
                <span>{user.company}</span>
              </div>
            )}
            <div className="flex items-center gap-3 text-sm">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span>Joined {formatDate(user.created_at)}</span>
            </div>
            {user.last_login && (
              <div className="flex items-center gap-3 text-sm">
                <User className="w-4 h-4 text-muted-foreground" />
                <span>Last login {formatDate(user.last_login)}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Profile Form */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>
              Update your personal details and preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    {...register('full_name', { required: 'Full name is required' })}
                    disabled={!isEditing}
                  />
                  {errors.full_name && (
                    <p className="text-sm text-destructive">{errors.full_name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    value={user.email}
                    disabled
                    className="bg-muted"
                  />
                  <p className="text-xs text-muted-foreground">
                    Email cannot be changed. Contact support if needed.
                  </p>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="company">Company</Label>
                  <Input
                    id="company"
                    {...register('company')}
                    disabled={!isEditing}
                    placeholder="Your company name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="title">Job Title</Label>
                  <Input
                    id="title"
                    {...register('title')}
                    disabled={!isEditing}
                    placeholder="Your job title"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  {...register('bio')}
                  disabled={!isEditing}
                  placeholder="Tell us about yourself..."
                  rows={4}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Input
                    id="timezone"
                    {...register('timezone')}
                    disabled={!isEditing}
                    placeholder="UTC"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Role</Label>
                  <Input
                    value={capitalizeFirst(user.role)}
                    disabled
                    className="bg-muted"
                  />
                  <p className="text-xs text-muted-foreground">
                    Role cannot be changed. Contact support if needed.
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <Label>Preferences</Label>
                <div className="flex items-center space-x-2">
                  <input
                    id="email_notifications"
                    type="checkbox"
                    {...register('email_notifications')}
                    disabled={!isEditing}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary disabled:opacity-50"
                  />
                  <Label htmlFor="email_notifications" className="text-sm">
                    Receive email notifications
                  </Label>
                </div>
              </div>

              {isEditing && (
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={handleCancel}>
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </Button>
                  <Button type="submit" disabled={!isDirty}>
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      </div>

      {/* Account Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Account Statistics</CardTitle>
          <CardDescription>
            Your activity and usage statistics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-sm text-muted-foreground">
                {user.role === 'founder' ? 'Startups Submitted' : 'Startups Analyzed'}
              </p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-sm text-muted-foreground">
                {user.role === 'founder' ? 'Analyses Received' : 'Analyses Completed'}
              </p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-sm text-muted-foreground">Comments Made</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
