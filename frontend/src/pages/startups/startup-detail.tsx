import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { 
  ArrowLeft, 
  Building2, 
  MapPin, 
  Users, 
  IndianRupee, 
  Calendar,
  Globe,
  FileText,
  Download,
  Sparkles,
  Clock,
  CheckCircle,
  TrendingUp,
  Target,
  Rocket,
  Scale,
  Package,
  Code,
  Award,
  Briefcase,
  Eye,
  Star,
  X,
  CalendarDays,
  MessageSquare,
  Share2,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { startupsApi, analysisApi, startupStatusApi } from '@/services/api'
import { formatCurrency, formatDate, formatFileSize, capitalizeFirst } from '@/utils'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/use-auth'

// Q&A Components
import { AskQuestionModal } from '@/components/questions/ask-question-modal'
import { AnswerQuestionsModal } from '@/components/questions/answer-questions-modal'
import { QuestionsList } from '@/components/questions/questions-list'
import { ActivityFeed } from '@/components/activity/activity-feed'
import { useStartupQuestions } from '@/hooks/use-questions'

// Helper functions for Indian market formatting
const formatINR = (amount: number | undefined) => {
  if (!amount) return 'Not specified'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

const formatCrores = (amount: number | undefined) => {
  if (!amount) return 'Not specified'
  const crores = amount / 10000000
  return `₹${crores.toFixed(2)} Cr`
}

const formatPercent = (value: number | undefined) => {
  if (!value) return 'Not specified'
  return `${value.toFixed(1)}%`
}

export function StartupDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [noteText, setNoteText] = useState('')
  const [isEditingNote, setIsEditingNote] = useState(false)
  
  // Get current user and role
  const { user, isInvestor, isFounder } = useAuth()

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

  // Get startup status (investors only)
  const { data: startupStatus } = useQuery({
    queryKey: ['startupStatus', id],
    queryFn: () => startupStatusApi.getStatus(id!),
    enabled: !!id && isInvestor,
  })

  // Get questions for this startup
  const { data: allQuestions = [] } = useStartupQuestions(id || '', undefined)
  const pendingQuestions = allQuestions.filter(q => q.status === 'pending')
  const answeredQuestions = allQuestions.filter(q => q.status === 'answered')

  const latestAnalysis = analyses?.data?.[0]
  const hasAnalysis = !!latestAnalysis
  const isAnalysisInProgress = hasAnalysis && latestAnalysis.status === 'in_progress'
  const isAnalysisCompleted = hasAnalysis && latestAnalysis.status === 'completed'

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

  // Note update mutation
  const updateNoteMutation = useMutation({
    mutationFn: ({ note }: { note: string }) => startupStatusApi.updateNote(id!, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['startupStatus', id] })
      setIsEditingNote(false)
      toast({
        title: 'Note Saved',
        description: 'Your note has been saved successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to save note',
        variant: 'destructive',
      })
    },
  })

  const handleStatusUpdate = (status: string) => {
    updateStatusMutation.mutate({ status })
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
      description: 'Startup page link copied to clipboard',
    })
  }

  const handleSaveNote = () => {
    if (noteText.trim()) {
      updateNoteMutation.mutate({ note: noteText })
    }
  }

  const currentStatus = startupStatus?.status || 'New'

  // Analysis status component (investors only)
  const AnalysisStatusCard = () => {
    if (!isInvestor) return null
    if (isAnalysisCompleted) {
      return (
        <Card className="border-none shadow-lg bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-800 dark:to-blue-800 rounded-full flex items-center justify-center animate-pulse">
                    <Sparkles className="w-8 h-8 text-purple-600 dark:text-purple-400 animate-bounce" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-white" />
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-1">Analysis Ready! ✨</h3>
                </div>
              </div>
              <Button size="lg" className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 shadow-lg" asChild>
                <Link to={`/startups/${id}/analysis`}>
                  <Sparkles className="w-5 h-5 mr-2 animate-pulse" />
                  View Analysis
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )
    }
    
    if (isAnalysisInProgress) {
      return (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/20">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center">
                <Clock className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-spin" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-blue-800 dark:text-blue-400 mb-1">Analysis in Progress</h3>
                <p className="text-blue-600 dark:text-blue-300">Our AI agents are analyzing this startup...</p>
                <div className="flex items-center gap-2 mt-2">
                  <div className="w-32 h-2 bg-blue-200 dark:bg-blue-700 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{width: '60%'}}></div>
                  </div>
                  <span className="text-sm text-blue-500 dark:text-blue-400">Analyzing...</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }
    
    return null
  }

  const InfoRow = ({ icon: Icon, label, value }: { icon: any, label: string, value: string | undefined }) => {
    if (!value || value === 'Not specified') return null
    return (
      <div className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
        <Icon className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm text-gray-600 dark:text-gray-400">{label}</p>
          <p className="text-base text-gray-900 dark:text-gray-100 break-words">{value}</p>
        </div>
      </div>
    )
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

  return (
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
            {/* Left - Back Button + Company Details */}
            <div className="flex items-center gap-5 flex-1">
              {/* Back Button */}
              <Button 
                variant="ghost" 
                size="icon"
                asChild
                className="text-white hover:bg-white/20 hover:text-white flex-shrink-0"
              >
                <Link to="/startups">
                  <ArrowLeft className="w-5 h-5" />
                </Link>
              </Button>
              
              {startup.company_info.logo_url ? (
                <img 
                  src={startup.company_info.logo_url} 
                  alt={`${startup.company_info.name} logo`}
                  className="w-20 h-20 rounded-2xl object-contain bg-white/90 p-2 shadow-xl border border-white/30 flex-shrink-0"
                />
              ) : (
                <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-xl border border-white/30 flex-shrink-0">
                  <Building2 className="w-10 h-10 text-white" />
                </div>
              )}
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg">
                  {startup.company_info.name}
                </h1>
                <div className="flex items-center gap-3 text-white/90 text-sm flex-wrap">
                  <span className="flex items-center gap-1.5 bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-full">
                    <span className="w-1.5 h-1.5 bg-white rounded-full" />
                    {capitalizeFirst(startup.company_info.industry.replace('_', ' '))}
                  </span>
                  <span className="flex items-center gap-1.5 bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-full">
                    <span className="w-1.5 h-1.5 bg-white rounded-full" />
                    {capitalizeFirst(startup.company_info.funding_stage.replace('_', ' '))}
                  </span>
                  <span className="flex items-center gap-1.5 bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-full">
                    <span className="w-1.5 h-1.5 bg-white rounded-full" />
                    {capitalizeFirst(startup.company_info.product_stage?.replace('_', ' ') || 'N/A')}
                  </span>
                </div>
              </div>
            </div>

            {/* Right - Status & Action Buttons (Investors only) */}
            {isInvestor && (
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
            )}
          </div>
          </div>
        </div>

      {/* Analysis Status Card */}
      <AnalysisStatusCard />

      {/* Notes Section (Investors only) */}
      {isInvestor && (
      <Card className="border border-gray-200 dark:border-gray-700">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-purple-500" />
            Notes
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {!isEditingNote && !startupStatus?.investor_note ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setIsEditingNote(true)
                setNoteText('')
              }}
              className="w-full justify-start text-muted-foreground hover:text-foreground"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Add a note...
            </Button>
          ) : !isEditingNote && startupStatus?.investor_note ? (
            <div className="space-y-2">
              <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-md text-sm">
                <p className="whitespace-pre-wrap">{startupStatus.investor_note}</p>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  {startupStatus.note_updated_at ? formatDate(startupStatus.note_updated_at) : 'N/A'}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setIsEditingNote(true)
                    setNoteText(startupStatus.investor_note || '')
                  }}
                >
                  Edit
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <Textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Enter your notes..."
                rows={3}
                className="text-sm"
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleSaveNote}
                  disabled={updateNoteMutation.isPending || !noteText.trim()}
                >
                  Save
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setIsEditingNote(false)
                    setNoteText('')
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      )}

      {/* Main Content Layout: Tabs on left, Activity Feed on right */}
      <div className="flex gap-6 items-start">
        {/* Left side - Tabs */}
        <div className="flex-1">
      <Card>
        <CardContent className="p-0">
      <Tabs defaultValue="overview" className="space-y-0">
        <div className="bg-white dark:bg-gray-800 p-3 rounded-t-lg border-b-2 border-gray-200 dark:border-gray-700">
          <TabsList className="grid w-full grid-cols-9 gap-2 bg-transparent p-0 h-auto">
            <TabsTrigger 
              value="overview" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger 
              value="product" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-purple-500 data-[state=active]:to-blue-500 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Product
            </TabsTrigger>
            <TabsTrigger 
              value="market" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-cyan-500 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Market
            </TabsTrigger>
            <TabsTrigger 
              value="traction" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-indigo-500 data-[state=active]:to-purple-500 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Traction
            </TabsTrigger>
            <TabsTrigger 
              value="financial" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-600 data-[state=active]:to-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Financial
            </TabsTrigger>
            <TabsTrigger 
              value="team" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-purple-600 data-[state=active]:to-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Team
            </TabsTrigger>
            <TabsTrigger 
              value="legal" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-indigo-500 data-[state=active]:to-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Legal
            </TabsTrigger>
            <TabsTrigger 
              value="vision" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Vision
            </TabsTrigger>
            <TabsTrigger 
              value="documents" 
              className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-indigo-600 data-[state=active]:to-blue-700 data-[state=active]:text-white data-[state=active]:shadow-lg font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all rounded-xl py-3 text-sm"
            >
              Documents
            </TabsTrigger>
          </TabsList>
        </div>

        {/* OVERVIEW TAB */}
        <TabsContent value="overview" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-blue-200 dark:border-blue-800">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700">
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-blue-500" />
                Company Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div>
                <h3 className="font-semibold text-lg mb-2">Description</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {startup.company_info.description}
                </p>
              </div>
              
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow icon={MapPin} label="Location" value={startup.company_info.location} />
                <InfoRow icon={Users} label="Team Size" value={startup.company_info.employee_count ? `${startup.company_info.employee_count} employees` : undefined} />
                <InfoRow icon={Globe} label="Website" value={startup.company_info.website_url} />
                <InfoRow icon={Calendar} label="Founded" value={startup.company_info.founded_date ? formatDate(startup.company_info.founded_date) : undefined} />
                <InfoRow icon={IndianRupee} label="Funding Raised" value={startup.company_info.funding_raised ? formatINR(startup.company_info.funding_raised) : undefined} />
                <InfoRow icon={IndianRupee} label="Funding Seeking" value={startup.company_info.funding_seeking ? formatINR(startup.company_info.funding_seeking) : undefined} />
              </div>
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* PRODUCT TAB */}
        <TabsContent value="product" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-purple-200 dark:border-purple-800">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30">
              <CardTitle className="flex items-center gap-2">
                <Package className="w-5 h-5 text-purple-500" />
                Product & Technology
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow icon={Rocket} label="Product Stage" value={startup.company_info.product_stage ? capitalizeFirst(startup.company_info.product_stage) : undefined} />
                <InfoRow icon={Code} label="Technology Stack" value={startup.company_info.technology_stack} />
              </div>
              
              {startup.company_info.ip_patents && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <Award className="w-4 h-4 text-purple-500" />
                    IP & Patents
                  </h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.ip_patents}</p>
                </div>
              )}
              
              {startup.company_info.development_timeline && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Development Timeline</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.development_timeline}</p>
                </div>
              )}
              
              {startup.company_info.product_roadmap && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Product Roadmap</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.product_roadmap}</p>
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* MARKET TAB */}
        <TabsContent value="market" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-blue-200 dark:border-blue-800">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30">
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-500" />
                Market & Customers
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              {startup.company_info.target_customer_profile && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Target Customer Profile</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.target_customer_profile}</p>
                </div>
              )}
              
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                <InfoRow icon={IndianRupee} label="CAC" value={formatINR(startup.company_info.customer_acquisition_cost)} />
                <InfoRow icon={IndianRupee} label="LTV" value={formatINR(startup.company_info.lifetime_value)} />
                <InfoRow icon={Users} label="Current Customers" value={startup.company_info.current_customer_count?.toString()} />
                <InfoRow icon={TrendingUp} label="Retention Rate" value={formatPercent(startup.company_info.customer_retention_rate)} />
                <InfoRow icon={MapPin} label="Geographic Markets" value={startup.company_info.geographic_markets} />
              </div>
              
              {startup.company_info.go_to_market_strategy && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Go-to-Market Strategy</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.go_to_market_strategy}</p>
                </div>
              )}
              
              <div className="grid gap-3 md:grid-cols-3">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800">
                  <p className="text-sm font-medium text-blue-600 dark:text-blue-400">TAM</p>
                  <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">{formatCrores(startup.metadata?.market_size_tam)}</p>
                </div>
                <div className="p-4 bg-cyan-50 dark:bg-cyan-900/20 rounded-lg border-2 border-cyan-200 dark:border-cyan-800">
                  <p className="text-sm font-medium text-cyan-600 dark:text-cyan-400">SAM</p>
                  <p className="text-2xl font-bold text-cyan-700 dark:text-cyan-300">{formatCrores(startup.metadata?.market_size_sam)}</p>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-2 border-purple-200 dark:border-purple-800">
                  <p className="text-sm font-medium text-purple-600 dark:text-purple-400">SOM</p>
                  <p className="text-2xl font-bold text-purple-700 dark:text-purple-300">{formatCrores(startup.metadata?.market_size_som)}</p>
                </div>
              </div>
              
              {startup.metadata?.main_competitors && startup.metadata.main_competitors.length > 0 && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Main Competitors</h3>
                  <ul className="space-y-1">
                    {startup.metadata.main_competitors.map((competitor, i) => (
                      <li key={i} className="text-muted-foreground">• {competitor}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {startup.metadata?.unique_value_proposition && (
                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border-2 border-indigo-200 dark:border-indigo-800">
                  <h3 className="font-semibold mb-2 text-indigo-800 dark:text-indigo-400">Unique Value Proposition</h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{startup.metadata.unique_value_proposition}</p>
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* TRACTION TAB */}
        <TabsContent value="traction" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-indigo-200 dark:border-indigo-800">
            <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/30">
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-indigo-500" />
                Traction & Metrics
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">MRR</p>
                  <p className="text-xl font-bold text-purple-600 dark:text-purple-400">{formatINR(startup.company_info.monthly_recurring_revenue)}</p>
                </div>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">ARR</p>
                  <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{formatINR(startup.company_info.annual_recurring_revenue)}</p>
                </div>
                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Revenue Run Rate</p>
                  <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400">{formatINR(startup.company_info.revenue_run_rate)}</p>
                </div>
                <InfoRow icon={TrendingUp} label="Revenue Growth" value={formatPercent(startup.company_info.revenue_growth_rate)} />
                <InfoRow icon={TrendingUp} label="User Growth" value={formatPercent(startup.company_info.user_growth_rate)} />
                <InfoRow icon={IndianRupee} label="Burn Rate" value={startup.company_info.burn_rate ? `${formatINR(startup.company_info.burn_rate)}/month` : undefined} />
                <InfoRow icon={Calendar} label="Runway" value={startup.company_info.runway_months ? `${startup.company_info.runway_months} months` : undefined} />
              </div>
              
              {startup.company_info.key_performance_indicators && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Key Performance Indicators</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.key_performance_indicators}</p>
                </div>
              )}
              
              {startup.metadata?.traction_highlights && startup.metadata.traction_highlights.length > 0 && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h3 className="font-semibold mb-2">Traction Highlights</h3>
                  <ul className="space-y-2">
                    {startup.metadata.traction_highlights.map((highlight, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                        <span className="text-muted-foreground">{highlight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* FINANCIAL TAB */}
        <TabsContent value="financial" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-blue-200 dark:border-blue-800">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30">
              <CardTitle className="flex items-center gap-2">
                <IndianRupee className="w-5 h-5 text-blue-500" />
                Financial Details
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow icon={IndianRupee} label="Funding Raised" value={formatINR(startup.company_info.funding_raised)} />
                <InfoRow icon={IndianRupee} label="Funding Seeking" value={formatINR(startup.company_info.funding_seeking)} />
              </div>
              
              {startup.company_info.previous_funding_rounds && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Previous Funding Rounds</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.previous_funding_rounds}</p>
                </div>
              )}
              
              {startup.company_info.current_investors && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Current Investors</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.current_investors}</p>
                </div>
              )}
              
              {startup.company_info.use_of_funds && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h3 className="font-semibold mb-2">Use of Funds</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.use_of_funds}</p>
                </div>
              )}
              
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow icon={Calendar} label="Profitability Timeline" value={startup.company_info.profitability_timeline} />
                <InfoRow icon={TrendingUp} label="Unit Economics" value={startup.company_info.unit_economics} />
              </div>
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* TEAM TAB */}
        <TabsContent value="team" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-purple-200 dark:border-purple-800">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-700">
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-purple-500" />
                Founders & Team
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid gap-6 md:grid-cols-2">
                {startup.founders.map((founder, index) => (
                  <Card key={index} className="border-2">
                    <CardHeader className="bg-gray-50 dark:bg-gray-800/50">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center">
                          <Users className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{founder.name}</CardTitle>
                          <CardDescription>{founder.role}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-3">
                      {founder.email && (
                        <p className="text-sm text-muted-foreground">📧 {founder.email}</p>
                      )}
                      
                      {founder.linkedin_url && (
                        <a href={founder.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-500 hover:underline block">
                          🔗 LinkedIn Profile
                        </a>
                      )}
                      
                      {founder.bio && (
                        <div>
                          <h4 className="font-medium text-sm mb-1">Bio</h4>
                          <p className="text-sm text-muted-foreground">{founder.bio}</p>
                        </div>
                      )}
                      
                      {founder.domain_expertise_years && (
                        <p className="text-sm"><span className="font-medium">Domain Expertise:</span> {founder.domain_expertise_years} years</p>
                      )}
                      
                      {founder.previous_exits && (
                        <div>
                          <h4 className="font-medium text-sm mb-1">Previous Exits</h4>
                          <p className="text-sm text-muted-foreground">{founder.previous_exits}</p>
                        </div>
                      )}
                      
                      {founder.key_achievements && (
                        <div>
                          <h4 className="font-medium text-sm mb-1">Key Achievements</h4>
                          <p className="text-sm text-muted-foreground">{founder.key_achievements}</p>
                        </div>
                      )}
                      
                      {founder.previous_experience && founder.previous_experience.length > 0 && (
                        <div>
                          <h4 className="font-medium text-sm mb-1">Experience</h4>
                          <ul className="space-y-1">
                            {founder.previous_experience.map((exp, i) => (
                              <li key={i} className="text-sm text-muted-foreground">• {exp}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {founder.education && founder.education.length > 0 && (
                        <div>
                          <h4 className="font-medium text-sm mb-1">Education</h4>
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
              
              {startup.metadata?.advisory_board && startup.metadata.advisory_board.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Advisory Board</h3>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {startup.metadata.advisory_board.map((advisor, i) => (
                      <Card key={i} className="border">
                        <CardContent className="pt-4">
                          <h4 className="font-semibold">{advisor.name}</h4>
                          <p className="text-sm text-muted-foreground mt-1">{advisor.expertise}</p>
                          <p className="text-xs text-muted-foreground mt-2">{advisor.background}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
              
              {startup.metadata?.key_hires_planned && (
                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h3 className="font-semibold mb-2">Key Hires Planned</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.metadata.key_hires_planned}</p>
                </div>
              )}
              
              {startup.metadata?.team_gaps && (
                <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h3 className="font-semibold mb-2">Team Gaps</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.metadata.team_gaps}</p>
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* LEGAL TAB */}
        <TabsContent value="legal" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-indigo-200 dark:border-indigo-800">
            <CardHeader className="bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-gray-800 dark:to-gray-700">
              <CardTitle className="flex items-center gap-2">
                <Scale className="w-5 h-5 text-indigo-500" />
                Legal & Compliance
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow icon={Briefcase} label="Company Structure" value={startup.company_info.company_structure ? capitalizeFirst(startup.company_info.company_structure.replace('_', ' ')) : undefined} />
                <InfoRow icon={MapPin} label="Incorporation Location" value={startup.company_info.incorporation_location} />
              </div>
              
              {startup.company_info.regulatory_requirements && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <h3 className="font-semibold mb-2">Regulatory Requirements</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{startup.company_info.regulatory_requirements}</p>
                </div>
              )}
              
              {startup.company_info.legal_issues && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border-2 border-red-200 dark:border-red-800">
                  <h3 className="font-semibold mb-2 text-red-800 dark:text-red-400">Legal Issues</h3>
                  <p className="text-red-700 dark:text-red-300 whitespace-pre-wrap">{startup.company_info.legal_issues}</p>
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* VISION TAB */}
        <TabsContent value="vision" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card className="border-2 border-pink-200 dark:border-pink-800">
            <CardHeader className="bg-gradient-to-r from-pink-50 to-purple-50 dark:from-gray-800 dark:to-gray-700">
              <CardTitle className="flex items-center gap-2">
                <Rocket className="w-5 h-5 text-pink-500" />
                Vision & Strategy
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              {startup.company_info.mission_statement && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800">
                  <h3 className="font-semibold mb-2 text-blue-800 dark:text-blue-400">Mission Statement</h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{startup.company_info.mission_statement}</p>
                </div>
              )}
              
              {startup.company_info.five_year_vision && (
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-2 border-purple-200 dark:border-purple-800">
                  <h3 className="font-semibold mb-2 text-purple-800 dark:text-purple-400">5-Year Vision</h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{startup.company_info.five_year_vision}</p>
                </div>
              )}
              
              {startup.company_info.exit_strategy && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-200 dark:border-green-800">
                  <h3 className="font-semibold mb-2 text-green-800 dark:text-green-400">Exit Strategy</h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{startup.company_info.exit_strategy}</p>
                </div>
              )}
              
              {startup.company_info.social_impact && (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border-2 border-yellow-200 dark:border-yellow-800">
                  <h3 className="font-semibold mb-2 text-yellow-800 dark:text-yellow-400">Social Impact</h3>
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{startup.company_info.social_impact}</p>
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>

        {/* DOCUMENTS TAB */}
        <TabsContent value="documents" className="p-4">
          <ScrollArea className="h-[480px] pr-4">
            <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Uploaded Documents
              </CardTitle>
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
                  {startup.documents.map((doc, index) => (
                    <div key={doc.id || index} className="flex items-center justify-between p-4 border-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <p className="font-medium">{doc.filename}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.document_type ? capitalizeFirst(doc.document_type.replace('_', ' ')) : doc.mime_type || 'Document'}
                            {doc.file_size && ` • ${formatFileSize(doc.file_size)}`}
                          </p>
                        </div>
                      </div>
                      {doc.id && doc.storage_path && (
                        <Button variant="outline" size="sm" asChild>
                          <a href={startupsApi.downloadDocument(startup.id, doc.id)} download>
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </a>
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
        </CardContent>
      </Card>
        </div>
        {/* Right side - Activity Feed */}
        <div className="w-96 sticky top-4">
          <ActivityFeed startupId={id!} />
        </div>
      </div>

      {/* Questions & Answers Section - Below Tabs */}
      {/* Questions Section (Founders only) */}
      {isFounder && (
        <div className="space-y-6 mt-8">
          {/* Pending Questions */}
          {pendingQuestions.length > 0 && (
            <Card className="border-none shadow-lg">
              <CardHeader className="border-b bg-gradient-to-r from-orange-50 to-red-50 dark:from-blue-900/20 dark:to-indigo-900/20">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                      <MessageSquare className="h-5 w-5 text-orange-600" />
                      Open Questions ({pendingQuestions.length})
                    </CardTitle>
                    <CardDescription className="text-sm mt-1">Questions from investors awaiting your response</CardDescription>
                  </div>
                  <AnswerQuestionsModal 
                    questions={pendingQuestions} 
                    startupId={id!}
                  />
                </div>
              </CardHeader>
              <CardContent className="p-6">
                <QuestionsList 
                  questions={pendingQuestions}
                  emptyMessage="No pending questions"
                />
              </CardContent>
            </Card>
          )}

          {/* Answered Questions */}
          {answeredQuestions.length > 0 && (
            <Card className="border-none shadow-lg">
              <CardHeader className="border-b bg-gradient-to-r from-green-50 to-emerald-50 dark:from-blue-900/20 dark:to-cyan-900/20">
                <CardTitle className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Answered Questions ({answeredQuestions.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <QuestionsList 
                  questions={answeredQuestions}
                  emptyMessage="No answered questions yet"
                />
              </CardContent>
            </Card>
          )}

          {/* No questions state */}
          {allQuestions.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
                <p className="text-muted-foreground">No questions yet from investors</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Questions Section (Investors only - View mode) */}
      {isInvestor && (
        <Card className="mt-8 border-none shadow-lg">
          <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                Questions & Answers ({allQuestions.length})
              </CardTitle>
              <AskQuestionModal startupId={id!} />
            </div>
          </CardHeader>
          {allQuestions.length > 0 ? (
            <CardContent className="p-6">
              <QuestionsList questions={allQuestions} />
            </CardContent>
          ) : (
            <CardContent className="py-16 text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900 dark:to-cyan-900 rounded-full mb-4">
                <MessageSquare className="h-10 w-10 text-blue-600 dark:text-cyan-400" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">No questions asked yet</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Be the first to ask a question about this startup</p>
            </CardContent>
          )}
        </Card>
      )}
    </div>
    </div>
  )
}
