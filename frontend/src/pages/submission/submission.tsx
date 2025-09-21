import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, useFieldArray } from 'react-hook-form'
import { Plus, X, Upload, FileText, Loader2 } from 'lucide-react'
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

export function SubmissionPage() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const navigate = useNavigate()
  const { toast } = useToast()

  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors },
  } = useForm<StartupSubmissionForm>({
    defaultValues: {
      founders: [{ name: '', email: '', role: '', bio: '', previous_experience: [], education: [] }],
      metadata: {
        key_metrics: {},
        competitive_advantages: [],
        traction_highlights: [],
      },
    },
  })

  const { fields: founders, append: addFounder, remove: removeFounder } = useFieldArray({
    control,
    name: 'founders',
  })

  const { fields: advantages, append: addAdvantage, remove: removeAdvantage } = useFieldArray({
    control,
    name: 'metadata.competitive_advantages',
  })

  const { fields: highlights, append: addHighlight, remove: removeHighlight } = useFieldArray({
    control,
    name: 'metadata.traction_highlights',
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      setUploadedFiles(prev => [...prev, ...acceptedFiles])
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

  const onSubmit = async (data: StartupSubmissionForm) => {
    setIsSubmitting(true)
    try {
      // Create startup submission
      const startup = await startupsApi.create({
        ...data,
        documents: uploadedFiles,
      })

      toast({
        title: 'Startup submitted successfully!',
        description: 'Your startup has been submitted for review and analysis.',
        variant: 'success',
      })

      navigate(`/startups/${startup.id}`)
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
    <div className="p-6 max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight">Submit Your Startup</h1>
        <p className="text-muted-foreground mt-2">
          Provide comprehensive information about your startup for AI-powered analysis
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Company Information */}
        <Card>
          <CardHeader>
            <CardTitle>Company Information</CardTitle>
            <CardDescription>Basic details about your startup</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="company_name">Company Name *</Label>
                <Input
                  id="company_name"
                  {...register('company_info.name', { required: 'Company name is required' })}
                  className={cn(errors.company_info?.name && 'border-destructive')}
                />
                {errors.company_info?.name && (
                  <p className="text-sm text-destructive">{errors.company_info.name.message}</p>
                )}
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
                <Label htmlFor="location">Location *</Label>
                <Input
                  id="location"
                  placeholder="City, Country"
                  {...register('company_info.location', { required: 'Location is required' })}
                  className={cn(errors.company_info?.location && 'border-destructive')}
                />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="employee_count">Team Size</Label>
                <Input
                  id="employee_count"
                  type="number"
                  placeholder="Number of employees"
                  {...register('company_info.employee_count', { valueAsNumber: true })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="funding_raised">Funding Raised (USD)</Label>
                <Input
                  id="funding_raised"
                  type="number"
                  placeholder="Total funding raised"
                  {...register('company_info.funding_raised', { valueAsNumber: true })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="funding_seeking">Funding Seeking (USD)</Label>
                <Input
                  id="funding_seeking"
                  type="number"
                  placeholder="Amount seeking to raise"
                  {...register('company_info.funding_seeking', { valueAsNumber: true })}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Founders */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Founders & Team</CardTitle>
                <CardDescription>Information about the founding team</CardDescription>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => addFounder({ name: '', email: '', role: '', bio: '', previous_experience: [], education: [] })}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Founder
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {founders.map((field, index) => (
              <div key={field.id} className="p-4 border rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Founder {index + 1}</h4>
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
                      placeholder="Founder's full name"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Email *</Label>
                    <Input
                      type="email"
                      {...register(`founders.${index}.email`, { required: 'Email is required' })}
                      placeholder="founder@company.com"
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Role *</Label>
                    <Input
                      {...register(`founders.${index}.role`, { required: 'Role is required' })}
                      placeholder="CEO, CTO, etc."
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
                  <Label>Bio</Label>
                  <Textarea
                    {...register(`founders.${index}.bio`)}
                    placeholder="Brief background and experience..."
                    rows={3}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Competitive Advantages */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Competitive Advantages</CardTitle>
                <CardDescription>What sets your startup apart from competitors</CardDescription>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => addAdvantage('')}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Advantage
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {advantages.map((field, index) => (
              <div key={field.id} className="flex items-center gap-2">
                <Input
                  {...register(`metadata.competitive_advantages.${index}` as const)}
                  placeholder="Describe a competitive advantage..."
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeAdvantage(index)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
            {advantages.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No competitive advantages added yet. Click "Add Advantage" to get started.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Traction Highlights */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Traction Highlights</CardTitle>
                <CardDescription>Key metrics and achievements that demonstrate traction</CardDescription>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => addHighlight('')}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Highlight
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {highlights.map((field, index) => (
              <div key={field.id} className="flex items-center gap-2">
                <Input
                  {...register(`metadata.traction_highlights.${index}` as const)}
                  placeholder="e.g., 10,000+ active users, $50K MRR, Partnership with Fortune 500..."
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeHighlight(index)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
            {highlights.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No traction highlights added yet. Click "Add Highlight" to get started.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Documents */}
        <Card>
          <CardHeader>
            <CardTitle>Documents</CardTitle>
            <CardDescription>
              Upload pitch deck, business plan, financial models, and other relevant documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={cn(
                "file-upload-area",
                isDragActive && "drag-active"
              )}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium mb-2">
                {isDragActive ? 'Drop files here' : 'Upload documents'}
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Drag & drop files here, or click to select files
              </p>
              <p className="text-xs text-muted-foreground">
                Supported: PDF, PPTX, DOCX, XLSX, TXT, MD (max 50MB each)
              </p>
            </div>

            {uploadedFiles.length > 0 && (
              <div className="mt-6 space-y-2">
                <h4 className="font-medium">Uploaded Files</h4>
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-muted-foreground" />
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

        {/* Submit */}
        <div className="flex justify-end gap-4">
          <Button type="button" variant="outline" onClick={() => navigate('/startups')}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Submit for Analysis
          </Button>
        </div>
      </form>
    </div>
  )
}
