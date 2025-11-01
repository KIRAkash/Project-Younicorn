// This component will be the existing detailed form submission
// For now, we'll import and wrap the existing submission component
// The actual implementation will reuse most of the existing submission.tsx logic

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, useFieldArray } from 'react-hook-form'
import { ArrowLeft, Building2, Users as UsersIcon, Target, TrendingUp, IndianRupee, Scale, Rocket, Plus, X, Upload, FileText, Loader2, Sparkles, ArrowRight } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { startupsApi } from '@/services/api'
import { useToast } from '@/hooks/use-toast'
import { StartupSubmissionForm } from '@/types'
import { formatFileSize, cn } from '@/utils'
import { StartupLogoUpload } from '@/components/startup-logo-upload'

interface FormSubmissionProps {
  onBack: () => void
}

export function FormSubmission({ onBack }: FormSubmissionProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [logoUrl, setLogoUrl] = useState<string | undefined>()
  const [logoGcsPath, setLogoGcsPath] = useState<string | undefined>()
  const [startupId] = useState(() => `temp-${Date.now()}`)
  const navigate = useNavigate()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    control,
    setValue,
    trigger,
    formState: { errors },
  } = useForm<StartupSubmissionForm>({
    defaultValues: {
      company_info: {
        product_stage: 'idea' as any,
        company_structure: 'private_limited' as any,
        incorporation_location: 'India',
      },
      founders: [{ 
        name: '', 
        email: '', 
        role: '', 
        bio: '', 
        previous_experience: [], 
        education: [],
        previous_exits: '',
        domain_expertise_years: undefined,
        key_achievements: ''
      }],
      metadata: {
        key_metrics: {},
        competitive_advantages: [],
        traction_highlights: [],
        advisory_board: [],
        main_competitors: [],
      },
    },
  })

  const { fields: founders, append: addFounder, remove: removeFounder } = useFieldArray({
    control,
    name: 'founders',
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      // Validate file sizes
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
      setUploadedFiles(prev => [...prev, ...validFiles])
    },
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  })

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
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

  const nextStep = async () => {
    let fieldsToValidate: any[] = []
    
    if (currentStep === 1) {
      fieldsToValidate = [
        'company_info.name',
        'company_info.description',
        'company_info.industry',
        'company_info.funding_stage',
        'company_info.location',
        'company_info.product_stage',
        'company_info.company_structure',
        'company_info.incorporation_location',
        'founders',
      ]
    }

    const isValid = await trigger(fieldsToValidate as any)
    if (isValid) {
      setCurrentStep(2)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const prevStep = () => {
    setCurrentStep(1)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const onSubmit = async (data: StartupSubmissionForm) => {
    setIsSubmitting(true)
    try {
      const documentsData = await Promise.all(
        uploadedFiles.map(async (file) => ({
          filename: file.name,
          content_type: file.type,
          data: await fileToBase64(file),
          size: file.size,
        }))
      )

      const submissionData = {
        submission_type: 'form',
        ...data,
        documents: documentsData,
      }

      const response = await startupsApi.create(submissionData)
      
      toast({
        title: 'Success!',
        description: 'Your startup has been submitted for analysis',
      })

      navigate(`/startups/${response.id}`)
    } catch (error) {
      toast({
        title: 'Submission failed',
        description: error instanceof Error ? error.message : 'Failed to submit startup',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-8 shadow-2xl">
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
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-4xl font-black text-white">Form Submission</h1>
            </div>
            <div className="text-white/90 text-lg font-bold">
              Step {currentStep} of 2
            </div>
          </div>
          <p className="text-white/90 text-lg max-w-2xl font-medium">
            Complete the detailed form below. You can also upload supporting documents.
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

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* STEP 1: Basic Information */}
        {currentStep === 1 && (
          <div className="space-y-8 animate-in fade-in duration-500">
            {/* Company Information */}
            <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-blue-500">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                    <Building2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Company Information</CardTitle>
                    <CardDescription className="text-base">Basic details about your startup</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 pt-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="company_name">Company Name *</Label>
                    <Input
                      id="company_name"
                      {...register('company_info.name', { required: 'Company name is required' })}
                      placeholder="Enter company name"
                      className={cn(errors.company_info?.name && 'border-destructive')}
                    />
                    {errors.company_info?.name && (
                      <p className="text-sm text-destructive">{errors.company_info.name.message}</p>
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
                        setValue('company_info.logo_url' as any, signedUrl)
                      }}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="website_url">Website URL</Label>
                    <Input
                      id="website_url"
                      type="url"
                      placeholder="https://example.com"
                      {...register('company_info.website_url')}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Company Description *</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe what your company does, the problem you solve, and your solution..."
                    rows={4}
                    {...register('company_info.description', { required: 'Description is required' })}
                    className={cn(errors.company_info?.description && 'border-destructive')}
                  />
                  {errors.company_info?.description && (
                    <p className="text-sm text-destructive">{errors.company_info.description.message}</p>
                  )}
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label>Industry *</Label>
                    <Select onValueChange={(value) => setValue('company_info.industry', value)}>
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
                        <SelectItem value="blockchain">Blockchain</SelectItem>
                        <SelectItem value="cybersecurity">Cybersecurity</SelectItem>
                        <SelectItem value="climate_tech">Climate Tech</SelectItem>
                        <SelectItem value="biotech">BioTech</SelectItem>
                        <SelectItem value="hardware">Hardware</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Funding Stage *</Label>
                    <Select onValueChange={(value) => setValue('company_info.funding_stage', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select stage" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pre_seed">Pre-Seed</SelectItem>
                        <SelectItem value="seed">Seed</SelectItem>
                        <SelectItem value="series_a">Series A</SelectItem>
                        <SelectItem value="series_b">Series B</SelectItem>
                        <SelectItem value="series_c">Series C</SelectItem>
                        <SelectItem value="later_stage">Later Stage</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Product Stage *</Label>
                    <Select onValueChange={(value) => setValue('company_info.product_stage', value as any)} defaultValue="idea">
                      <SelectTrigger>
                        <SelectValue placeholder="Select stage" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="idea">Idea</SelectItem>
                        <SelectItem value="prototype">Prototype</SelectItem>
                        <SelectItem value="mvp">MVP</SelectItem>
                        <SelectItem value="beta">Beta</SelectItem>
                        <SelectItem value="live">Live/Production</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="location">Location *</Label>
                    <Input
                      id="location"
                      placeholder="e.g., Bangalore, Karnataka"
                      {...register('company_info.location', { required: 'Location is required' })}
                      className={cn(errors.company_info?.location && 'border-destructive')}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="employee_count">Team Size</Label>
                    <Input
                      id="employee_count"
                      type="number"
                      placeholder="Number of employees"
                      {...register('company_info.employee_count', { valueAsNumber: true })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="technology_stack">Technology Stack</Label>
                  <Textarea
                    id="technology_stack"
                    placeholder="e.g., React, Node.js, PostgreSQL, AWS..."
                    rows={3}
                    {...register('company_info.technology_stack')}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="ip_patents">IP/Patents</Label>
                    <Textarea
                      id="ip_patents"
                      placeholder="Any intellectual property or patents filed/granted"
                      rows={3}
                      {...register('company_info.ip_patents')}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="product_roadmap">Product Roadmap</Label>
                    <Textarea
                      id="product_roadmap"
                      placeholder="Key milestones for next 12-24 months"
                      rows={3}
                      {...register('company_info.product_roadmap')}
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Company Structure *</Label>
                    <Select onValueChange={(value) => setValue('company_info.company_structure', value as any)} defaultValue="private_limited">
                      <SelectTrigger>
                        <SelectValue placeholder="Select structure" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="private_limited">Private Limited</SelectItem>
                        <SelectItem value="llp">LLP</SelectItem>
                        <SelectItem value="sole_proprietorship">Sole Proprietorship</SelectItem>
                        <SelectItem value="partnership">Partnership</SelectItem>
                        <SelectItem value="public_limited">Public Limited</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="incorporation_location">Incorporation Location *</Label>
                    <Input
                      id="incorporation_location"
                      placeholder="e.g., India"
                      {...register('company_info.incorporation_location', { required: 'Incorporation location is required' })}
                      defaultValue="India"
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
                    {...register('company_info.target_customer_profile')}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="customer_acquisition_cost">CAC (₹)</Label>
                    <Input
                      id="customer_acquisition_cost"
                      type="number"
                      placeholder="Customer Acquisition Cost in INR"
                      {...register('company_info.customer_acquisition_cost', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lifetime_value">LTV (₹)</Label>
                    <Input
                      id="lifetime_value"
                      type="number"
                      placeholder="Lifetime Value in INR"
                      {...register('company_info.lifetime_value', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="current_customer_count">Current Customers</Label>
                    <Input
                      id="current_customer_count"
                      type="number"
                      placeholder="Number of customers"
                      {...register('company_info.current_customer_count', { valueAsNumber: true })}
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="customer_retention_rate">Retention Rate (%)</Label>
                    <Input
                      id="customer_retention_rate"
                      type="number"
                      placeholder="Customer retention percentage"
                      {...register('company_info.customer_retention_rate', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="geographic_markets">Geographic Markets</Label>
                    <Input
                      id="geographic_markets"
                      placeholder="e.g., India, Southeast Asia"
                      {...register('company_info.geographic_markets')}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="go_to_market_strategy">Go-to-Market Strategy</Label>
                  <Textarea
                    id="go_to_market_strategy"
                    placeholder="Describe your strategy to acquire and retain customers"
                    rows={4}
                    {...register('company_info.go_to_market_strategy')}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="market_size_tam">TAM (₹ Crores)</Label>
                    <Input
                      id="market_size_tam"
                      type="number"
                      placeholder="Total Addressable Market"
                      {...register('metadata.market_size_tam', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="market_size_sam">SAM (₹ Crores)</Label>
                    <Input
                      id="market_size_sam"
                      type="number"
                      placeholder="Serviceable Addressable Market"
                      {...register('metadata.market_size_sam', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="market_size_som">SOM (₹ Crores)</Label>
                    <Input
                      id="market_size_som"
                      type="number"
                      placeholder="Serviceable Obtainable Market"
                      {...register('metadata.market_size_som', { valueAsNumber: true })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Founders & Team */}
            <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-purple-500">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
                      <UsersIcon className="w-6 h-6 text-white" />
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
                    onClick={() => addFounder({ 
                      name: '', 
                      email: '', 
                      role: '', 
                      bio: '', 
                      previous_experience: [], 
                      education: [],
                      previous_exits: '',
                      domain_expertise_years: undefined,
                      key_achievements: ''
                    })}
                    className="bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 border-2"
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

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-2">
                        <Label>Domain Expertise (Years)</Label>
                        <Input
                          type="number"
                          {...register(`founders.${index}.domain_expertise_years`, { valueAsNumber: true })}
                          placeholder="Years of experience in this domain"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Previous Exits</Label>
                        <Input
                          {...register(`founders.${index}.previous_exits`)}
                          placeholder="Any previous successful exits"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Bio</Label>
                      <Textarea
                        {...register(`founders.${index}.bio`)}
                        placeholder="Brief background and experience"
                        rows={3}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Key Achievements</Label>
                      <Textarea
                        {...register(`founders.${index}.key_achievements`)}
                        placeholder="Notable achievements and accomplishments"
                        rows={2}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Navigation */}
            <div className="flex justify-end gap-4 pt-4">
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
                size="lg"
                className="px-8 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold shadow-lg"
              >
                Next: Traction & Financials
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* STEP 2: Traction, Financial, Legal & Vision */}
        {currentStep === 2 && (
          <div className="space-y-8 animate-in fade-in duration-500">
            {/* Traction & Metrics */}
            <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-orange-50 to-red-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-orange-500">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Traction & Metrics</CardTitle>
                    <CardDescription className="text-base">Revenue, growth, and key performance indicators</CardDescription>
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
                      {...register('company_info.monthly_recurring_revenue', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="annual_recurring_revenue">ARR (₹)</Label>
                    <Input
                      id="annual_recurring_revenue"
                      type="number"
                      placeholder="Annual Recurring Revenue"
                      {...register('company_info.annual_recurring_revenue', { valueAsNumber: true })}
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="revenue_growth_rate">Revenue Growth (%)</Label>
                    <Input
                      id="revenue_growth_rate"
                      type="number"
                      placeholder="Month-over-month %"
                      {...register('company_info.revenue_growth_rate', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="user_growth_rate">User Growth (%)</Label>
                    <Input
                      id="user_growth_rate"
                      type="number"
                      placeholder="Month-over-month %"
                      {...register('company_info.user_growth_rate', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="runway_months">Runway (Months)</Label>
                    <Input
                      id="runway_months"
                      type="number"
                      placeholder="Months of runway"
                      {...register('company_info.runway_months', { valueAsNumber: true })}
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="burn_rate">Burn Rate (₹/month)</Label>
                    <Input
                      id="burn_rate"
                      type="number"
                      placeholder="Monthly cash burn in INR"
                      {...register('company_info.burn_rate', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="revenue_run_rate">Revenue Run Rate (₹)</Label>
                    <Input
                      id="revenue_run_rate"
                      type="number"
                      placeholder="Annual revenue run rate"
                      {...register('company_info.revenue_run_rate', { valueAsNumber: true })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="key_performance_indicators">Key Performance Indicators</Label>
                  <Textarea
                    id="key_performance_indicators"
                    placeholder="List your most important KPIs and their current values"
                    rows={4}
                    {...register('company_info.key_performance_indicators')}
                  />
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
                      {...register('company_info.funding_raised', { valueAsNumber: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="funding_seeking">Funding Seeking (₹)</Label>
                    <Input
                      id="funding_seeking"
                      type="number"
                      placeholder="Amount seeking to raise"
                      {...register('company_info.funding_seeking', { valueAsNumber: true })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="previous_funding_rounds">Previous Funding Rounds</Label>
                  <Textarea
                    id="previous_funding_rounds"
                    placeholder="Details of previous funding rounds (Seed ₹50L from XYZ Ventures, etc.)"
                    rows={3}
                    {...register('company_info.previous_funding_rounds')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="current_investors">Current Investors</Label>
                  <Textarea
                    id="current_investors"
                    placeholder="List of existing investors"
                    rows={2}
                    {...register('company_info.current_investors')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="use_of_funds">Use of Funds</Label>
                  <Textarea
                    id="use_of_funds"
                    placeholder="How will you use the capital you're raising?"
                    rows={4}
                    {...register('company_info.use_of_funds')}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="profitability_timeline">Profitability Timeline</Label>
                    <Input
                      id="profitability_timeline"
                      placeholder="e.g., 18-24 months"
                      {...register('company_info.profitability_timeline')}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="unit_economics">Unit Economics</Label>
                    <Input
                      id="unit_economics"
                      placeholder="e.g., Gross margin 70%, CAC payback 6 months"
                      {...register('company_info.unit_economics')}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Legal & Compliance */}
            <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-indigo-500">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-lg">
                    <Scale className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Legal & Compliance</CardTitle>
                    <CardDescription className="text-base">Legal information and regulatory requirements</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 pt-6">
                <div className="space-y-2">
                  <Label htmlFor="regulatory_requirements">Regulatory Requirements</Label>
                  <Textarea
                    id="regulatory_requirements"
                    placeholder="Any special licenses, compliance requirements, or regulatory considerations"
                    rows={3}
                    {...register('company_info.regulatory_requirements')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="legal_issues">Legal Issues</Label>
                  <Textarea
                    id="legal_issues"
                    placeholder="Any pending litigation, IP disputes, or legal concerns"
                    rows={3}
                    {...register('company_info.legal_issues')}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Vision & Strategy */}
            <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-purple-500">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
                    <Rocket className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Vision & Strategy</CardTitle>
                    <CardDescription className="text-base">Long-term vision and strategic goals</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 pt-6">
                <div className="space-y-2">
                  <Label htmlFor="mission_statement">Mission Statement</Label>
                  <Textarea
                    id="mission_statement"
                    placeholder="Your company's mission and purpose"
                    rows={3}
                    {...register('company_info.mission_statement')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="five_year_vision">5-Year Vision</Label>
                  <Textarea
                    id="five_year_vision"
                    placeholder="Where do you see the company in 5 years?"
                    rows={4}
                    {...register('company_info.five_year_vision')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="exit_strategy">Exit Strategy</Label>
                  <Textarea
                    id="exit_strategy"
                    placeholder="e.g., IPO, Acquisition, etc."
                    rows={3}
                    {...register('company_info.exit_strategy')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="social_impact">Social Impact</Label>
                  <Textarea
                    id="social_impact"
                    placeholder="Any social or environmental impact goals"
                    rows={3}
                    {...register('company_info.social_impact')}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Documents Upload */}
            <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 border-b-4 border-green-500">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg">
                    <Upload className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Documents</CardTitle>
                    <CardDescription className="text-base">
                      Upload pitch deck, business plan, financial models, and other relevant documents
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-6">
                <div
                  {...getRootProps()}
                  className={cn(
                    'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all',
                    isDragActive ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                  )}
                >
                  <input {...getInputProps()} />
                  <div className="flex flex-col items-center">
                    <div className="p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-4">
                      <Upload className="w-12 h-12 text-white" />
                    </div>
                    <p className="text-xl font-bold mb-2 text-gray-900 dark:text-white">
                      {isDragActive ? 'Drop files here' : 'Upload Documents'}
                    </p>
                    <p className="text-base text-gray-600 dark:text-gray-300 mb-2">
                      Drag & drop files here, or click to select files
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Supported: PDF, PPTX, DOCX, XLSX, TXT, MD (max 50MB each)
                    </p>
                  </div>
                </div>

                {uploadedFiles.length > 0 && (
                  <div className="mt-6 space-y-2">
                    <h4 className="font-medium text-lg">Uploaded Files</h4>
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border">
                        <div className="flex items-center gap-3">
                          <FileText className="w-5 h-5 text-blue-500" />
                          <div>
                            <p className="font-medium">{file.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
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
                className="px-8 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold shadow-lg"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Submit for AI Analysis
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </form>
    </div>
  )
}
