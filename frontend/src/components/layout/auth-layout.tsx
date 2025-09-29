
import { AuroraBackground } from '@/components/ui/aurora-background'

interface AuthLayoutProps {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <AuroraBackground>
      <div className="min-h-screen flex relative">
        {/* Left side - Branding */}
        <div className="hidden lg:flex lg:flex-1 lg:flex-col lg:justify-center lg:px-12 bg-white/20 dark:bg-black/20 backdrop-blur-sm">
        <div className="max-w-md">
          <div className="flex flex-col items-center mb-8 mt-12">
            <img 
              src="/logo.png" 
              alt="Younicorns Logo" 
              className="w-32 h-auto mb-4"
            />
            <p className="text-minerva-600 dark:text-minerva-400 text-sm text-center">
              Where unicorns are born
            </p>
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
        <div className="flex-1 flex flex-col justify-center px-6 py-12 lg:px-8 bg-white/30 dark:bg-black/30 backdrop-blur-sm">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          {/* Mobile branding */}
          <div className="flex flex-col items-center justify-center mb-8 lg:hidden">
            <img 
              src="/logo.png" 
              alt="Younicorns Logo" 
              className="w-24 h-auto mb-2"
            />
            <p className="text-sm text-muted-foreground text-center">Where unicorns are born</p>
          </div>
          
          {children}
        </div>
        </div>
      </div>
    </AuroraBackground>
  )
}
