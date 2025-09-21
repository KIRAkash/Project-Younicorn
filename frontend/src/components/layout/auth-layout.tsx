import { FileText } from 'lucide-react'

interface AuthLayoutProps {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:flex-1 lg:flex-col lg:justify-center lg:px-12 bg-minerva-50 dark:bg-minerva-950">
        <div className="max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-minerva-500 rounded-xl flex items-center justify-center">
              <FileText className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-minerva-900 dark:text-minerva-100">
                Project Minerva
              </h1>
              <p className="text-minerva-600 dark:text-minerva-400 text-sm">
                AI-Powered Due Diligence
              </p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-minerva-900 dark:text-minerva-100 mb-3">
                Transform Your Investment Process
              </h2>
              <p className="text-minerva-700 dark:text-minerva-300 leading-relaxed">
                Leverage advanced AI agents to analyze startups comprehensively, 
                from team assessment to market validation, all in one intelligent platform.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-minerva-500 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-minerva-900 dark:text-minerva-100">
                    Multi-Agent Analysis
                  </h3>
                  <p className="text-sm text-minerva-600 dark:text-minerva-400">
                    Specialized AI agents for team, market, product, and competition analysis
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-minerva-500 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-minerva-900 dark:text-minerva-100">
                    Interactive Dashboard
                  </h3>
                  <p className="text-sm text-minerva-600 dark:text-minerva-400">
                    Real-time insights with AI transparency and source traceability
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-minerva-500 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-minerva-900 dark:text-minerva-100">
                    Collaborative Workflow
                  </h3>
                  <p className="text-sm text-minerva-600 dark:text-minerva-400">
                    Team collaboration with comments, notes, and decision tracking
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Auth form */}
      <div className="flex-1 flex flex-col justify-center px-6 py-12 lg:px-8 bg-background">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          {/* Mobile branding */}
          <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
            <div className="w-10 h-10 bg-minerva-500 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Project Minerva</h1>
              <p className="text-sm text-muted-foreground">AI-Powered Due Diligence</p>
            </div>
          </div>
          
          {children}
        </div>
      </div>
    </div>
  )
}
