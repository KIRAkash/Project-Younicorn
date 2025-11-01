import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { useState } from 'react'
import {
  ArrowLeft,
  BarChart3,
  Download,
  Users,
  TrendingUp,
  Package,
  Target,
  CheckCircle,
  Shield,
  Eye,
  Star,
  X,
  CalendarDays,
  Share2,
  Building2,
  Lightbulb,
  AlertTriangle,
  ThumbsUp,
  ThumbsDown,
  Zap,
  Activity,
  Compass,
  Globe,
  Rocket,
  LineChart,
  DollarSign,
  MessageSquare,
  Award,
  Lock,
  TrendingDown,
  FileText,
  Clock,
  CheckSquare,
  RefreshCw,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { analysisApi, startupStatusApi, startupsApi } from '@/services/api'
import { getScoreColor, getScoreLabel, getInvestmentRecommendationColor } from '@/utils'
import { useToast } from '@/hooks/use-toast'
import { BeaconProvider, BeaconChat, BeaconButton, BeaconSectionIcon, BeaconSubsectionIcon } from '@/components/beacon'

// Helper function to extract subsection headings from analysis data
function extractSubsections(data: any): string[] {
  if (!data || typeof data !== 'object') return [];
  
  const subsections: string[] = [];
  
  // Extract top-level keys that look like section headings
  Object.keys(data).forEach(key => {
    // Convert snake_case to Title Case
    const formatted = key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    // Filter out common non-heading keys
    if (!['score', 'agent_name', 'analysis', 'response', 'detailed_analysis'].includes(key)) {
      subsections.push(formatted);
    }
  });
  
  return subsections;
}

// Helper function to get icon for section title
function getSectionIcon(sectionTitle: string) {
  const iconMap: Record<string, any> = {
    // Team sections
    'Team Assessment': Users,
    'Key Findings': Eye,
    'Recommendations': Lightbulb,
    
    // Market sections
    'Market Analysis': Globe,
    'Market Dynamics': Activity,
    'Market Outlook': Compass,
    
    // Product sections
    'Product Overview': Package,
    'Traction & Growth': Rocket,
    'Validation & Scalability': CheckCircle,
    'Strategic Assessment': Target,
    
    // Competition sections
    'Competitive Positioning': Target,
    'Competitors': Building2,
    'Competitive Advantages': Award,
    'Strategic Outlook': Compass,
    
    // Synthesis sections
    'Investment Analysis': FileText,
    'Investment Decision': CheckSquare,
    'Market Context': Globe,
    'Next Steps': Clock,
  };
  
  return iconMap[sectionTitle] || Star;
}

// Section component with tabs for sub-headings
function SectionCarousel({ 
  sectionIndex, 
  sectionTitle, 
  items, 
  data, 
  renderValue,
  analysisType 
}: { 
  sectionIndex: number
  sectionTitle: string
  items: Array<{ title: string; key: string }>
  data: any
  renderValue: (value: any, key: string) => React.ReactNode
  analysisType?: 'team' | 'market' | 'product' | 'competition' | 'synthesis'
}) {
  const [currentIndex, setCurrentIndex] = useState(0)

  const currentItem = items[currentIndex]
  const value = data[currentItem.key]
  const SectionIcon = getSectionIcon(sectionTitle)

  return (
    <Card className="overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700">
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 p-6 border-b-4 border-blue-500">
        <div className="flex items-center justify-between">
          <h3 className="text-2xl font-black text-gray-900 dark:text-white flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
              {sectionIndex}
            </div>
            <SectionIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            {sectionTitle}
          </h3>
        </div>
      </div>
      
      <CardContent className="p-8">
        {/* Left-aligned Tabs Navigation */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            {items.map((item, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
                  index === currentIndex 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {item.title}
              </button>
            ))}
          </div>
        </div>

        {/* Current Item Content */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-1 h-6 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            <h4 className="text-xl font-bold text-gray-800 dark:text-white flex items-center">
              {currentItem.title}
              {analysisType && (
                <BeaconSubsectionIcon
                  sectionId={`${analysisType}-${currentItem.key}`}
                  sectionTitle={sectionTitle}
                  subsectionTitle={currentItem.title}
                  sectionType={analysisType}
                  sectionData={value}
                />
              )}
            </h4>
          </div>
          <div className="pl-6 border-l-2 border-gray-200 dark:border-gray-700 font-['Inter',_'system-ui',_sans-serif]">
            {renderValue(value, currentItem.key)}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Component for arrays of objects with tab navigation (nested items)
function ArrayItemTabs({ 
  items, 
  renderItem,
  getItemLabel 
}: { 
  items: any[]
  renderItem: (item: any, index: number) => React.ReactNode
  getItemLabel: (item: any, index: number) => string
}) {
  const [currentIndex, setCurrentIndex] = useState(0)

  if (items.length === 0) return null
  if (items.length === 1) return <>{renderItem(items[0], 0)}</>

  return (
    <div className="space-y-4">
      {/* Nested Item Tabs - Smaller, lighter styling to distinguish from main section tabs */}
      <div className="flex flex-wrap gap-1.5 pl-4 border-l-2 border-gray-300 dark:border-gray-600">
        {items.map((item, index) => (
          <button
            key={index}
            onClick={() => setCurrentIndex(index)}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
              index === currentIndex 
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-700' 
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
          >
            {getItemLabel(item, index)}
          </button>
        ))}
      </div>

      {/* Current Item Content */}
      <div>
        {renderItem(items[currentIndex], currentIndex)}
      </div>
    </div>
  )
}

// Component to render analysis data with structured layout and scores
function AnalysisRenderer({ data, title, icon: Icon, analysisType }: { 
  data: any, 
  title: string, 
  icon: any, 
  analysisType: 'team' | 'market' | 'product' | 'competition' | 'synthesis'
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

  const renderValue = (value: any, parentKey?: string): React.ReactNode => {
    if (value === null || value === undefined) return null
    
    if (typeof value === 'string') {
      if (value.includes('\n') || value.includes('**') || value.includes('##') || value.includes('*')) {
        return (
          <div className="prose prose-base max-w-none dark:prose-invert font-['Inter',_'system-ui',_sans-serif]">
            <ReactMarkdown>{value}</ReactMarkdown>
          </div>
        )
      }
      return <p className="text-base leading-relaxed text-gray-700 dark:text-gray-300 font-['Inter',_'system-ui',_sans-serif]">{value}</p>
    }
    
    if (typeof value === 'number') {
      return <span className="font-mono text-base font-medium text-gray-800 dark:text-gray-200">{value}</span>
    }
    
    if (typeof value === 'boolean') {
      return <Badge variant={value ? 'default' : 'secondary'}>{value ? 'Yes' : 'No'}</Badge>
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) return <p className="text-muted-foreground text-base font-['Inter',_'system-ui',_sans-serif]">None</p>
      
      // Check if array contains competitive advantage objects
      if (value.length > 0 && value[0] && typeof value[0] === 'object' && value[0].advantage_type) {
        return (
          <ArrayItemTabs
            items={value}
            getItemLabel={(advantage) => advantage.advantage_type || 'Advantage'}
            renderItem={(advantage) => (
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
                <h4 className="font-semibold text-lg text-gray-900 dark:text-white mb-2">
                  {advantage.advantage_type}
                </h4>
                <div className="space-y-2">
                  {advantage.defensibility !== undefined && (
                    <p className="text-sm">
                      <span className="font-medium text-gray-700 dark:text-gray-300">Defensibility Score:</span>{' '}
                      <span className="font-bold text-blue-600 dark:text-blue-400">{advantage.defensibility}/10</span>
                    </p>
                  )}
                  {advantage.description && (
                    <p className="text-sm text-gray-700 dark:text-gray-300">{advantage.description}</p>
                  )}
                  {advantage.sustainability && (
                    <div className="mt-2">
                      <span className="font-medium text-gray-700 dark:text-gray-300">Sustainability:</span>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{advantage.sustainability}</p>
                    </div>
                  )}
                  {advantage.evidence && Array.isArray(advantage.evidence) && advantage.evidence.length > 0 && (
                    <div className="mt-2">
                      <span className="font-medium text-gray-700 dark:text-gray-300">Evidence:</span>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        {advantage.evidence.map((item: string, evidenceIndex: number) => (
                          <li key={evidenceIndex} className="text-base text-gray-600 dark:text-gray-400 font-['Inter',_'system-ui',_sans-serif]">{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          />
        )
      }
      
      // Check if array contains competitor objects
      if (value.length > 0 && value[0] && typeof value[0] === 'object' && value[0].name && (value[0].category || value[0].threat_level)) {
        return (
          <ArrayItemTabs
            items={value}
            getItemLabel={(competitor) => competitor.name || 'Competitor'}
            renderItem={(competitor) => {
              const [logoError, setLogoError] = useState(false);
              const hasLogo = competitor.public_logo_url && !logoError;
              
              return (
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      {/* Logo or default icon */}
                      <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-white dark:bg-gray-700 p-1 border border-gray-200 dark:border-gray-600 flex-shrink-0">
                        {hasLogo ? (
                          <img 
                            src={competitor.public_logo_url} 
                            alt={`${competitor.name} logo`}
                            className="w-full h-full object-contain"
                            onError={() => setLogoError(true)}
                          />
                        ) : (
                          <Building2 className="w-6 h-6 text-gray-400 dark:text-gray-500" />
                        )}
                      </div>
                      <div>
                      {competitor.public_url ? (
                        <a 
                          href={`https://${competitor.public_url}`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="font-semibold text-lg text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          {competitor.name}
                        </a>
                      ) : (
                        <h4 className="font-semibold text-lg text-gray-900 dark:text-white">
                          {competitor.name}
                        </h4>
                      )}
                      {competitor.category && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{competitor.category}</p>
                      )}
                    </div>
                  </div>
                  {competitor.threat_level && (
                    <Badge className={competitor.threat_level === 'High' || competitor.threat_level === 'Critical' ? 'bg-red-100 text-red-800' : competitor.threat_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}>
                      {competitor.threat_level} Threat
                    </Badge>
                  )}
                </div>
                {competitor.description && (
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{competitor.description}</p>
                )}
                <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                  {competitor.funding_raised && (
                    <div><span className="font-medium">Funding:</span> ${(competitor.funding_raised / 1000000).toFixed(1)}M</div>
                  )}
                  {competitor.employee_count && (
                    <div><span className="font-medium">Employees:</span> {competitor.employee_count}</div>
                  )}
                  {competitor.founded_year && (
                    <div><span className="font-medium">Founded:</span> {competitor.founded_year}</div>
                  )}
                  {competitor.market_share && (
                    <div><span className="font-medium">Market Share:</span> {competitor.market_share}%</div>
                  )}
                </div>
                {competitor.strengths && competitor.strengths.length > 0 && (
                  <div className="mt-2">
                    <span className="font-medium text-sm text-gray-700 dark:text-gray-300">Strengths:</span>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      {competitor.strengths.map((strength: string, sIndex: number) => (
                        <li key={sIndex} className="text-sm text-gray-600 dark:text-gray-400 font-['Inter',_'system-ui',_sans-serif]">{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {competitor.weaknesses && competitor.weaknesses.length > 0 && (
                  <div className="mt-2">
                    <span className="font-medium text-sm text-gray-700 dark:text-gray-300">Weaknesses:</span>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      {competitor.weaknesses.map((weakness: string, wIndex: number) => (
                        <li key={wIndex} className="text-sm text-gray-600 dark:text-gray-400 font-['Inter',_'system-ui',_sans-serif]">{weakness}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {competitor.differentiation && (
                  <div className="mt-2">
                    <span className="font-medium text-sm text-gray-700 dark:text-gray-300">Differentiation:</span>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{competitor.differentiation}</p>
                  </div>
                )}
              </div>
              );
            }}
          />
        )
      }
      
      // Regular array of strings
      return (
        <ul className="space-y-2">
          {value.map((item, index) => (
            <li key={index} className="flex items-start gap-3">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-base leading-relaxed text-gray-700 dark:text-gray-300 font-['Inter',_'system-ui',_sans-serif]">{typeof item === 'string' ? item : JSON.stringify(item)}</span>
            </li>
          ))}
        </ul>
      )
    }
    
    if (typeof value === 'object') {
      // Special handling for TractionMetrics
      if (parentKey === 'traction_metrics') {
        return (
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
            <h5 className="font-semibold text-gray-900 dark:text-white mb-3">Traction Metrics</h5>
            <div className="grid grid-cols-2 gap-4">
              {value.total_users !== undefined && value.total_users !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Users</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{value.total_users.toLocaleString()}</p>
                </div>
              )}
              {value.monthly_active_users !== undefined && value.monthly_active_users !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Monthly Active Users</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{value.monthly_active_users.toLocaleString()}</p>
                </div>
              )}
              {value.monthly_recurring_revenue !== undefined && value.monthly_recurring_revenue !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">MRR</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">${value.monthly_recurring_revenue.toLocaleString()}</p>
                </div>
              )}
              {value.annual_recurring_revenue !== undefined && value.annual_recurring_revenue !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">ARR</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">${value.annual_recurring_revenue.toLocaleString()}</p>
                </div>
              )}
              {value.user_growth_rate !== undefined && value.user_growth_rate !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">User Growth Rate</p>
                  <p className="text-lg font-bold text-green-600 dark:text-green-400">{value.user_growth_rate}%</p>
                </div>
              )}
              {value.revenue_growth_rate !== undefined && value.revenue_growth_rate !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Revenue Growth Rate</p>
                  <p className="text-lg font-bold text-green-600 dark:text-green-400">{value.revenue_growth_rate}%</p>
                </div>
              )}
              {value.customer_acquisition_cost !== undefined && value.customer_acquisition_cost !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">CAC</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">${value.customer_acquisition_cost}</p>
                </div>
              )}
              {value.lifetime_value !== undefined && value.lifetime_value !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">LTV</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">${value.lifetime_value}</p>
                </div>
              )}
              {value.ltv_cac_ratio !== undefined && value.ltv_cac_ratio !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">LTV:CAC Ratio</p>
                  <p className="text-lg font-bold text-blue-600 dark:text-blue-400">{value.ltv_cac_ratio.toFixed(1)}:1</p>
                </div>
              )}
              {value.customer_retention_rate !== undefined && value.customer_retention_rate !== null && (
                <div className="space-y-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Retention Rate</p>
                  <p className="text-lg font-bold text-green-600 dark:text-green-400">{value.customer_retention_rate}%</p>
                </div>
              )}
            </div>
            {value.metrics_quality && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Metrics Quality:</span> {value.metrics_quality}
                </p>
              </div>
            )}
            {value.data_reliability !== undefined && (
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Data Reliability:</span> {(value.data_reliability * 100).toFixed(0)}%
                </p>
              </div>
            )}
          </div>
        )
      }
      
      // Special handling for InvestmentRecommendation, RiskAssessment, OpportunityAssessment
      if (parentKey === 'investment_recommendation' || parentKey === 'risk_assessment' || parentKey === 'opportunity_assessment') {
        return (
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-4 space-y-3">
            {Object.entries(value).map(([subKey, subValue]) => (
              <div key={subKey}>
                <h5 className="font-semibold text-sm text-gray-800 dark:text-gray-200 mb-2">
                  {subKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </h5>
                {renderValue(subValue, subKey)}
              </div>
            ))}
          </div>
        )
      }
      
      // Generic object rendering
      return (
        <div className="space-y-3">
          {Object.entries(value).map(([subKey, subValue]) => (
            <div key={subKey} className="border-l-4 border-blue-500 pl-4">
              <h5 className="font-semibold text-sm text-gray-800 dark:text-gray-200 mb-2">{subKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h5>
              {renderValue(subValue, subKey)}
            </div>
          ))}
        </div>
      )
    }
    
    return <pre className="text-xs bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-gray-200 p-3 rounded-lg overflow-auto">{JSON.stringify(value, null, 2)}</pre>
  }

  // Get scores based on analysis type
  const getScores = () => {
    switch (analysisType) {
      case 'team':
        return [
          { label: 'Overall Score', value: data.overall_score, key: 'overall' },
          { label: 'Founder Market Fit', value: data.founder_market_fit_score, key: 'founder_fit' },
          { label: 'Team Completeness', value: data.team_completeness_score, key: 'completeness' },
          { label: 'Experience', value: data.experience_score, key: 'experience' },
          { label: 'Leadership', value: data.leadership_score, key: 'leadership' }
        ]
      case 'market':
        return [
          { label: 'Overall Score', value: data.overall_score, key: 'overall' },
          { label: 'Market Size', value: data.market_size_score, key: 'size' },
          { label: 'Market Growth', value: data.market_growth_score, key: 'growth' },
          { label: 'Market Timing', value: data.market_timing_score, key: 'timing' },
          { label: 'Market Access', value: data.market_accessibility_score, key: 'access' }
        ]
      case 'product':
        return [
          { label: 'Overall Score', value: data.overall_score, key: 'overall' },
          { label: 'Product Market Fit', value: data.product_market_fit_score, key: 'pmf' },
          { label: 'Traction', value: data.traction_score, key: 'traction' },
          { label: 'Scalability', value: data.scalability_score, key: 'scalability' },
          { label: 'Differentiation', value: data.differentiation_score, key: 'differentiation' }
        ]
      case 'competition':
        return [
          { label: 'Overall Score', value: data.overall_score, key: 'overall' },
          { label: 'Competitive Position', value: data.competitive_position_score, key: 'position' },
          { label: 'Moat Strength', value: data.moat_strength_score, key: 'moat' },
          { label: 'Differentiation', value: data.differentiation_score, key: 'differentiation' }
        ]
      case 'synthesis':
        return [
          { label: 'Overall Score', value: data.overall_investability_score, key: 'overall' },
          { label: 'Team Score', value: data.team_score, key: 'team' },
          { label: 'Market Score', value: data.market_score, key: 'market' },
          { label: 'Product Score', value: data.product_score, key: 'product' },
          { label: 'Competition Score', value: data.competition_score, key: 'competition' }
        ]
      default:
        return []
    }
  }

  // Get structured sections with grouping based on analysis type
  const getSections = () => {
    switch (analysisType) {
      case 'team':
        return [
          { title: 'Summary', key: 'executive_summary', isMain: true },
          { section: 'Team Assessment', items: [
            { title: 'Founder Analysis', key: 'founder_analysis' },
            { title: 'Team Composition', key: 'team_composition' },
            { title: 'Experience Assessment', key: 'experience_assessment' },
            { title: 'Leadership Evaluation', key: 'leadership_evaluation' }
          ]},
          { section: 'Key Findings', items: [
            { title: 'Strengths', key: 'strengths' },
            { title: 'Weaknesses', key: 'weaknesses' },
            { title: 'Red Flags', key: 'red_flags' }
          ]},
          { section: 'Recommendations', items: [
            { title: 'Recommendations', key: 'recommendations' },
            { title: 'Supporting Evidence', key: 'supporting_evidence' }
          ]}
        ]
      case 'market':
        return [
          { title: 'Summary', key: 'executive_summary', isMain: true },
          { section: 'Market Analysis', items: [
            { title: 'Market Definition', key: 'market_definition' },
            { title: 'Market Sizing', key: 'market_sizing' },
            { title: 'Market Timing', key: 'market_timing' },
            { title: 'Regulatory Environment', key: 'regulatory_environment' }
          ]},
          { section: 'Market Dynamics', items: [
            { title: 'Market Trends', key: 'market_trends' },
            { title: 'Supporting Trends', key: 'trends_supporting' },
            { title: 'Opposing Trends', key: 'trends_opposing' }
          ]},
          { section: 'Market Outlook', items: [
            { title: 'Opportunities', key: 'opportunities' },
            { title: 'Challenges', key: 'challenges' },
            { title: 'Supporting Evidence', key: 'supporting_evidence' }
          ]}
        ]
      case 'product':
        return [
          { title: 'Summary', key: 'executive_summary', isMain: true },
          { section: 'Product Overview', items: [
            { title: 'Product Description', key: 'product_overview' },
            { title: 'Value Proposition', key: 'value_proposition' },
            { title: 'Product Market Fit', key: 'product_market_fit' }
          ]},
          { section: 'Traction & Growth', items: [
            { title: 'Traction Metrics', key: 'traction_metrics' },
            { title: 'Traction Analysis', key: 'traction_analysis' },
            { title: 'Revenue Model', key: 'revenue_model' }
          ]},
          { section: 'Validation & Scalability', items: [
            { title: 'Customer Feedback', key: 'customer_feedback' },
            { title: 'Use Case Validation', key: 'use_case_validation' },
            { title: 'Scalability Assessment', key: 'scalability_assessment' }
          ]},
          { section: 'Strategic Assessment', items: [
            { title: 'Strengths', key: 'strengths' },
            { title: 'Weaknesses', key: 'weaknesses' },
            { title: 'Growth Drivers', key: 'growth_drivers' },
            { title: 'Scaling Challenges', key: 'scaling_challenges' },
            { title: 'Supporting Evidence', key: 'supporting_evidence' }
          ]}
        ]
      case 'competition':
        return [
          { title: 'Summary', key: 'executive_summary', isMain: true },
          { section: 'Competitive Positioning', items: [
            { title: 'Competitive Landscape', key: 'competitive_landscape' },
            { title: 'Market Positioning', key: 'market_positioning' },
            { title: 'Differentiation Analysis', key: 'differentiation_analysis' }
          ]},
          { section: 'Competitors', items: [
            { title: 'Direct Competitors', key: 'direct_competitors' },
            { title: 'Indirect Competitors', key: 'indirect_competitors' },
            { title: 'Substitute Threats', key: 'substitute_threats' }
          ]},
          { section: 'Competitive Advantages', items: [
            { title: 'Our Advantages', key: 'competitive_advantages' },
            { title: 'Key Differentiators', key: 'key_differentiators' },
            { title: 'Moat Analysis', key: 'moat_analysis' },
            { title: 'Barriers to Entry', key: 'barriers_to_entry' },
            { title: 'Switching Costs', key: 'switching_costs' }
          ]},
          { section: 'Strategic Outlook', items: [
            { title: 'Competitive Threats', key: 'competitive_threats' },
            { title: 'Competitive Risks', key: 'competitive_risks' },
            { title: 'Competitive Strategy', key: 'competitive_strategy' },
            { title: 'Positioning Recommendations', key: 'positioning_recommendations' },
            { title: 'Supporting Evidence', key: 'supporting_evidence' }
          ]}
        ]
      case 'synthesis':
        return [
          { title: 'Summary', key: 'executive_summary', isMain: true },
          { section: 'Investment Analysis', items: [
            { title: 'Investment Thesis', key: 'investment_thesis' },
            { title: 'Investment Memo', key: 'investment_memo' },
            { title: 'Key Insights', key: 'key_insights' }
          ]},
          { section: 'Investment Decision', items: [
            { title: 'Recommendation', key: 'investment_recommendation' },
            { title: 'Risk Assessment', key: 'risk_assessment' },
            { title: 'Opportunity Assessment', key: 'opportunity_assessment' }
          ]},
          { section: 'Market Context', items: [
            { title: 'Comparable Companies', key: 'comparable_companies' },
            { title: 'Competitive Positioning', key: 'competitive_positioning' }
          ]},
          { section: 'Next Steps', items: [
            { title: 'Action Items', key: 'next_steps' },
            { title: 'Timeline', key: 'timeline' }
          ]}
        ]
      default:
        return []
    }
  }

  const scores = getScores().filter(score => score.value !== undefined && score.value !== null)
  const sections = getSections()

  return (
    <div className="space-y-8">
      {/* Analysis Title with Icon */}
      <div className="flex items-center gap-4 pb-4 border-b-2 border-gradient-to-r from-blue-500 to-purple-500">
        <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
          <Icon className="w-10 h-10 text-white" />
        </div>
        <div>
          <h2 className="text-4xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {title}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Comprehensive AI-Powered Analysis</p>
        </div>
      </div>

      {/* Analysis Content with Grouped Sections */}
      <div className="space-y-8">
        {sections.map((section, sectionIndex) => {
          // Handle main sections (like Executive Summary)
          if ('isMain' in section && section.isMain) {
            const value = data[section.key]
            if (value === null || value === undefined) return null
            
            return (
              <Card key={section.key} className="overflow-hidden border-2 border-blue-200 dark:border-blue-800 shadow-xl">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
                  <h3 className="text-3xl font-black text-white flex items-center gap-3">
                    <span className="w-2 h-8 bg-white rounded-full"></span>
                    {section.title}
                  </h3>
                </div>
                <CardContent className="p-8">
                  {/* Performance Scores inside Summary */}
                  {scores.length > 0 && (
                    <div className="mb-6">
                      <div className="flex items-center gap-2 mb-3">
                        <h4 className="text-sm font-bold text-gray-900 dark:text-white">Performance Scores</h4>
                      </div>
                      <div className="flex gap-2 overflow-x-auto">
                        {scores.map((scoreItem, index) => (
                          <div key={scoreItem.key} className={`p-3 rounded-lg shadow-sm hover:shadow-md flex-shrink-0 ${
                            index === 0 
                              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white min-w-[200px]' 
                              : 'bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 min-w-[180px]'
                          }`}>
                            <div className="flex items-center justify-between gap-2">
                              <p className={`text-xs font-semibold ${
                                index === 0 ? 'text-blue-100' : 'text-gray-600 dark:text-gray-300'
                              }`}>
                                {scoreItem.label}
                              </p>
                              <div className={`text-2xl font-black ${
                                index === 0 ? 'text-white' : getScoreColor(scoreItem.value || 0)
                              }`}>
                                {scoreItem.value?.toFixed(1) || 'N/A'}
                                {typeof scoreItem.value === 'number' && (
                                  <span className={`text-xs font-medium ml-0.5 ${
                                    index === 0 ? 'text-blue-100' : 'text-gray-400 dark:text-gray-500'
                                  }`}>/10</span>
                                )}
                              </div>
                            </div>
                            {typeof scoreItem.value === 'number' && (
                              <Progress 
                                value={scoreItem.value * 10} 
                                className={`h-1.5 mt-2 ${
                                  index === 0 ? 'bg-blue-300' : ''
                                }`}
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="prose prose-lg max-w-none dark:prose-invert font-['Inter',_'system-ui',_sans-serif] leading-relaxed">
                    {renderValue(value, section.key)}
                  </div>
                </CardContent>
              </Card>
            )
          }
          
          // Handle grouped sections with carousel
          if ('section' in section && section.items) {
            // Filter items that have values
            const validItems = section.items.filter(item => {
              const value = data[item.key]
              return value !== null && value !== undefined
            })

            if (validItems.length === 0) return null

            return (
              <SectionCarousel
                key={sectionIndex}
                sectionIndex={sectionIndex}
                sectionTitle={section.section}
                items={validItems}
                data={data}
                renderValue={renderValue}
                analysisType={analysisType}
              />
            )
          }
          
          return null
        })}
      </div>
    </div>
  )
}

export function AnalysisPage() {
  const { id } = useParams<{ id: string }>()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [isReanalysisModalOpen, setIsReanalysisModalOpen] = useState(false)
  const [investorNotes, setInvestorNotes] = useState('')

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses', id],
    queryFn: () => analysisApi.list({ startup_id: id }),
    enabled: !!id,
  })

  // Get startup data for founder email
  const { data: startup } = useQuery({
    queryKey: ['startup', id],
    queryFn: () => startupsApi.get(id!),
    enabled: !!id,
  })

  // Get startup status
  const { data: startupStatus } = useQuery({
    queryKey: ['startupStatus', id],
    queryFn: () => startupStatusApi.getStatus(id!),
    enabled: !!id,
  })

  const latestAnalysis = analyses?.data?.[0]

  // Status update mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ status }: { status: string }) => startupStatusApi.updateStatus(id!, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['startupStatus', id] })
      toast({
        title: 'Status Updated',
        description: 'Startup status has been updated successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to update status',
        variant: 'destructive',
      })
    },
  })

  const handleStatusUpdate = (status: string) => {
    updateStatusMutation.mutate({ status })
  }

  // Re-analysis mutation
  const reanalysisMutation = useMutation({
    mutationFn: ({ notes }: { notes: string }) => analysisApi.triggerReanalysis(id!, notes),
    onSuccess: (data) => {
      setIsReanalysisModalOpen(false)
      setInvestorNotes('')
      queryClient.invalidateQueries({ queryKey: ['analyses', id] })
      toast({
        title: 'Re-analysis Started',
        description: `Analysis ${data.analysis_id} has been queued. The AI agents will re-analyze the startup with your notes.`,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to trigger re-analysis',
        variant: 'destructive',
      })
    },
  })

  const handleReanalysis = () => {
    if (!investorNotes.trim()) {
      toast({
        title: 'Notes Required',
        description: 'Please provide investor notes for the re-analysis',
        variant: 'destructive',
      })
      return
    }
    reanalysisMutation.mutate({ notes: investorNotes })
  }

  const handleScheduleMeeting = () => {
    const founderEmail = startup?.founders?.[0]?.email
    if (founderEmail) {
      window.location.href = `mailto:${founderEmail}?subject=Meeting Request - ${startup?.company_info?.name}`
    }
  }

  const handleShare = () => {
    const url = window.location.href
    navigator.clipboard.writeText(url)
    toast({
      title: 'Link Copied!',
      description: 'Analysis page link copied to clipboard',
    })
  }

  const currentStatus = startupStatus?.status || 'New'

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

  // Parse investment recommendation if it's a JSON string
  const parseInvestmentRecommendation = (recommendation: any) => {
    if (!recommendation) return 'PENDING'
    if (typeof recommendation === 'string') {
      try {
        const parsed = JSON.parse(recommendation)
        return parsed.recommendation || parsed.investment_recommendation || recommendation
      } catch {
        return recommendation
      }
    }
    return recommendation.recommendation || recommendation.investment_recommendation || 'PENDING'
  }

  // Create investability score object for the UI using BigQuery fields
  const investabilityScore = latestAnalysis?.investability_score || {
    overall_score: latestAnalysis?.overall_score || 0,
    team_score: latestAnalysis?.team_score || 0,
    market_score: latestAnalysis?.market_score || 0, 
    product_score: latestAnalysis?.product_score || 0,
    competition_score: latestAnalysis?.competition_score || 0,
    investment_recommendation: parseInvestmentRecommendation(latestAnalysis?.investment_recommendation),
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
    <BeaconProvider>
    <div className="min-h-screen bg-white dark:bg-gray-950">
      <div className="p-6 space-y-6">
      {/* Header */}
      {/* Modern Gradient Header Card */}
      <div className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-500 px-6 py-12 md:py-16 shadow-2xl">
          {/* Animated Background Elements */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-1/2 -right-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute -bottom-1/2 -left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          </div>
          
          <div className="relative max-w-7xl mx-auto">
          <div className="flex items-center justify-between gap-8">
            {/* Left - Back Button + Analysis Info */}
            <div className="flex items-center gap-5 flex-1">
              {/* Back Button */}
              <Button 
                variant="ghost" 
                size="icon"
                asChild
                className="text-white hover:bg-white/20 hover:text-white flex-shrink-0"
              >
                <Link to={`/startups/${id}`}>
                  <ArrowLeft className="w-5 h-5" />
                </Link>
              </Button>
              
              {startup?.company_info?.logo_url ? (
                <img 
                  src={startup.company_info.logo_url} 
                  alt={`${startup.company_info.name} logo`}
                  className="w-20 h-20 rounded-2xl object-contain bg-white/90 p-2 shadow-xl border border-white/30 flex-shrink-0"
                />
              ) : (
                <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-xl border border-white/30 flex-shrink-0">
                  <BarChart3 className="w-10 h-10 text-white" />
                </div>
              )}
              <div className="flex-1">
                <p className="text-lg text-white/80 mb-1">Investment Analysis</p>
                  {latestAnalysis?.company_name && (
                    <div className="flex items-center gap-3 mb-2">
                      <h1 className="text-4xl font-bold text-white drop-shadow-lg">{latestAnalysis.company_name}</h1>
                      <Badge className="bg-white/30 backdrop-blur-sm text-white border-white/40 hover:bg-white/40 px-3 py-1.5 text-sm">
                        {investabilityScore?.investment_recommendation || 'Pending'}
                      </Badge>
                    </div>
                  )}
                  <div className="flex items-center gap-2 mt-3">
                    <Button 
                      variant="secondary" 
                      size="sm"
                      onClick={() => setIsReanalysisModalOpen(true)}
                      className="bg-white/90 hover:bg-white text-gray-900 font-medium shadow-lg h-8 px-3 text-xs"
                    >
                      <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
                      Re-analyze
                    </Button>
                  </div>
                </div>
              </div>

            {/* Right - Status & Action Buttons */}
            <div className="flex items-center gap-2 flex-wrap justify-end">
              {/* Current Status Badge */}
              <div className="flex items-center gap-2 bg-white/20 backdrop-blur-md rounded-xl px-4 py-2 border border-white/30">
                <span className="text-sm font-medium text-white/90">Status:</span>
                <Badge variant="secondary" className="text-base font-bold px-4 py-1.5 bg-white text-purple-700">
                  {currentStatus}
                </Badge>
              </div>

              {/* Divider */}
              <div className="h-8 w-px bg-white/30" />

              {/* Watch Button */}
              {currentStatus !== 'On Watch' && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleStatusUpdate('On Watch')}
                  disabled={updateStatusMutation.isPending}
                  className="flex items-center gap-2 bg-white/90 hover:bg-white text-gray-900 font-medium shadow-lg"
                >
                  <Eye className="w-4 h-4" />
                  Watch
                </Button>
              )}

              {/* Shortlist Button */}
              {currentStatus !== 'Shortlist' && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleStatusUpdate('Shortlist')}
                  disabled={updateStatusMutation.isPending}
                  className="flex items-center gap-2 bg-white/90 hover:bg-white text-gray-900 font-medium shadow-lg"
                >
                  <Star className="w-4 h-4" />
                  Shortlist
                </Button>
              )}

              {/* Pass Button */}
              {currentStatus !== 'Pass' && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleStatusUpdate('Pass')}
                  disabled={updateStatusMutation.isPending}
                  className="flex items-center gap-2 bg-white/90 hover:bg-white text-gray-900 font-medium shadow-lg"
                >
                  <X className="w-4 h-4" />
                  Pass
                </Button>
              )}

              {/* Schedule Meeting Button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleScheduleMeeting}
                className="flex items-center gap-2 bg-white/90 hover:bg-white text-gray-900 font-medium shadow-lg"
              >
                <CalendarDays className="w-4 h-4" />
                Meeting
              </Button>

              {/* Share Button */}
              <Button
                variant="secondary"
                size="sm"
                onClick={handleShare}
                className="flex items-center gap-2 bg-white/90 hover:bg-white text-gray-900 font-medium shadow-lg"
              >
                <Share2 className="w-4 h-4" />
                Share
              </Button>
            </div>
          </div>
          </div>
        </div>

      {/* Overall Score Cards */}
      {investabilityScore && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center justify-between">
                <span>Overall Score</span>
                <BeaconSectionIcon
                  sectionId="overall-score"
                  sectionTitle="Overall Investment Score"
                  sectionType="synthesis"
                  sectionData={investabilityScore}
                />
              </CardTitle>
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
              <CardTitle className="text-sm font-medium flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Team
                </div>
                <BeaconSectionIcon
                  sectionId="team-score"
                  sectionTitle="Team Analysis"
                  sectionType="team"
                  sectionData={{
                    ...teamAnalysis,
                    subsections: extractSubsections(teamAnalysis)
                  }}
                />
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
              <CardTitle className="text-sm font-medium flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Market
                </div>
                <BeaconSectionIcon
                  sectionId="market-score"
                  sectionTitle="Market Analysis"
                  sectionType="market"
                  sectionData={{
                    ...marketAnalysis,
                    subsections: extractSubsections(marketAnalysis)
                  }}
                />
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
              <CardTitle className="text-sm font-medium flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Product
                </div>
                <BeaconSectionIcon
                  sectionId="product-score"
                  sectionTitle="Product Analysis"
                  sectionType="product"
                  sectionData={{
                    ...productAnalysis,
                    subsections: extractSubsections(productAnalysis)
                  }}
                />
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
              <CardTitle className="text-sm font-medium flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4" />
                  Competition
                </div>
                <BeaconSectionIcon
                  sectionId="competition-score"
                  sectionTitle="Competition Analysis"
                  sectionType="competition"
                  sectionData={{
                    ...competitionAnalysis,
                    subsections: extractSubsections(competitionAnalysis)
                  }}
                />
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

      <Tabs defaultValue="team" className="space-y-8">
        <div className="bg-white dark:bg-gray-800 p-3 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700">
          <TabsList className="grid w-full grid-cols-5 gap-3 bg-transparent p-0 h-auto">
            <TabsTrigger 
              value="team" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-4 text-base"
            >
              <div className="flex flex-col items-center gap-1">
                <Users className="w-5 h-5" />
                <span>Team</span>
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="market" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-4 text-base"
            >
              <div className="flex flex-col items-center gap-1">
                <TrendingUp className="w-5 h-5" />
                <span>Market</span>
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="product" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-4 text-base"
            >
              <div className="flex flex-col items-center gap-1">
                <Package className="w-5 h-5" />
                <span>Product</span>
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="competition" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-4 text-base"
            >
              <div className="flex flex-col items-center gap-1">
                <Target className="w-5 h-5" />
                <span>Competition</span>
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="synthesis" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-4 text-base"
            >
              <div className="flex flex-col items-center gap-1">
                <CheckCircle className="w-5 h-5" />
                <span>Verdict</span>
              </div>
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="team" className="space-y-6">
          <AnalysisRenderer 
            data={teamAnalysis} 
            title="Team Analysis" 
            icon={Users} 
            analysisType="team"
          />
        </TabsContent>

        <TabsContent value="market" className="space-y-6">
          <AnalysisRenderer 
            data={marketAnalysis} 
            title="Market Analysis" 
            icon={TrendingUp} 
            analysisType="market"
          />
        </TabsContent>

        <TabsContent value="product" className="space-y-6">
          <AnalysisRenderer 
            data={productAnalysis} 
            title="Product Analysis" 
            icon={Target} 
            analysisType="product"
          />
        </TabsContent>

        <TabsContent value="competition" className="space-y-6">
          <AnalysisRenderer 
            data={competitionAnalysis} 
            title="Competition Analysis" 
            icon={Shield} 
            analysisType="competition"
          />
        </TabsContent>

        <TabsContent value="synthesis" className="space-y-6">
          <AnalysisRenderer 
            data={synthesisAnalysis} 
            title="Final Verdict" 
            icon={BarChart3} 
            analysisType="synthesis"
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
                {latestAnalysis?.investment_memo && (
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown>{latestAnalysis.investment_memo}</ReactMarkdown>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

      </Tabs>

      {/* Re-analysis Modal */}
      <Dialog open={isReanalysisModalOpen} onOpenChange={setIsReanalysisModalOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-purple-600" />
              Request Re-analysis
            </DialogTitle>
            <DialogDescription>
              Provide specific notes or focus areas for the AI agents to consider during re-analysis. 
              The agents will incorporate answered questions, new attachments, and your guidance to generate an updated analysis.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="investor-notes" className="text-base font-medium">
                Investor Notes <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="investor-notes"
                placeholder="Example: Focus on financial viability and team strength. Pay special attention to the updated financial projections and new CTO hire. Assess scalability concerns and competitive positioning in the European market."
                value={investorNotes}
                onChange={(e) => setInvestorNotes(e.target.value)}
                rows={8}
                className="resize-none"
              />
              <p className="text-sm text-muted-foreground">
                Be specific about what aspects you want the AI to focus on (e.g., financials, team, market, product, competition).
              </p>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <Lightbulb className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    What happens during re-analysis?
                  </p>
                  <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-disc list-inside">
                    <li>AI agents will review all answered questions and their attachments</li>
                    <li>Your notes will guide the focus areas for analysis</li>
                    <li>A new comprehensive analysis will be generated</li>
                    <li>Previous analysis will remain accessible for comparison</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsReanalysisModalOpen(false)
                setInvestorNotes('')
              }}
              disabled={reanalysisMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleReanalysis}
              disabled={reanalysisMutation.isPending || !investorNotes.trim()}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {reanalysisMutation.isPending ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Start Re-analysis
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Beacon Chat Panel */}
      <BeaconChat 
        startupId={id!} 
        analysisData={latestAnalysis}
        startupData={startup}
      />

      {/* Beacon Floating Button */}
      <BeaconButton />
    </div>
    </div>
    </BeaconProvider>
  )
}
