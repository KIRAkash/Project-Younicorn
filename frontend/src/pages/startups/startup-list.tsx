import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  Building2, 
  Search, 
  Filter, 
  Plus, 
  Eye, 
  BarChart3,
  Calendar,
  MapPin,
  IndianRupee,
  Users,
  Trash2,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { startupsApi } from '@/services/api'
import { useAuth } from '@/hooks/use-auth'
import { useToast } from '@/hooks/use-toast'
import { StartupSubmission, StartupFilters } from '@/types'
import { formatCurrency, formatDate, getStatusColor, capitalizeFirst, formatINR } from '@/utils'

export function StartupListPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState<StartupFilters>({})
  const [page, setPage] = useState(1)

  const isFounder = user?.role === 'founder'

  const { data, isLoading, error } = useQuery({
    queryKey: ['startups', { search, filters, page, isFounder }],
    queryFn: () => isFounder 
      ? startupsApi.list({ page, per_page: 12 }) // Founders see their own startups
      : startupsApi.list({ // Investors/analysts see all with filters
          page,
          per_page: 12,
          search: search || undefined,
          industry: filters.industry,
          funding_stage: filters.funding_stage,
          status: filters.status,
        }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => startupsApi.delete(id),
    onSuccess: () => {
      toast({ title: 'Startup deleted', variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['startups'] })
    },
    onError: (error) => {
      toast({ title: 'Error deleting startup', description: error.message, variant: 'destructive' })
    },
  })

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this startup?')) {
      deleteMutation.mutate(id)
    }
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <Building2 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Failed to load startups</h3>
          <p className="text-muted-foreground mb-4">
            There was an error loading the startup data.
          </p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

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
                {isFounder ? 'My Startups' : (
                  <>
                    Startup
                    <span className="block bg-gradient-to-r from-yellow-200 via-pink-200 to-purple-200 bg-clip-text text-transparent">
                      Portfolio
                    </span>
                  </>
                )}
              </h1>
              <p className="text-lg md:text-xl text-white/90 max-w-2xl mb-6">
                {isFounder 
                  ? 'Manage your startup submissions and track analysis progress'
                  : 'Discover and analyze promising startup opportunities'
                }
              </p>
              
              {/* CTA Button */}
              {isFounder && (
                <Button 
                  size="lg" 
                  className="bg-white text-purple-600 hover:bg-white/90 shadow-xl hover:shadow-2xl transition-all duration-300 font-semibold"
                  asChild
                >
                  <Link to="/submit">
                    <Plus className="w-5 h-5 mr-2" />
                    Submit New Startup
                  </Link>
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Filters - only for non-founders */}
        {!isFounder && (
          <Card className="border-none shadow-lg">
            <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950">
              <CardTitle className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Search & Filter
              </CardTitle>
              <CardDescription className="text-sm mt-1">
                Find the perfect startup for your portfolio
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="Search startups by name, industry, or location..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      className="pl-10 border-gray-200 dark:border-gray-800 focus:border-purple-400"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Select
                    onValueChange={(value) => 
                      setFilters(prev => ({ ...prev, industry: value ? [value] : undefined }))
                    }
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Industry" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fintech">FinTech</SelectItem>
                      <SelectItem value="healthtech">HealthTech</SelectItem>
                      <SelectItem value="edtech">EdTech</SelectItem>
                      <SelectItem value="enterprise_software">Enterprise</SelectItem>
                      <SelectItem value="consumer_apps">Consumer</SelectItem>
                      <SelectItem value="ai_ml">AI/ML</SelectItem>
                    </SelectContent>
                  </Select>
                  
                  <Select
                    onValueChange={(value) => 
                      setFilters(prev => ({ ...prev, funding_stage: value ? [value] : undefined }))
                    }
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Stage" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pre_seed">Pre-Seed</SelectItem>
                      <SelectItem value="seed">Seed</SelectItem>
                      <SelectItem value="series_a">Series A</SelectItem>
                      <SelectItem value="series_b">Series B</SelectItem>
                      <SelectItem value="series_c">Series C</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Startup Grid */}
        {isLoading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="border-none shadow-lg animate-pulse">
                <CardHeader className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-200 to-blue-200 dark:from-purple-800 dark:to-blue-800 rounded-xl"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-5 bg-gray-200 dark:bg-gray-800 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 dark:bg-gray-800 rounded w-1/2"></div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="h-4 bg-gray-200 dark:bg-gray-800 rounded"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-800 rounded w-2/3"></div>
                  <div className="h-10 bg-gray-200 dark:bg-gray-800 rounded"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (!Array.isArray(data?.data) || data.data.length === 0) ? (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 rounded-full mb-4">
              <Building2 className="w-10 h-10 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">No startups found</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
              {search || Object.keys(filters).length > 0
                ? 'Try adjusting your search criteria or filters'
                : isFounder 
                  ? 'Submit your first startup to get started on your journey'
                  : 'No startups have been submitted yet. Check back soon!'
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
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {(data?.data ?? []).map((startup: StartupSubmission) => (
              <Card key={startup.id} className="relative border-none shadow-lg hover:shadow-2xl transition-all duration-300 group overflow-hidden">
                {/* Gradient Border Effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{ padding: '2px' }}>
                  <div className="absolute inset-[2px] bg-white dark:bg-gray-900 rounded-xl"></div>
                </div>
                
                {/* Card Content */}
                <div className="relative">
                  <CardHeader className="pb-3 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30">
                    <div className="flex items-start gap-3">
                      {/* Logo */}
                      {startup.company_info.logo_url ? (
                        <img 
                          src={startup.company_info.logo_url} 
                          alt={`${startup.company_info.name} logo`}
                          className="w-16 h-16 rounded-xl object-contain border-2 border-white dark:border-gray-800 bg-white shadow-md flex-shrink-0"
                        />
                      ) : (
                        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                          <span className="text-2xl font-black text-white">
                            {startup.company_info.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}
                      
                      {/* Title & Status */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <CardTitle className="text-lg font-bold group-hover:bg-gradient-to-r group-hover:from-purple-600 group-hover:to-blue-600 group-hover:bg-clip-text group-hover:text-transparent transition-all truncate">
                            {startup.company_info.name}
                          </CardTitle>
                          <Badge variant="secondary" className={`flex-shrink-0 text-xs ${getStatusColor(startup.status)}`}>
                            {capitalizeFirst(startup.status)}
                          </Badge>
                        </div>
                        <CardDescription className="text-sm capitalize font-medium">
                          {capitalizeFirst(startup.company_info.industry.replace('_', ' '))}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4 pt-4">
                    {/* Description */}
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 min-h-[40px]">
                      {startup.company_info.description}
                    </p>
                    
                    {/* Metadata */}
                    <div className="space-y-2 py-2 border-t border-gray-100 dark:border-gray-800">
                      <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                        <MapPin className="w-3.5 h-3.5 flex-shrink-0 text-purple-500" />
                        <span className="truncate">{startup.company_info.location}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                        <Users className="w-3.5 h-3.5 flex-shrink-0 text-blue-500" />
                        <span>{startup.company_info.employee_count || 'N/A'} employees</span>
                      </div>
                      {startup.company_info.funding_seeking && (
                        <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                          <IndianRupee className="w-3.5 h-3.5 flex-shrink-0 text-cyan-500" />
                          <span className="truncate">Seeking {formatINR(startup.company_info.funding_seeking)}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                        <Calendar className="w-3.5 h-3.5 flex-shrink-0 text-purple-500" />
                        <span>{formatDate(startup.submission_timestamp)}</span>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-2 pt-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1 border-purple-200 hover:bg-purple-50 hover:border-purple-300 dark:border-purple-800 dark:hover:bg-purple-950" 
                        asChild
                      >
                        <Link to={`/startups/${startup.id}`}>
                          <Eye className="w-4 h-4 mr-2" />
                          Details
                        </Link>
                      </Button>
                      
                      {startup.analysis_completed ? (
                        <Button 
                          size="sm" 
                          className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-md" 
                          asChild
                        >
                          <Link to={`/startups/${startup.id}/analysis`}>
                            <BarChart3 className="w-4 h-4 mr-2" />
                            Analysis
                          </Link>
                        </Button>
                      ) : (
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="flex-1 border-gray-200 dark:border-gray-800"
                          disabled
                        >
                          <BarChart3 className="w-4 h-4 mr-2 opacity-50" />
                          Pending
                        </Button>
                      )}
                      
                      {isFounder && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="px-2 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950"
                          onClick={() => handleDelete(startup.id)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="flex justify-center items-center gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="border-gray-200 dark:border-gray-800"
            >
              Previous
            </Button>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-sm font-semibold">
                Page {page} of {data.total_pages}
              </Badge>
            </div>
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
              disabled={page === data.total_pages}
              className="border-gray-200 dark:border-gray-800"
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
