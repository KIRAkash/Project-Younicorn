import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, useFieldArray } from 'react-hook-form'
import { ArrowLeft, Video, Upload, X, Loader2, Rocket, Sparkles, Play, StopCircle, FileText, Lightbulb, CheckCircle, Plus, Users, TrendingUp, IndianRupee, Target } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { startupsApi } from '@/services/api'
import { useToast } from '@/hooks/use-toast'
import { formatFileSize, cn } from '@/utils'
import type { ProductStage, CompanyStructure } from '@/types'
import { StartupLogoUpload } from '@/components/startup-logo-upload'

interface VideoSubmissionProps {
  onBack: () => void
}

interface FounderInfo {
  name: string
  email: string
  role: string
  linkedin_url?: string
  domain_expertise_years?: number
}

interface BasicInfoForm {
  company_name: string
  description: string
  industry: string
  funding_stage: string
  location: string
  product_stage: ProductStage
  website_url?: string
  employee_count?: number
  founders: FounderInfo[]
  // Financial
  funding_raised?: number
  funding_seeking?: number
  burn_rate?: number
  runway_months?: number
  // Traction
  monthly_recurring_revenue?: number
  annual_recurring_revenue?: number
  revenue_growth_rate?: number
  user_growth_rate?: number
  // Market
  target_customer_profile?: string
  customer_acquisition_cost?: number
  lifetime_value?: number
  market_size_tam?: number
  market_size_sam?: number
  market_size_som?: number
}

export function VideoSubmission({ onBack }: VideoSubmissionProps) {
  const [currentStep, setCurrentStep] = useState(1) // 1: Video, 2: Basic Info
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null)
  const [uploadedDocs, setUploadedDocs] = useState<File[]>([])
  const [liveStream, setLiveStream] = useState<MediaStream | null>(null)
  const [logoUrl, setLogoUrl] = useState<string | undefined>()
  const [logoGcsPath, setLogoGcsPath] = useState<string | undefined>()
  const [startupId] = useState(() => `temp-${Date.now()}`)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const videoChunksRef = useRef<Blob[]>([])
  const liveVideoRef = useRef<HTMLVideoElement>(null)
  const navigate = useNavigate()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<BasicInfoForm>({
    defaultValues: {
      founders: [{ name: '', email: '', role: '', linkedin_url: '', domain_expertise_years: undefined }]
    }
  })

  const { fields: founders, append: addFounder, remove: removeFounder } = useFieldArray({
    control,
    name: 'founders',
  })

  const { getRootProps: getVideoRootProps, getInputProps: getVideoInputProps, isDragActive: isVideoDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0]
      if (file) {
        if (file.size > 50 * 1024 * 1024) {
          toast({
            title: 'File too large',
            description: 'Video file must be less than 50MB',
            variant: 'destructive',
          })
          return
        }
        setVideoFile(file)
        setVideoPreviewUrl(URL.createObjectURL(file))
      }
    },
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.webm', '.mkv'],
    },
    maxSize: 50 * 1024 * 1024,
    multiple: false,
  })

  const { getRootProps: getDocsRootProps, getInputProps: getDocsInputProps, isDragActive: isDocsDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      const validFiles = acceptedFiles.filter(file => {
        if (file.size > 50 * 1024 * 1024) {
          toast({
            title: 'File too large',
            description: `${file.name} exceeds 50MB limit`,
            variant: 'destructive',
          })
          return false
        }
        return true
      })
      setUploadedDocs(prev => [...prev, ...validFiles])
    },
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxSize: 50 * 1024 * 1024,
  })

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      setLiveStream(stream)
      
      // Set live preview
      if (liveVideoRef.current) {
        liveVideoRef.current.srcObject = stream
        liveVideoRef.current.play()
      }
      
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      videoChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          videoChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(videoChunksRef.current, { type: 'video/webm' })
        const file = new File([blob], `video-pitch-${Date.now()}.webm`, { type: 'video/webm' })
        setVideoFile(file)
        setVideoPreviewUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach(track => track.stop())
        setLiveStream(null)
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      toast({
        title: 'Recording failed',
        description: 'Could not access camera/microphone',
        variant: 'destructive',
      })
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      if (liveStream) {
        liveStream.getTracks().forEach(track => track.stop())
        setLiveStream(null)
      }
    }
  }

  const removeVideo = () => {
    setVideoFile(null)
    if (videoPreviewUrl) {
      URL.revokeObjectURL(videoPreviewUrl)
      setVideoPreviewUrl(null)
    }
  }

  const removeDoc = (index: number) => {
    setUploadedDocs(prev => prev.filter((_, i) => i !== index))
  }

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        const base64 = reader.result as string
        const base64Data = base64.split(',')[1]
        resolve(base64Data)
      }
      reader.onerror = error => reject(error)
    })
  }

  const nextStep = () => {
    if (!videoFile) {
      toast({
        title: 'Video required',
        description: 'Please record or upload a video pitch',
        variant: 'destructive',
      })
      return
    }
    setCurrentStep(2)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const prevStep = () => {
    setCurrentStep(1)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const onSubmit = async (data: BasicInfoForm) => {
    if (!videoFile) {
      toast({
        title: 'Video required',
        description: 'Please record or upload a video pitch',
        variant: 'destructive',
      })
      return
    }

    setIsSubmitting(true)
    try {
      // Convert video to base64
      const videoBase64 = await fileToBase64(videoFile)
      
      // Convert documents to base64
      const documentsData = await Promise.all(
        uploadedDocs.map(async (file) => ({
          filename: file.name,
          content_type: file.type,
          data: await fileToBase64(file),
          size: file.size,
        }))
      )

      // Add video as a document
      const allDocuments = [
        {
          filename: videoFile.name,
          content_type: videoFile.type,
          data: videoBase64,
          size: videoFile.size,
        },
        ...documentsData
      ]

      const submissionData = {
        submission_type: 'video',
        company_info: {
          name: data.company_name,
          description: data.description,
          industry: data.industry,
          funding_stage: data.funding_stage,
          location: data.location,
          product_stage: data.product_stage,
          website_url: data.website_url,
          logo_url: logoUrl,  // Include uploaded logo URL
          employee_count: data.employee_count,
          company_structure: 'private_limited' as CompanyStructure,
          incorporation_location: 'India',
          funding_raised: data.funding_raised,
          funding_seeking: data.funding_seeking,
          burn_rate: data.burn_rate,
          runway_months: data.runway_months,
          monthly_recurring_revenue: data.monthly_recurring_revenue,
          annual_recurring_revenue: data.annual_recurring_revenue,
          revenue_growth_rate: data.revenue_growth_rate,
          user_growth_rate: data.user_growth_rate,
          target_customer_profile: data.target_customer_profile,
          customer_acquisition_cost: data.customer_acquisition_cost,
          lifetime_value: data.lifetime_value,
        },
        founders: data.founders.map(f => ({
          name: f.name,
          email: f.email,
          role: f.role,
          linkedin_url: f.linkedin_url,
          domain_expertise_years: f.domain_expertise_years,
          bio: '',
          previous_experience: [],
          education: [],
        })),
        documents: allDocuments,
        metadata: {
          key_metrics: {},
          competitive_advantages: [],
          traction_highlights: [],
          advisory_board: [],
          main_competitors: [],
          market_size_tam: data.market_size_tam,
          market_size_sam: data.market_size_sam,
          market_size_som: data.market_size_som,
        },
      }

      const response = await startupsApi.create(submissionData)
      
      toast({
        title: 'Success!',
        description: 'Your video pitch has been submitted for analysis',
      })

      navigate(`/startups/${response.id}`)
    } catch (error) {
      toast({
        title: 'Submission failed',
        description: error instanceof Error ? error.message : 'Failed to submit video pitch',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 p-8 shadow-2xl">
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={onBack}
                className="text-white hover:bg-white/20"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                <Video className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-4xl font-black text-white">Video Pitch</h1>
            </div>
            <div className="text-white/90 text-lg font-bold">
              Step {currentStep} of 2
            </div>
          </div>
          <p className="text-white/90 text-lg max-w-2xl font-medium">
            {currentStep === 1 
              ? 'Record or upload your video pitch (max 50MB)'
              : 'Provide some basic information about your startup'
            }
          </p>
          
          {/* Progress Bar */}
          <div className="mt-6 bg-white/20 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-white h-full transition-all duration-500 ease-out"
              style={{ width: `${(currentStep / 2) * 100}%` }}
            />
          </div>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full blur-2xl"></div>
      </div>

      {/* STEP 1: Video Upload/Record */}
      {currentStep === 1 && (
        <div className="space-y-8 animate-in fade-in duration-500">
          {/* Pitch Guide */}
          <Card className="border-2 border-blue-200 dark:border-blue-700 shadow-lg bg-blue-50/50 dark:bg-blue-900/20">
            <CardHeader className="bg-gradient-to-r from-blue-100 to-cyan-100 dark:from-blue-900 dark:to-cyan-900 border-b-2 border-blue-300">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg">
                  <Lightbulb className="w-6 h-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold text-blue-900 dark:text-blue-100">What to Include in Your Video Pitch</CardTitle>
                  <CardDescription className="text-base text-blue-700 dark:text-blue-300">Cover these key points for a comprehensive pitch</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Company Overview</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">What problem are you solving? What's your solution?</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Founding Team</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Who are the founders? What's your relevant experience?</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Product Details</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">What stage is your product? Key features and differentiators?</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Market Opportunity</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">What's the market size? Who are your target customers?</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Traction & Metrics</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Current revenue, users, growth rate, and key milestones?</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Funding History</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">How much have you raised? From whom? Current runway?</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Financial Overview</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Current burn rate, revenue projections, path to profitability?</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">Ask & Use of Funds</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">How much are you raising? What will you use it for?</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-purple-500">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
                  <Video className="w-6 h-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold">Your Video Pitch</CardTitle>
                  <CardDescription className="text-base">Record directly or upload a video file</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              {!videoFile ? (
                <>
                  {/* Live Preview during recording */}
                  {isRecording && (
                    <div className="space-y-4">
                      <div className="relative rounded-xl overflow-hidden bg-black">
                        <video
                          ref={liveVideoRef}
                          autoPlay
                          muted
                          playsInline
                          className="w-full max-h-96 mx-auto"
                        />
                        <div className="absolute top-4 right-4 flex items-center gap-2 px-4 py-2 bg-red-500 rounded-full animate-pulse">
                          <div className="w-3 h-3 bg-white rounded-full"></div>
                          <span className="text-white font-bold text-sm">RECORDING</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Recording Controls */}
                  <div className="flex justify-center gap-4">
                    {!isRecording ? (
                      <Button
                        type="button"
                        onClick={startRecording}
                        size="lg"
                        className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-bold shadow-lg"
                      >
                        <Play className="w-5 h-5 mr-2" />
                        Start Recording
                      </Button>
                    ) : (
                      <Button
                        type="button"
                        onClick={stopRecording}
                        size="lg"
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold shadow-lg animate-pulse"
                      >
                        <StopCircle className="w-5 h-5 mr-2" />
                        Stop Recording
                      </Button>
                    )}
                  </div>

                  {!isRecording && (
                    <>
                      <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                          <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                          <span className="px-4 bg-white dark:bg-gray-900 text-gray-500">OR</span>
                        </div>
                      </div>

                      {/* Upload Area */}
                      <div
                        {...getVideoRootProps()}
                        className={cn(
                          'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all',
                          isVideoDragActive ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-purple-400'
                        )}
                      >
                        <input {...getVideoInputProps()} />
                        <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                        <p className="text-xl font-semibold mb-2">
                          {isVideoDragActive ? 'Drop video here' : 'Upload Video File'}
                        </p>
                        <p className="text-sm text-gray-500">
                          Drag & drop or click to browse
                        </p>
                        <p className="text-xs text-gray-400 mt-2">
                          Supported formats: MP4, MOV, AVI, WebM, MKV (Max 50MB)
                        </p>
                      </div>
                    </>
                  )}
                </>
              ) : (
                <div className="space-y-4">
                  <div className="relative rounded-xl overflow-hidden bg-black">
                    {videoPreviewUrl && (
                      <video
                        src={videoPreviewUrl}
                        controls
                        className="w-full max-h-96 mx-auto"
                      />
                    )}
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Video className="w-6 h-6 text-purple-500" />
                      <div>
                        <p className="font-medium">{videoFile.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(videoFile.size)}</p>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={removeVideo}
                    >
                      <X className="w-5 h-5" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Optional Documents */}
          <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-blue-500">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold">Supporting Documents (Optional)</CardTitle>
                  <CardDescription className="text-base">Upload pitch deck, business plan, etc.</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div
                {...getDocsRootProps()}
                className={cn(
                  'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all',
                  isDocsDragActive ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                )}
              >
                <input {...getDocsInputProps()} />
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-semibold mb-2">
                  {isDocsDragActive ? 'Drop files here' : 'Upload Documents'}
                </p>
                <p className="text-sm text-gray-500">
                  PDF, DOCX, PPTX (Max 50MB per file)
                </p>
              </div>

              {uploadedDocs.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold">Uploaded Documents ({uploadedDocs.length})</h4>
                  {uploadedDocs.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-blue-500" />
                        <div>
                          <p className="font-medium">{file.name}</p>
                          <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeDoc(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex justify-between gap-4 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onBack}
              size="lg"
              className="px-8"
            >
              Cancel
            </Button>
            <Button 
              type="button"
              onClick={nextStep}
              disabled={!videoFile}
              size="lg"
              className="px-8 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-bold shadow-lg"
            >
              Next: Basic Information
              <Sparkles className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      )}

      {/* STEP 2: Basic Information */}
      {currentStep === 2 && (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8 animate-in fade-in duration-500">
          <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-blue-500">
              <CardTitle className="text-2xl font-bold">Startup Information</CardTitle>
              <CardDescription className="text-base">Provide key details about your company, team, traction, and market</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="company_name">Company Name *</Label>
                  <Input
                    id="company_name"
                    {...register('company_name', { required: 'Company name is required' })}
                    className={cn(errors.company_name && 'border-destructive')}
                  />
                  {errors.company_name && (
                    <p className="text-sm text-destructive">{errors.company_name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Company Logo (optional)</Label>
                  <StartupLogoUpload
                    startupId={startupId}
                    currentLogoUrl={logoUrl}
                    onUploadSuccess={(signedUrl, gcsPath) => {
                      setLogoUrl(signedUrl)
                      setLogoGcsPath(gcsPath)
                    }}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="website_url">Website URL</Label>
                  <Input
                    id="website_url"
                    type="url"
                    placeholder="https://example.com"
                    {...register('website_url')}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Brief Description *</Label>
                <Textarea
                  id="description"
                  placeholder="What does your startup do?"
                  rows={3}
                  {...register('description', { required: 'Description is required' })}
                  className={cn(errors.description && 'border-destructive')}
                />
                {errors.description && (
                  <p className="text-sm text-destructive">{errors.description.message}</p>
                )}
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label>Industry *</Label>
                  <Select onValueChange={(value) => setValue('industry', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select industry" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fintech">FinTech</SelectItem>
                      <SelectItem value="healthtech">HealthTech</SelectItem>
                      <SelectItem value="edtech">EdTech</SelectItem>
                      <SelectItem value="enterprise_software">Enterprise Software</SelectItem>
                      <SelectItem value="consumer_apps">Consumer Apps</SelectItem>
                      <SelectItem value="ecommerce">E-commerce</SelectItem>
                      <SelectItem value="ai_ml">AI/ML</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Funding Stage *</Label>
                  <Select onValueChange={(value) => setValue('funding_stage', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select stage" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pre_seed">Pre-Seed</SelectItem>
                      <SelectItem value="seed">Seed</SelectItem>
                      <SelectItem value="series_a">Series A</SelectItem>
                      <SelectItem value="series_b">Series B</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Product Stage *</Label>
                  <Select onValueChange={(value) => setValue('product_stage', value as ProductStage)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select stage" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="idea">Idea</SelectItem>
                      <SelectItem value="prototype">Prototype</SelectItem>
                      <SelectItem value="mvp">MVP</SelectItem>
                      <SelectItem value="beta">Beta</SelectItem>
                      <SelectItem value="live">Live</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="location">Location *</Label>
                  <Input
                    id="location"
                    placeholder="e.g., Bangalore, India"
                    {...register('location', { required: 'Location is required' })}
                    className={cn(errors.location && 'border-destructive')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="employee_count">Team Size</Label>
                  <Input
                    id="employee_count"
                    type="number"
                    placeholder="Number of employees"
                    {...register('employee_count', { valueAsNumber: true })}
                  />
                </div>
              </div>

            </CardContent>
          </Card>

          {/* Founders & Team */}
          <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-purple-500">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Founders & Team</CardTitle>
                    <CardDescription className="text-base">Information about the founding team</CardDescription>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => addFounder({ name: '', email: '', role: '', linkedin_url: '', domain_expertise_years: undefined })}
                  className="bg-white dark:bg-gray-800"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Founder
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              {founders.map((field, index) => (
                <div key={field.id} className="p-6 border-2 rounded-xl space-y-4 bg-gray-50 dark:bg-gray-800/50">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-lg">Founder {index + 1}</h4>
                    {founders.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFounder(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Full Name *</Label>
                      <Input
                        {...register(`founders.${index}.name`, { required: 'Name is required' })}
                        placeholder="Founder name"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Email *</Label>
                      <Input
                        type="email"
                        {...register(`founders.${index}.email`, { required: 'Email is required' })}
                        placeholder="founder@example.com"
                      />
                    </div>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Role *</Label>
                      <Input
                        {...register(`founders.${index}.role`, { required: 'Role is required' })}
                        placeholder="e.g., CEO, CTO"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>LinkedIn URL</Label>
                      <Input
                        {...register(`founders.${index}.linkedin_url`)}
                        placeholder="https://linkedin.com/in/..."
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Domain Expertise (Years)</Label>
                    <Input
                      type="number"
                      {...register(`founders.${index}.domain_expertise_years`, { valueAsNumber: true })}
                      placeholder="Years of experience in this domain"
                    />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Traction & Metrics */}
          <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-orange-50 to-red-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-orange-500">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold">Traction & Metrics</CardTitle>
                  <CardDescription className="text-base">Revenue and growth indicators</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="monthly_recurring_revenue">MRR (₹)</Label>
                  <Input
                    id="monthly_recurring_revenue"
                    type="number"
                    placeholder="Monthly Recurring Revenue"
                    {...register('monthly_recurring_revenue', { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="annual_recurring_revenue">ARR (₹)</Label>
                  <Input
                    id="annual_recurring_revenue"
                    type="number"
                    placeholder="Annual Recurring Revenue"
                    {...register('annual_recurring_revenue', { valueAsNumber: true })}
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="revenue_growth_rate">Revenue Growth (%)</Label>
                  <Input
                    id="revenue_growth_rate"
                    type="number"
                    placeholder="Month-over-month %"
                    {...register('revenue_growth_rate', { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="user_growth_rate">User Growth (%)</Label>
                  <Input
                    id="user_growth_rate"
                    type="number"
                    placeholder="Month-over-month %"
                    {...register('user_growth_rate', { valueAsNumber: true })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Financial Details */}
          <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-yellow-500">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg">
                  <IndianRupee className="w-6 h-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold">Financial Details</CardTitle>
                  <CardDescription className="text-base">Funding and financial information</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="funding_raised">Funding Raised (₹)</Label>
                  <Input
                    id="funding_raised"
                    type="number"
                    placeholder="Total funding raised to date"
                    {...register('funding_raised', { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="funding_seeking">Funding Seeking (₹)</Label>
                  <Input
                    id="funding_seeking"
                    type="number"
                    placeholder="Amount seeking to raise"
                    {...register('funding_seeking', { valueAsNumber: true })}
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="burn_rate">Burn Rate (₹/month)</Label>
                  <Input
                    id="burn_rate"
                    type="number"
                    placeholder="Monthly cash burn"
                    {...register('burn_rate', { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="runway_months">Runway (Months)</Label>
                  <Input
                    id="runway_months"
                    type="number"
                    placeholder="Months of runway"
                    {...register('runway_months', { valueAsNumber: true })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Market & Customer */}
          <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-green-500">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold">Market & Customer</CardTitle>
                  <CardDescription className="text-base">Target market and customer information</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="space-y-2">
                <Label htmlFor="target_customer_profile">Target Customer Profile</Label>
                <Textarea
                  id="target_customer_profile"
                  placeholder="Describe your ideal customer (B2B/B2C, demographics, company size, etc.)"
                  rows={3}
                  {...register('target_customer_profile')}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="customer_acquisition_cost">CAC (₹)</Label>
                  <Input
                    id="customer_acquisition_cost"
                    type="number"
                    placeholder="Customer Acquisition Cost"
                    {...register('customer_acquisition_cost', { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lifetime_value">LTV (₹)</Label>
                  <Input
                    id="lifetime_value"
                    type="number"
                    placeholder="Lifetime Value"
                    {...register('lifetime_value', { valueAsNumber: true })}
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="market_size_tam">TAM (₹ Crores)</Label>
                  <Input
                    id="market_size_tam"
                    type="number"
                    placeholder="Total Addressable Market"
                    {...register('market_size_tam', { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="market_size_sam">SAM (₹ Crores)</Label>
                  <Input
                    id="market_size_sam"
                    type="number"
                    placeholder="Serviceable Addressable Market"
                    {...register('market_size_sam', { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="market_size_som">SOM (₹ Crores)</Label>
                  <Input
                    id="market_size_som"
                    type="number"
                    placeholder="Serviceable Obtainable Market"
                    {...register('market_size_som', { valueAsNumber: true })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex justify-between gap-4 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={prevStep}
              size="lg"
              className="px-8"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </Button>
            <Button 
              type="submit"
              disabled={isSubmitting}
              size="lg"
              className="px-8 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold shadow-lg"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Rocket className="w-5 h-5 mr-2" />
                  Submit for Analysis
                </>
              )}
            </Button>
          </div>
        </form>
      )}
    </div>
  )
}
