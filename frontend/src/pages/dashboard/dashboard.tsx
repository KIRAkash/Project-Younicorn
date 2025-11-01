import { useQuery } from '@tanstack/react-query'
import { useState, memo } from 'react'
import { 
  Building2, 
  ArrowUpRight,
  Plus,
  Eye,
  TrendingUp,
  Sparkles,
  Rocket,
  Target,
  Zap,
  BarChart3,
  Briefcase,
  Package,
  FileText,
} from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { dashboardApi } from '@/services/api'
import { useAuth } from '@/hooks/use-auth'
import { formatRelativeTime } from '@/utils'

// Empty state component for insights
function EmptyInsights({ icon: Icon, message }: { icon: any, message: string }) {
  return (
    <div className="text-center py-12">
      <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-full mb-3">
        <Icon className="w-8 h-8 text-gray-500 dark:text-gray-400" />
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  
  // Split into multiple optimized queries with caching
  const { data: coreStats, isLoading: loadingCore } = useQuery({
    queryKey: ['dashboard-core-stats'],
    queryFn: dashboardApi.getCoreStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  })

  const { data: recentStartups, isLoading: loadingStartups } = useQuery({
    queryKey: ['dashboard-recent-startups', 5],
    queryFn: () => dashboardApi.getRecentStartups(5),
    staleTime: 2 * 60 * 1000, // 2 minutes
    enabled: !!coreStats, // Wait for core stats
    refetchOnWindowFocus: false,
  })

  const { data: breakdowns } = useQuery({
    queryKey: ['dashboard-breakdowns'],
    queryFn: dashboardApi.getBreakdowns,
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!recentStartups, // Load after startups
    refetchOnWindowFocus: false,
  })

  const { data: recentActivity } = useQuery({
    queryKey: ['dashboard-activity', 8],
    queryFn: () => dashboardApi.getRecentActivity(8),
    staleTime: 2 * 60 * 1000, // 2 minutes
    enabled: !!recentStartups, // Load after startups
    refetchOnWindowFocus: false,
  })

  const isLoading = loadingCore

  if (loadingCore) {
    return (
      <div className="min-h-screen">
        {/* Hero Loading */}
        <div className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-500 px-6 py-16">
          <div className="max-w-7xl mx-auto">
            <div className="h-16 bg-white/20 rounded-lg w-2/3 mb-4 animate-pulse"></div>
            <div className="h-6 bg-white/20 rounded-lg w-1/2 animate-pulse"></div>
          </div>
        </div>
        
        {/* Content Loading */}
        <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded-xl animate-pulse"></div>
            ))}
          </div>
          <div className="h-96 bg-muted rounded-xl animate-pulse"></div>
        </div>
      </div>
    )
  }

  const isFounder = user?.role === 'founder'
  const isInvestor = user?.role === 'investor'

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-950 dark:to-gray-900">
      {/* Hero Section with Gradient */}
      <div className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-500 px-6 py-12 md:py-16">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -right-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-1/2 -left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto">
          <div className="flex items-start justify-between flex-wrap gap-8">
            <div className="flex-1 min-w-[300px]">
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-black tracking-tight text-white mb-4">
                Welcome back,
                <span className="block bg-gradient-to-r from-yellow-200 via-pink-200 to-purple-200 bg-clip-text text-transparent">
                  {user?.displayName?.split(' ')[0] || 'Investor'}
                </span>
              </h1>
              <p className="text-lg md:text-xl text-white/90 max-w-2xl mb-6">
                {isFounder 
                  ? "Track your startup journey and get AI-powered insights to accelerate your growth"
                  : "Discover exceptional startups and make data-driven investment decisions"
                }
              </p>
              
              {/* CTA Buttons moved here */}
              <div className="flex gap-3 flex-wrap">
                {isFounder && (
                  <Button 
                    size="lg" 
                    className="bg-white text-purple-600 hover:bg-white/90 shadow-xl hover:shadow-2xl transition-all duration-300 font-semibold"
                    asChild
                  >
                    <Link to="/submit">
                      <Plus className="w-5 h-5 mr-2" />
                      Submit Startup
                    </Link>
                  </Button>
                )}
                {isInvestor && (
                  <Button 
                    size="lg" 
                    className="bg-white text-purple-600 hover:bg-white/90 shadow-xl hover:shadow-2xl transition-all duration-300 font-semibold"
                    asChild
                  >
                    <Link to="/startups">
                      <Eye className="w-5 h-5 mr-2" />
                      Browse Startups
                    </Link>
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Quick Stats Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card className="border-none shadow-lg hover:shadow-xl transition-shadow duration-300 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2.5 bg-purple-600 rounded-lg">
                  <Building2 className="h-5 w-5 text-white" />
                </div>
                <Badge className="bg-purple-600 text-white border-none text-xs">
                  <ArrowUpRight className="w-3 h-3 mr-1" />
                  +12%
                </Badge>
              </div>
              <div className="text-3xl font-black text-purple-900 dark:text-purple-100 mb-1">
                {coreStats?.total_startups || 0}
              </div>
              <p className="text-xs font-semibold text-purple-700 dark:text-purple-300">
                Total Startups
              </p>
            </CardContent>
          </Card>

          <Card className="border-none shadow-lg hover:shadow-xl transition-shadow duration-300 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2.5 bg-blue-600 rounded-lg">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <Badge className="bg-blue-600 text-white border-none text-xs">
                  <ArrowUpRight className="w-3 h-3 mr-1" />
                  +23%
                </Badge>
              </div>
              <div className="text-3xl font-black text-blue-900 dark:text-blue-100 mb-1">
                {coreStats?.completed_analysis || 0}
              </div>
              <p className="text-xs font-semibold text-blue-700 dark:text-blue-300">
                Completed Analysis
              </p>
            </CardContent>
          </Card>

          <Card className="border-none shadow-lg hover:shadow-xl transition-shadow duration-300 bg-gradient-to-br from-cyan-50 to-cyan-100 dark:from-cyan-950 dark:to-cyan-900">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2.5 bg-cyan-600 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                <Badge className="bg-cyan-600 text-white border-none text-xs">
                  <Target className="w-3 h-3 mr-1" />
                  High
                </Badge>
              </div>
              <div className="text-3xl font-black text-cyan-900 dark:text-cyan-100 mb-1">
                {coreStats?.total_startups || 0}
              </div>
              <p className="text-xs font-semibold text-cyan-700 dark:text-cyan-300">
                Active Opportunities
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Two Column Layout for Main Content */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recently Added Startups */}
          <Card className="border-none shadow-lg lg:col-span-2">
            <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                    Recently Added
                  </CardTitle>
                  <CardDescription className="text-base mt-1">
                    Latest startups ready for your review
                  </CardDescription>
                </div>
                <Button variant="outline" asChild className="border-purple-200 hover:bg-purple-50 dark:border-purple-800 dark:hover:bg-purple-950">
                  <Link to="/startups">
                    View All
                    <ArrowUpRight className="w-4 h-4 ml-2" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              {loadingStartups ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-24 bg-gray-100 dark:bg-gray-800 rounded-xl animate-pulse"></div>
                  ))}
                </div>
              ) : recentStartups?.map((startup) => (
                <div 
                  key={startup.id} 
                  className="group flex items-center gap-4 p-4 rounded-xl border border-gray-200 dark:border-gray-800 hover:border-purple-300 dark:hover:border-purple-700 hover:shadow-md transition-all duration-300 cursor-pointer"
                  onClick={() => window.location.href = `/startups/${startup.id}`}
                >
                  {/* Startup Logo */}
                  <div className="relative flex-shrink-0">
                    {startup.company_info.logo_url ? (
                      <img 
                        src={startup.company_info.logo_url} 
                        alt={`${startup.company_info.name} logo`}
                        className="w-16 h-16 rounded-xl object-contain border-2 border-gray-200 dark:border-gray-700 group-hover:border-purple-400 transition-colors bg-white"
                        loading="lazy"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                        <span className="text-2xl font-black text-white">
                          {startup.company_info.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {/* Startup Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 truncate group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                        {startup.company_info.name}
                      </h3>
                      {startup.analysis_status === 'completed' && (
                        <Sparkles className="w-4 h-4 text-green-600 animate-pulse flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-1">
                      {startup.company_info.description}
                    </p>
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="secondary" className="text-xs font-medium capitalize">
                        {startup.company_info.industry.replace(/_/g, ' ')}
                      </Badge>
                      <Badge variant="outline" className="text-xs capitalize">
                        {startup.company_info.funding_stage.replace(/_/g, ' ')}
                      </Badge>
                      {startup.overall_score && (
                        <Badge className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-none text-xs">
                          <Target className="w-3 h-3 mr-1" />
                          {startup.overall_score.toFixed(1)}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {/* Action Button */}
                  <div className="flex-shrink-0">
                    {startup.analysis_status === 'completed' ? (
                      <Button 
                        size="sm" 
                        className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-md"
                        asChild
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Link to={`/startups/${startup.id}/analysis`}>
                          <Sparkles className="w-4 h-4 mr-2" />
                          View Analysis
                        </Link>
                      </Button>
                    ) : (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        asChild
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Link to={`/startups/${startup.id}`}>
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </Link>
                      </Button>
                    )}
                  </div>
                </div>
              )) || (
                <div className="text-center py-16">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 rounded-full mb-4">
                    <Rocket className="w-10 h-10 text-purple-600 dark:text-purple-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    No startups yet
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {isFounder 
                      ? "Submit your first startup to get started"
                      : "New startups will appear here once submitted"
                    }
                  </p>
                  {isFounder && (
                    <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700" asChild>
                      <Link to="/submit">
                        <Plus className="w-4 h-4 mr-2" />
                        Submit Startup
                      </Link>
                    </Button>
                  )}
                </div>
              )}
            </div>
          </CardContent>
          </Card>

          {/* Insights with Tabs */}
          <Card className="border-none shadow-lg">
            <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950">
              <div>
                <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  Insights
                </CardTitle>
                <CardDescription className="text-base mt-1">
                  Portfolio breakdown by different dimensions
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <Tabs defaultValue="industry" className="w-full">
                <TabsList className="grid w-full grid-cols-4 mb-6">
                  <TabsTrigger value="industry" className="text-xs">
                    <BarChart3 className="w-3 h-3 mr-1" />
                    Industry
                  </TabsTrigger>
                  <TabsTrigger value="funding" className="text-xs">
                    <Target className="w-3 h-3 mr-1" />
                    Funding
                  </TabsTrigger>
                  <TabsTrigger value="product" className="text-xs">
                    <Package className="w-3 h-3 mr-1" />
                    Product
                  </TabsTrigger>
                  <TabsTrigger value="structure" className="text-xs">
                    <Briefcase className="w-3 h-3 mr-1" />
                    Structure
                  </TabsTrigger>
                </TabsList>

                {/* Industry Tab */}
                <TabsContent value="industry" className="space-y-4">
                  {breakdowns?.industry_breakdown?.slice(0, 5).map((item, index) => {
                    const colors = [
                      { bg: 'from-purple-500 to-purple-600' },
                      { bg: 'from-blue-500 to-blue-600' },
                      { bg: 'from-cyan-500 to-cyan-600' },
                      { bg: 'from-green-500 to-green-600' },
                      { bg: 'from-orange-500 to-orange-600' },
                    ]
                    const color = colors[index % colors.length]
                    const percentage = ((item.value / (coreStats?.total_startups || 1)) * 100).toFixed(0)

                    return (
                      <div key={item.name} className="flex items-center gap-3">
                        <div className={`flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br ${color.bg} flex items-center justify-center`}>
                          <BarChart3 className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-semibold text-sm text-gray-900 dark:text-gray-100 capitalize">
                              {item.name.replace(/_/g, ' ')}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-gray-700 dark:text-gray-300">
                                {item.value}
                              </span>
                              <Badge variant="secondary" className="text-xs">
                                {percentage}%
                              </Badge>
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div 
                              className={`h-full bg-gradient-to-r ${color.bg} transition-all duration-500 rounded-full`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )
                  }) || <EmptyInsights icon={BarChart3} message="No industry data yet" />}
                </TabsContent>

                {/* Funding Stage Tab */}
                <TabsContent value="funding" className="space-y-4">
                  {breakdowns?.funding_stage_breakdown?.slice(0, 5).map((item, index) => {
                    const colors = [
                      { bg: 'from-emerald-500 to-emerald-600' },
                      { bg: 'from-teal-500 to-teal-600' },
                      { bg: 'from-sky-500 to-sky-600' },
                      { bg: 'from-indigo-500 to-indigo-600' },
                      { bg: 'from-violet-500 to-violet-600' },
                    ]
                    const color = colors[index % colors.length]
                    const percentage = ((item.value / (coreStats?.total_startups || 1)) * 100).toFixed(0)

                    return (
                      <div key={item.name} className="flex items-center gap-3">
                        <div className={`flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br ${color.bg} flex items-center justify-center`}>
                          <Target className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-semibold text-sm text-gray-900 dark:text-gray-100 capitalize">
                              {item.name.replace(/_/g, ' ')}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-gray-700 dark:text-gray-300">
                                {item.value}
                              </span>
                              <Badge variant="secondary" className="text-xs">
                                {percentage}%
                              </Badge>
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div 
                              className={`h-full bg-gradient-to-r ${color.bg} transition-all duration-500 rounded-full`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )
                  }) || <EmptyInsights icon={Target} message="No funding stage data yet" />}
                </TabsContent>

                {/* Product Stage Tab */}
                <TabsContent value="product" className="space-y-4">
                  {breakdowns?.product_stage_breakdown?.slice(0, 5).map((item, index) => {
                    const colors = [
                      { bg: 'from-rose-500 to-rose-600' },
                      { bg: 'from-pink-500 to-pink-600' },
                      { bg: 'from-fuchsia-500 to-fuchsia-600' },
                      { bg: 'from-purple-500 to-purple-600' },
                      { bg: 'from-violet-500 to-violet-600' },
                    ]
                    const color = colors[index % colors.length]
                    const percentage = ((item.value / (coreStats?.total_startups || 1)) * 100).toFixed(0)

                    return (
                      <div key={item.name} className="flex items-center gap-3">
                        <div className={`flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br ${color.bg} flex items-center justify-center`}>
                          <Package className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-semibold text-sm text-gray-900 dark:text-gray-100 capitalize">
                              {item.name.replace(/_/g, ' ')}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-gray-700 dark:text-gray-300">
                                {item.value}
                              </span>
                              <Badge variant="secondary" className="text-xs">
                                {percentage}%
                              </Badge>
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div 
                              className={`h-full bg-gradient-to-r ${color.bg} transition-all duration-500 rounded-full`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )
                  }) || <EmptyInsights icon={Package} message="No product stage data yet" />}
                </TabsContent>

                {/* Company Structure Tab */}
                <TabsContent value="structure" className="space-y-4">
                  {breakdowns?.company_structure_breakdown?.slice(0, 5).map((item, index) => {
                    const colors = [
                      { bg: 'from-amber-500 to-amber-600' },
                      { bg: 'from-yellow-500 to-yellow-600' },
                      { bg: 'from-lime-500 to-lime-600' },
                      { bg: 'from-green-500 to-green-600' },
                      { bg: 'from-emerald-500 to-emerald-600' },
                    ]
                    const color = colors[index % colors.length]
                    const percentage = ((item.value / (coreStats?.total_startups || 1)) * 100).toFixed(0)

                    return (
                      <div key={item.name} className="flex items-center gap-3">
                        <div className={`flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br ${color.bg} flex items-center justify-center`}>
                          <Briefcase className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-semibold text-sm text-gray-900 dark:text-gray-100 capitalize">
                              {item.name.replace(/_/g, ' ')}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-gray-700 dark:text-gray-300">
                                {item.value}
                              </span>
                              <Badge variant="secondary" className="text-xs">
                                {percentage}%
                              </Badge>
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div 
                              className={`h-full bg-gradient-to-r ${color.bg} transition-all duration-500 rounded-full`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )
                  }) || <EmptyInsights icon={Briefcase} message="No company structure data yet" />}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Recent Activity Timeline */}
          <Card className="border-none shadow-lg">
          <CardHeader className="border-b bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  Recent Activity
                </CardTitle>
                <CardDescription className="text-base mt-1">
                  Latest analysis completions and updates
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-3">
              {recentActivity?.map((activity, index) => (
                <div key={index} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">
                  <div className="flex-shrink-0">
                    {activity.status === 'completed' ? (
                      <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
                        <Zap className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-gray-100 font-medium mb-1">
                      {activity.company_name} Analysis {activity.status === 'completed' ? 'completed' : 'started'}
                    </p>
                    <div className="flex items-center gap-2 flex-wrap text-xs text-gray-600 dark:text-gray-400">
                      {activity.overall_score && (
                        <Badge className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-none text-xs">
                          {activity.overall_score.toFixed(1)}
                        </Badge>
                      )}
                      <span>
                        • {activity.started_at ? formatRelativeTime(activity.started_at) : 'Recently'}
                      </span>
                      {activity.investment_recommendation && (
                        <span>• {activity.investment_recommendation}</span>
                      )}
                    </div>
                  </div>
                </div>
              )) || (
                <div className="text-center py-16">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900 dark:to-emerald-900 rounded-full mb-4">
                    <Zap className="w-10 h-10 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    No recent activity
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Activity will appear here as analyses are completed
                  </p>
                </div>
              )}
            </div>
          </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
