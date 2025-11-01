import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Video, Mic, ArrowRight, Sparkles, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FormSubmission } from './flows/FormSubmission'
import { VideoSubmission } from './flows/VideoSubmission'
import { AudioSubmission } from './flows/AudioSubmission'

type SubmissionFlow = 'select' | 'form' | 'video' | 'audio'

export function SubmissionPage() {
  const [selectedFlow, setSelectedFlow] = useState<SubmissionFlow>('select')
  const navigate = useNavigate()

  const handleFlowSelect = (flow: SubmissionFlow) => {
    setSelectedFlow(flow)
  }

  const handleBack = () => {
    setSelectedFlow('select')
  }

  if (selectedFlow === 'form') {
    return <FormSubmission onBack={handleBack} />
  }

  if (selectedFlow === 'video') {
    return <VideoSubmission onBack={handleBack} />
  }

  if (selectedFlow === 'audio') {
    return <AudioSubmission onBack={handleBack} />
  }

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Hero Header */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-12 shadow-2xl">
          <div className="relative z-10 text-center">
            <div className="flex items-center justify-center mb-6">
              <div className="p-4 bg-white/20 backdrop-blur-sm rounded-2xl">
                <Sparkles className="w-12 h-12 text-white" />
              </div>
            </div>
            <h1 className="text-5xl font-black text-white mb-4">
              Let's Get to Know Your Startup!
            </h1>
            <p className="text-white/90 text-xl max-w-3xl mx-auto font-medium">
              Choose a way to share information about you and your startup. We'll analyze it and provide comprehensive insights.
            </p>
          </div>
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-72 h-72 bg-white/10 rounded-full blur-2xl"></div>
        </div>

        {/* Flow Selection Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Flow 1: Form Submission */}
          <Card 
            className="group cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 border-4 border-transparent hover:border-blue-500 bg-white dark:bg-gray-800"
            onClick={() => handleFlowSelect('form')}
          >
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 p-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <FileText className="w-12 h-12 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Fill Out a Form
              </CardTitle>
              <CardDescription className="text-base mt-2">
                Complete a detailed form with all your startup information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <p className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold">✓</span>
                  <span>Comprehensive company details</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold">✓</span>
                  <span>Team and founder information</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold">✓</span>
                  <span>Upload supporting documents</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-blue-500 font-bold">✓</span>
                  <span>Financial and traction metrics</span>
                </p>
              </div>
              <Button 
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold shadow-lg group-hover:shadow-xl transition-all"
                size="lg"
              >
                Start Form
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>

          {/* Flow 2: Video Pitch */}
          <Card 
            className="group cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 border-4 border-transparent hover:border-purple-500 bg-white dark:bg-gray-800"
            onClick={() => handleFlowSelect('video')}
          >
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 p-6 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Video className="w-12 h-12 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                Video Pitch
              </CardTitle>
              <CardDescription className="text-base mt-2">
                Record or upload a video pitch about your startup
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <p className="flex items-start gap-2">
                  <span className="text-purple-500 font-bold">✓</span>
                  <span>Record directly or upload video</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-purple-500 font-bold">✓</span>
                  <span>Quick basic information form</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-purple-500 font-bold">✓</span>
                  <span>Optional document uploads</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-purple-500 font-bold">✓</span>
                  <span>Up to 50MB video file</span>
                </p>
              </div>
              <Button 
                className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-bold shadow-lg group-hover:shadow-xl transition-all"
                size="lg"
              >
                Record Video
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>

          {/* Flow 3: Audio Pitch */}
          <Card 
            className="group cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 border-4 border-transparent hover:border-pink-500 bg-white dark:bg-gray-800"
            onClick={() => handleFlowSelect('audio')}
          >
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 p-6 bg-gradient-to-br from-pink-500 to-red-600 rounded-2xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Mic className="w-12 h-12 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-red-600 bg-clip-text text-transparent">
                Audio Pitch
              </CardTitle>
              <CardDescription className="text-base mt-2">
                Record or upload an audio pitch about your startup
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <p className="flex items-start gap-2">
                  <span className="text-pink-500 font-bold">✓</span>
                  <span>Record directly or upload audio</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-pink-500 font-bold">✓</span>
                  <span>Quick basic information form</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-pink-500 font-bold">✓</span>
                  <span>Optional document uploads</span>
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-pink-500 font-bold">✓</span>
                  <span>Up to 50MB audio file</span>
                </p>
              </div>
              <Button 
                className="w-full bg-gradient-to-r from-pink-500 to-red-600 hover:from-pink-600 hover:to-red-700 text-white font-bold shadow-lg group-hover:shadow-xl transition-all"
                size="lg"
              >
                Record Audio
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Info Section */}
        <Card className="border-2 border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 backdrop-blur">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Upload className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-2">What Happens Next?</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  After you submit your information, our AI-powered analysis system will review your startup across multiple dimensions including team, market, product, and competition. You'll receive a comprehensive investment analysis report within minutes.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
