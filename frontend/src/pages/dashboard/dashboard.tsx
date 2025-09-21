import { useQuery } from '@tanstack/react-query'
import { 
  BarChart3, 
  Building2, 
  Clock,
  ArrowUpRight,
  Plus,
  Eye,
  FileText,
  Target,
} from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { dashboardApi } from '@/services/api'
import { useAuth } from '@/hooks/use-auth'
import { formatRelativeTime, getScoreColor, getStatusColor } from '@/utils'

export function DashboardPage() {
  const { user } = useAuth()
  
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
  })

  const { data: recentActivity } = useQuery({
    queryKey: ['dashboard-activity'],
    queryFn: dashboardApi.getRecentActivity,
  })

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/4 mb-2"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-muted rounded-lg animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  const isFounder = user?.role === 'founder'
  const isInvestor = user?.role === 'investor'

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.full_name?.split(' ')[0]}
          </h1>
          <p className="text-muted-foreground">
            {isFounder 
              ? "Track your startup submissions and analysis progress"
              : "Monitor your portfolio and discover new investment opportunities"
            }
          </p>
        </div>
        <div className="flex gap-2">
          {isFounder && (
            <Button asChild>
              <Link to="/submit">
                <Plus className="w-4 h-4 mr-2" />
                Submit Startup
              </Link>
            </Button>
          )}
          {isInvestor && (
            <Button asChild>
              <Link to="/startups">
                <Eye className="w-4 h-4 mr-2" />
                Browse Startups
              </Link>
            </Button>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Startups</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_startups || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-success-600 flex items-center">
                <ArrowUpRight className="w-3 h-3 mr-1" />
                +12% from last month
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Analysis</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_analysis || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-warning-600 flex items-center">
                <ArrowUpRight className="w-3 h-3 mr-1" />
                +5 this week
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Analysis</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.completed_analysis || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-success-600 flex items-center">
                <ArrowUpRight className="w-3 h-3 mr-1" />
                +23% completion rate
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.avg_score?.toFixed(1) || '0.0'}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-success-600 flex items-center">
                <ArrowUpRight className="w-3 h-3 mr-1" />
                +0.3 from last month
              </span>
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Submissions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Submissions</CardTitle>
            <CardDescription>
              Latest startup submissions and their status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.recent_submissions?.slice(0, 5).map((startup) => (
                <div key={startup.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-minerva-100 rounded-lg flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-minerva-600" />
                    </div>
                    <div>
                      <p className="font-medium">{startup.company_info.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {startup.company_info.industry} • {startup.company_info.funding_stage}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(startup.status)}>
                      {startup.status}
                    </Badge>
                    <Button variant="ghost" size="sm" asChild>
                      <Link to={`/startups/${startup.id}`}>
                        <Eye className="w-4 h-4" />
                      </Link>
                    </Button>
                  </div>
                </div>
              )) || (
                <div className="text-center py-8 text-muted-foreground">
                  <Building2 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No submissions yet</p>
                  {isFounder && (
                    <Button variant="outline" size="sm" className="mt-2" asChild>
                      <Link to="/submit">Submit your first startup</Link>
                    </Button>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Industry Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Industry Breakdown</CardTitle>
            <CardDescription>
              Distribution of startups by industry
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.industry_breakdown?.slice(0, 6).map((industry, index) => (
                <div key={industry.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: `hsl(${index * 60}, 70%, 50%)` }}
                    />
                    <span className="font-medium capitalize">
                      {industry.name.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {industry.value}
                    </span>
                    <div className="w-20">
                      <Progress 
                        value={(industry.value / (stats?.total_startups || 1)) * 100} 
                        className="h-2"
                      />
                    </div>
                  </div>
                </div>
              )) || (
                <div className="text-center py-8 text-muted-foreground">
                  <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No data available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest actions and updates across the platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity?.slice(0, 8).map((activity, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-minerva-500 rounded-full mt-2 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm">
                    <span className="font-medium">{activity.user_name}</span>{' '}
                    {activity.action}{' '}
                    <span className="font-medium">{activity.target}</span>
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatRelativeTime(activity.timestamp)}
                  </p>
                </div>
                {activity.score && (
                  <Badge className={getScoreColor(activity.score)}>
                    {activity.score.toFixed(1)}
                  </Badge>
                )}
              </div>
            )) || (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No recent activity</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
