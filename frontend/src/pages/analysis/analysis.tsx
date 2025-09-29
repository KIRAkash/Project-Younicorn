import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  ArrowLeft, 
  BarChart3, 
  Users, 
  TrendingUp, 
  Shield, 
  Target,
  ExternalLink,
  MessageSquare,
  Download,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { analysisApi, startupsApi } from '@/services/api'
import { getScoreColor, getScoreLabel, getInvestmentRecommendationColor, formatDate } from '@/utils'

// Component to render analysis data with markdown support
function AnalysisRenderer({ data, title, icon: Icon, score }: { 
  data: any, 
  title: string, 
  icon: any, 
  score?: number 
}) {
  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Icon className="w-5 h-5" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No analysis data available</p>
        </CardContent>
      </Card>
    )
  }

  const renderValue = (_key: string, value: any): React.ReactNode => {
    if (value === null || value === undefined) return null
    
    if (typeof value === 'string') {
      // Check if it looks like markdown or has line breaks
      if (value.includes('\n') || value.includes('**') || value.includes('##') || value.includes('*')) {
        return (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{value}</ReactMarkdown>
          </div>
        )
      }
      return <p className="text-sm">{value}</p>
    }
    
    if (typeof value === 'number') {
      return <span className="font-mono text-sm">{value}</span>
    }
    
    if (typeof value === 'boolean') {
      return <Badge variant={value ? 'default' : 'secondary'}>{value ? 'Yes' : 'No'}</Badge>
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) return <p className="text-muted-foreground text-sm">None</p>
      return (
        <ul className="space-y-1">
          {value.map((item, index) => (
            <li key={index} className="flex items-start gap-2">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm">{typeof item === 'string' ? item : JSON.stringify(item)}</span>
            </li>
          ))}
        </ul>
      )
    }
    
    if (typeof value === 'object') {
      return (
        <div className="space-y-2">
          {Object.entries(value).map(([subKey, subValue]) => (
            <div key={subKey} className="border-l-2 border-muted pl-4">
              <h5 className="font-medium text-sm capitalize mb-1">{subKey.replace(/_/g, ' ')}</h5>
              {renderValue(subKey, subValue)}
            </div>
          ))}
        </div>
      )
    }
    
    return <pre className="text-xs bg-muted p-2 rounded overflow-auto">{JSON.stringify(value, null, 2)}</pre>
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Icon className="w-5 h-5" />
              {title}
            </CardTitle>
            <CardDescription>AI-generated analysis</CardDescription>
          </div>
          {score !== undefined && (
            <Badge className={getScoreColor(score)}>
              {score.toFixed(1)}/10
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {Object.entries(data).map(([key, value]) => {
          if (value === null || value === undefined) return null
          
          return (
            <div key={key}>
              <h4 className="font-medium mb-2 capitalize">{key.replace(/_/g, ' ')}</h4>
              {renderValue(key, value)}
              <Separator className="mt-4" />
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

export function AnalysisPage() {
  const { id } = useParams<{ id: string }>()

  const { data: startup } = useQuery({
    queryKey: ['startup', id],
    queryFn: () => startupsApi.get(id!),
    enabled: !!id,
  })

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses', id],
    queryFn: () => {
      console.log('Calling analysisApi.list with startup_id:', id)
      return analysisApi.list({ startup_id: id })
    },
    enabled: !!id,
  })

  const latestAnalysis = analyses?.data?.[0]
  
  // Debug logging
  console.log('Analysis API Response:', analyses)
  console.log('Latest Analysis:', latestAnalysis)
  console.log('Startup ID:', id)

  // Parse individual agent analysis columns from BigQuery schema
  const parseAnalysis = (data: any) => {
    if (!data) return null
    if (typeof data === 'string') {
      try {
        return JSON.parse(data)
      } catch {
        return null
      }
    }
    return data
  }

  const teamAnalysis = parseAnalysis(latestAnalysis?.team_analysis)
  const marketAnalysis = parseAnalysis(latestAnalysis?.market_analysis)
  const productAnalysis = parseAnalysis(latestAnalysis?.product_analysis)
  const competitionAnalysis = parseAnalysis(latestAnalysis?.competition_analysis)
  const synthesisAnalysis = parseAnalysis(latestAnalysis?.synthesis_analysis)

  // Note: Now using individual analysis columns from BigQuery schema

  // Create investability score object for the UI using BigQuery fields
  const investabilityScore = latestAnalysis?.investability_score || {
    overall_score: latestAnalysis?.overall_score || 0,
    team_score: latestAnalysis?.team_score || 0,
    market_score: latestAnalysis?.market_score || 0, 
    product_score: latestAnalysis?.product_score || 0,
    competition_score: latestAnalysis?.competition_score || 0,
    investment_recommendation: latestAnalysis?.investment_recommendation || 'PENDING',
    confidence_level: latestAnalysis?.confidence_level || 0.5,
    score_weights: {}
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-1/4"></div>
          <div className="grid gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded"></div>
            ))}
          </div>
          <div className="h-96 bg-muted rounded"></div>
        </div>
      </div>
    )
  }

  if (!latestAnalysis) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <BarChart3 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">No analysis available</h3>
          <p className="text-muted-foreground mb-4">
            This startup hasn't been analyzed yet or you don't have access to the analysis.
          </p>
          <Button asChild>
            <Link to={`/startups/${id}`}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Startup
            </Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/startups/${id}`}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Startup
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Investment Analysis</h1>
            <p className="text-muted-foreground">
              {startup?.company_info.name} • Generated {formatDate(latestAnalysis.started_at || '')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getInvestmentRecommendationColor(investabilityScore?.investment_recommendation || '')}>
            {investabilityScore?.investment_recommendation || 'Pending'}
          </Badge>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Overall Score Cards */}
      {investabilityScore && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Overall Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                <span className={getScoreColor(investabilityScore.overall_score)}>
                  {investabilityScore.overall_score.toFixed(1)}
                </span>
                <span className="text-lg text-muted-foreground">/10</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {getScoreLabel(investabilityScore.overall_score)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="w-4 h-4" />
                Team
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                <span className={getScoreColor(investabilityScore.team_score)}>
                  {investabilityScore.team_score.toFixed(1)}
                </span>
              </div>
              <Progress value={investabilityScore.team_score * 10} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Market
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                <span className={getScoreColor(investabilityScore.market_score)}>
                  {investabilityScore.market_score.toFixed(1)}
                </span>
              </div>
              <Progress value={investabilityScore.market_score * 10} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Target className="w-4 h-4" />
                Product
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                <span className={getScoreColor(investabilityScore.product_score)}>
                  {investabilityScore.product_score.toFixed(1)}
                </span>
              </div>
              <Progress value={investabilityScore.product_score * 10} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Competition
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                <span className={getScoreColor(investabilityScore.competition_score)}>
                  {investabilityScore.competition_score.toFixed(1)}
                </span>
              </div>
              <Progress value={investabilityScore.competition_score * 10} className="mt-2" />
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="team" className="space-y-6">
        <TabsList>
          <TabsTrigger value="team">Team Analysis</TabsTrigger>
          <TabsTrigger value="market">Market Analysis</TabsTrigger>
          <TabsTrigger value="product">Product Analysis</TabsTrigger>
          <TabsTrigger value="competition">Competition Analysis</TabsTrigger>
          <TabsTrigger value="synthesis">Final Verdict</TabsTrigger>
        </TabsList>

        <TabsContent value="team" className="space-y-6">
          <AnalysisRenderer 
            data={teamAnalysis} 
            title="Team Analysis" 
            icon={Users} 
            score={latestAnalysis?.team_score}
          />
        </TabsContent>

        <TabsContent value="market" className="space-y-6">
          <AnalysisRenderer 
            data={marketAnalysis} 
            title="Market Analysis" 
            icon={TrendingUp} 
            score={latestAnalysis?.market_score}
          />
        </TabsContent>

        <TabsContent value="product" className="space-y-6">
          <AnalysisRenderer 
            data={productAnalysis} 
            title="Product Analysis" 
            icon={Target} 
            score={latestAnalysis?.product_score}
          />
        </TabsContent>

        <TabsContent value="competition" className="space-y-6">
          <AnalysisRenderer 
            data={competitionAnalysis} 
            title="Competition Analysis" 
            icon={Shield} 
            score={latestAnalysis?.competition_score}
          />
        </TabsContent>

        <TabsContent value="synthesis" className="space-y-6">
          <AnalysisRenderer 
            data={synthesisAnalysis} 
            title="Final Verdict" 
            icon={BarChart3} 
            score={latestAnalysis?.overall_score}
          />

          {/* Investment Summary Card */}
          {investabilityScore && (
            <Card>
              <CardHeader>
                <CardTitle>Investment Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 mb-4">
                  <Badge 
                    className={`${getInvestmentRecommendationColor(investabilityScore.investment_recommendation)} text-lg px-4 py-2`}
                  >
                    {investabilityScore.investment_recommendation}
                  </Badge>
                  <div className="text-sm text-muted-foreground">
                    Overall Score: <span className="font-medium">{investabilityScore.overall_score.toFixed(1)}/10</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Confidence: {(investabilityScore.confidence_level * 100).toFixed(0)}%
                  </div>
                </div>
                {latestAnalysis?.executive_summary && (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{latestAnalysis.executive_summary}</ReactMarkdown>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

      </Tabs>
    </div>
  )
}
