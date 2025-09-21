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
  DollarSign,
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
import { formatCurrency, formatDate, getStatusColor, capitalizeFirst } from '@/utils'

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
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isFounder ? 'My Startups' : 'Startup Portfolio'}
          </h1>
          <p className="text-muted-foreground">
            {isFounder 
              ? 'Manage your startup submissions and track analysis progress'
              : 'Discover and analyze promising startup opportunities'
            }
          </p>
        </div>
        {isFounder && (
          <Button asChild>
            <Link to="/submit">
              <Plus className="w-4 h-4 mr-2" />
              Submit New Startup
            </Link>
          </Button>
        )}
      </div>

      {/* Filters - only for non-founders */}
      {!isFounder && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Search & Filter</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                  <Input
                    placeholder="Search startups..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="pl-10"
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

                <Button variant="outline" size="icon">
                  <Filter className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Startup Grid */}
      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded w-3/4"></div>
                <div className="h-4 bg-muted rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-4 bg-muted rounded"></div>
                  <div className="h-4 bg-muted rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (!Array.isArray(data?.data) || data.data.length === 0) ? (
        <div className="text-center py-12">
          <Building2 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">No startups found</h3>
          <p className="text-muted-foreground mb-4">
            {search || Object.keys(filters).length > 0
              ? 'Try adjusting your search criteria'
              : isFounder 
                ? 'Submit your first startup to get started'
                : 'No startups have been submitted yet'
            }
          </p>
          {isFounder && (
            <Button asChild>
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
            <Card key={startup.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-minerva-100 rounded-lg flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-minerva-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{startup.company_info.name}</CardTitle>
                      <CardDescription>
                        {capitalizeFirst(startup.company_info.industry.replace('_', ' '))}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge className={getStatusColor(startup.status)}>
                    {capitalizeFirst(startup.status)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                  {startup.company_info.description}
                </p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="w-4 h-4" />
                    {startup.company_info.location}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Users className="w-4 h-4" />
                    {startup.company_info.employee_count || 'N/A'} employees
                  </div>
                  {startup.company_info.funding_seeking && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <DollarSign className="w-4 h-4" />
                      Seeking {formatCurrency(startup.company_info.funding_seeking)}
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    {formatDate(startup.submission_timestamp)}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" className="flex-1" asChild>
                    <Link to={`/startups/${startup.id}`}>
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </Link>
                  </Button>
                  {startup.analysis_completed && (
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/startups/${startup.id}/analysis`}>
                        <BarChart3 className="w-4 h-4" />
                      </Link>
                    </Button>
                  )}
                  {isFounder && (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(startup.id)}
                      disabled={deleteMutation.isLoading}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="flex items-center px-4 text-sm text-muted-foreground">
            Page {page} of {data.total_pages}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
            disabled={page === data.total_pages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
