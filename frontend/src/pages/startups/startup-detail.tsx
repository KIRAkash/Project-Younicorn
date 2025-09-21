import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  ArrowLeft, 
  Building2, 
  MapPin, 
  Users, 
  DollarSign, 
  Calendar,
  Globe,
  FileText,
  Download,
  BarChart3,
  Play,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { startupsApi, analysisApi } from '@/services/api'
import { useAuth } from '@/hooks/use-auth'
import { formatCurrency, formatDate, formatFileSize, getStatusColor, capitalizeFirst } from '@/utils'

export function StartupDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()

  const { data: startup, isLoading } = useQuery({
    queryKey: ['startup', id],
    queryFn: () => startupsApi.get(id!),
    enabled: !!id,
  })

  const { data: analyses } = useQuery({
    queryKey: ['analyses', id],
    queryFn: () => analysisApi.list({ startup_id: id }),
    enabled: !!id,
  })

  const isFounder = user?.role === 'founder'
  const canAnalyze = !isFounder && startup && !startup.analysis_requested

  const handleStartAnalysis = async () => {
    if (!id) return
    try {
      await analysisApi.create(id)
      // Refresh the data
      window.location.reload()
    } catch (error) {
      console.error('Failed to start analysis:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-1/4"></div>
          <div className="h-64 bg-muted rounded"></div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="h-48 bg-muted rounded"></div>
            <div className="h-48 bg-muted rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!startup) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <Building2 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Startup not found</h3>
          <p className="text-muted-foreground mb-4">
            The startup you're looking for doesn't exist or you don't have access to it.
          </p>
          <Button asChild>
            <Link to="/startups">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Startups
            </Link>
          </Button>
        </div>
      </div>
    )
  }

  const latestAnalysis = analyses?.data?.[0]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/startups">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Link>
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-minerva-100 rounded-xl flex items-center justify-center">
              <Building2 className="w-8 h-8 text-minerva-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">{startup.company_info.name}</h1>
              <p className="text-muted-foreground">
                {capitalizeFirst(startup.company_info.industry.replace('_', ' '))} • {' '}
                {capitalizeFirst(startup.company_info.funding_stage.replace('_', ' '))}
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getStatusColor(startup.status)}>
            {capitalizeFirst(startup.status)}
          </Badge>
          {canAnalyze && (
            <Button onClick={handleStartAnalysis}>
              <Play className="w-4 h-4 mr-2" />
              Start Analysis
            </Button>
          )}
          {latestAnalysis && (
            <Button variant="outline" asChild>
              <Link to={`/startups/${id}/analysis`}>
                <BarChart3 className="w-4 h-4 mr-2" />
                View Analysis
              </Link>
            </Button>
          )}
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="team">Team</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Company Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Company Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-6">
                {startup.company_info.description}
              </p>
              
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div className="flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Location</p>
                    <p className="text-sm text-muted-foreground">
                      {startup.company_info.location}
                    </p>
                  </div>
                </div>
                
                {startup.company_info.website_url && (
                  <div className="flex items-center gap-3">
                    <Globe className="w-5 h-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Website</p>
                      <a 
                        href={startup.company_info.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary hover:underline"
                      >
                        {startup.company_info.website_url}
                      </a>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Team Size</p>
                    <p className="text-sm text-muted-foreground">
                      {startup.company_info.employee_count || 'Not specified'} employees
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Founded</p>
                    <p className="text-sm text-muted-foreground">
                      {startup.company_info.founded_date 
                        ? formatDate(startup.company_info.founded_date)
                        : 'Not specified'
                      }
                    </p>
                  </div>
                </div>
                
                {startup.company_info.funding_raised && (
                  <div className="flex items-center gap-3">
                    <DollarSign className="w-5 h-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Funding Raised</p>
                      <p className="text-sm text-muted-foreground">
                        {formatCurrency(startup.company_info.funding_raised)}
                      </p>
                    </div>
                  </div>
                )}
                
                {startup.company_info.funding_seeking && (
                  <div className="flex items-center gap-3">
                    <DollarSign className="w-5 h-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Seeking</p>
                      <p className="text-sm text-muted-foreground">
                        {formatCurrency(startup.company_info.funding_seeking)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Key Metrics */}
          {startup.metadata.key_metrics && Object.keys(startup.metadata.key_metrics).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Key Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {Object.entries(startup.metadata.key_metrics).map(([key, value]) => (
                    <div key={key} className="p-4 border rounded-lg">
                      <p className="font-medium capitalize">{key.replace('_', ' ')}</p>
                      <p className="text-2xl font-bold text-primary">{String(value)}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Traction Highlights */}
          {startup.metadata.traction_highlights?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Traction Highlights</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {startup.metadata.traction_highlights.map((highlight, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="team" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {startup.founders.map((founder, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-minerva-100 rounded-full flex items-center justify-center">
                      <Users className="w-6 h-6 text-minerva-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{founder.name}</CardTitle>
                      <CardDescription>{founder.role}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {founder.bio && (
                    <p className="text-sm text-muted-foreground mb-4">{founder.bio}</p>
                  )}
                  
                  {founder.previous_experience?.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Experience</h4>
                      <ul className="space-y-1">
                        {founder.previous_experience.map((exp, i) => (
                          <li key={i} className="text-sm text-muted-foreground">• {exp}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {founder.education?.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Education</h4>
                      <ul className="space-y-1">
                        {founder.education.map((edu, i) => (
                          <li key={i} className="text-sm text-muted-foreground">• {edu}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="documents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Documents</CardTitle>
              <CardDescription>
                Documents submitted with this startup application
              </CardDescription>
            </CardHeader>
            <CardContent>
              {startup.documents.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No documents uploaded</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {startup.documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <FileText className="w-8 h-8 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{doc.filename}</p>
                          <p className="text-sm text-muted-foreground">
                            {capitalizeFirst(doc.document_type.replace('_', ' '))} • {formatFileSize(doc.file_size)}
                          </p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm" asChild>
                        <a href={startupsApi.downloadDocument(startup.id, doc.id)} download>
                          <Download className="w-4 h-4 mr-2" />
                          Download
                        </a>
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Activity Timeline</CardTitle>
              <CardDescription>
                Recent activity and updates for this startup
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2" />
                  <div>
                    <p className="font-medium">Startup submitted</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(startup.submission_timestamp)}
                    </p>
                  </div>
                </div>
                
                {startup.analysis_started && (
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-warning-500 rounded-full mt-2" />
                    <div>
                      <p className="font-medium">Analysis started</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(startup.analysis_started)}
                      </p>
                    </div>
                  </div>
                )}
                
                {startup.analysis_completed && (
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-success-500 rounded-full mt-2" />
                    <div>
                      <p className="font-medium">Analysis completed</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(startup.analysis_completed)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
