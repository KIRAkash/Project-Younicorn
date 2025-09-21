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

export function AnalysisPage() {
  const { id } = useParams<{ id: string }>()

  const { data: startup } = useQuery({
    queryKey: ['startup', id],
    queryFn: () => startupsApi.get(id!),
    enabled: !!id,
  })

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses', id],
    queryFn: () => analysisApi.list({ startup_id: id }),
    enabled: !!id,
  })

  const latestAnalysis = analyses?.data?.[0]

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

  const investabilityScore = latestAnalysis.investability_score

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

      <Tabs defaultValue="summary" className="space-y-6">
        <TabsList>
          <TabsTrigger value="summary">Executive Summary</TabsTrigger>
          <TabsTrigger value="detailed">Detailed Analysis</TabsTrigger>
          <TabsTrigger value="risks">Risks & Opportunities</TabsTrigger>
          <TabsTrigger value="sources">Sources & Traceability</TabsTrigger>
          <TabsTrigger value="chat">AI Co-pilot</TabsTrigger>
        </TabsList>

        <TabsContent value="summary" className="space-y-6">
          {/* Executive Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Executive Summary</CardTitle>
              <CardDescription>
                AI-generated investment overview and recommendation
              </CardDescription>
            </CardHeader>
            <CardContent>
              {latestAnalysis.executive_summary ? (
                <ReactMarkdown className="prose prose-sm max-w-none">
                  {latestAnalysis.executive_summary}
                </ReactMarkdown>
              ) : (
                <p className="text-muted-foreground">Executive summary not available</p>
              )}
            </CardContent>
          </Card>

          {/* Key Insights */}
          {latestAnalysis.key_insights?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Key Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {latestAnalysis.key_insights.map((insight, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                      <span>{insight}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Investment Recommendation */}
          {investabilityScore && (
            <Card>
              <CardHeader>
                <CardTitle>Investment Recommendation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 mb-4">
                  <Badge 
                    className={`${getInvestmentRecommendationColor(investabilityScore.investment_recommendation)} text-lg px-4 py-2`}
                  >
                    {investabilityScore.investment_recommendation}
                  </Badge>
                  <div className="text-sm text-muted-foreground">
                    Confidence: {(investabilityScore.confidence_level * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <h4 className="font-medium mb-2">Score Breakdown</h4>
                    <div className="space-y-2">
                      {Object.entries(investabilityScore.score_weights).map(([component, weight]) => (
                        <div key={component} className="flex justify-between text-sm">
                          <span className="capitalize">{component}</span>
                          <span>{(weight * 100).toFixed(0)}% weight</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="detailed" className="space-y-6">
          {/* Detailed Agent Analyses */}
          {Object.entries(latestAnalysis.agent_analyses || {}).map(([agentType, analysis]) => (
            <Card key={agentType}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="capitalize flex items-center gap-2">
                      {agentType === 'team' && <Users className="w-5 h-5" />}
                      {agentType === 'market' && <TrendingUp className="w-5 h-5" />}
                      {agentType === 'product' && <Target className="w-5 h-5" />}
                      {agentType === 'competition' && <Shield className="w-5 h-5" />}
                      {agentType.replace('_', ' ')} Analysis
                    </CardTitle>
                    <CardDescription>
                      Confidence: {(analysis.confidence_level * 100).toFixed(0)}%
                    </CardDescription>
                  </div>
                  <Badge className={getScoreColor(analysis.score)}>
                    {analysis.score.toFixed(1)}/10
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Summary</h4>
                  <p className="text-muted-foreground">{analysis.summary}</p>
                </div>

                <Separator />

                <div>
                  <h4 className="font-medium mb-2">Detailed Analysis</h4>
                  <ReactMarkdown className="prose prose-sm max-w-none">
                    {analysis.detailed_analysis}
                  </ReactMarkdown>
                </div>

                {analysis.key_findings?.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="font-medium mb-2">Key Findings</h4>
                      <ul className="space-y-1">
                        {analysis.key_findings.map((finding, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm">{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </>
                )}

                {analysis.supporting_evidence?.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="font-medium mb-2">Supporting Evidence</h4>
                      <ul className="space-y-1">
                        {analysis.supporting_evidence.map((evidence, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <div className="w-2 h-2 bg-muted-foreground rounded-full mt-2 flex-shrink-0" />
                            <span className="text-sm text-muted-foreground">{evidence}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="risks" className="space-y-6">
          {/* Risks and Opportunities */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-danger-600">
                  <AlertTriangle className="w-5 h-5" />
                  Risks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {latestAnalysis.risks_opportunities
                    ?.filter(item => item.type === 'risk')
                    .map((risk, index) => (
                      <div key={index} className="p-4 border border-danger-200 bg-danger-50 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-danger-800">{risk.title}</h4>
                          <Badge variant="destructive" className="text-xs">
                            {risk.level}
                          </Badge>
                        </div>
                        <p className="text-sm text-danger-700 mb-2">{risk.description}</p>
                        <p className="text-xs text-danger-600">
                          <strong>Impact:</strong> {risk.impact}
                        </p>
                        {risk.mitigation && (
                          <p className="text-xs text-danger-600 mt-1">
                            <strong>Mitigation:</strong> {risk.mitigation}
                          </p>
                        )}
                      </div>
                    )) || (
                    <p className="text-muted-foreground text-center py-8">No risks identified</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-success-600">
                  <TrendingUp className="w-5 h-5" />
                  Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {latestAnalysis.risks_opportunities
                    ?.filter(item => item.type === 'opportunity')
                    .map((opportunity, index) => (
                      <div key={index} className="p-4 border border-success-200 bg-success-50 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-success-800">{opportunity.title}</h4>
                          <Badge variant="success" className="text-xs">
                            {opportunity.level}
                          </Badge>
                        </div>
                        <p className="text-sm text-success-700 mb-2">{opportunity.description}</p>
                        <p className="text-xs text-success-600">
                          <strong>Impact:</strong> {opportunity.impact}
                        </p>
                      </div>
                    )) || (
                    <p className="text-muted-foreground text-center py-8">No opportunities identified</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="sources" className="space-y-6">
          {/* Sources and Citations */}
          <Card>
            <CardHeader>
              <CardTitle>Sources & Citations</CardTitle>
              <CardDescription>
                All sources used in the analysis with traceability
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.values(latestAnalysis.agent_analyses || {})
                  .flatMap(analysis => analysis.sources || [])
                  .map((source, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium">{source.title}</h4>
                          {source.url && (
                            <a 
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-primary hover:underline flex items-center gap-1 mt-1"
                            >
                              {source.domain || source.url}
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                          {source.excerpt && (
                            <p className="text-sm text-muted-foreground mt-2 italic">
                              "{source.excerpt}"
                            </p>
                          )}
                        </div>
                        {source.confidence_score && (
                          <Badge variant="outline">
                            {(source.confidence_score * 100).toFixed(0)}% confidence
                          </Badge>
                        )}
                      </div>
                    </div>
                  )) || (
                  <p className="text-muted-foreground text-center py-8">No sources available</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chat" className="space-y-6">
          {/* AI Co-pilot Chat */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                AI Co-pilot
              </CardTitle>
              <CardDescription>
                Ask questions about the analysis and get detailed answers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-semibold mb-2">Coming Soon</h3>
                <p>Interactive AI co-pilot will be available in the next update</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
