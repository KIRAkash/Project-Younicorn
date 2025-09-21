import { Link } from 'react-router-dom'
import { Home, ArrowLeft, Search } from 'lucide-react'

import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="mb-8">
          <div className="text-9xl font-bold text-muted-foreground/20 mb-4">404</div>
          <h1 className="text-3xl font-bold mb-2">Page Not Found</h1>
          <p className="text-muted-foreground">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-2 justify-center">
            <Button asChild>
              <Link to="/dashboard">
                <Home className="w-4 h-4 mr-2" />
                Go to Dashboard
              </Link>
            </Button>
            <Button variant="outline" onClick={() => window.history.back()}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Go Back
            </Button>
          </div>

          <div className="text-sm text-muted-foreground">
            <p>Looking for something specific?</p>
            <div className="flex items-center justify-center gap-2 mt-2">
              <Search className="w-4 h-4" />
              <span>Try using the search bar in the navigation</span>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t">
          <p className="text-xs text-muted-foreground">
            If you believe this is an error, please{' '}
            <a href="mailto:support@projectminerva.ai" className="text-primary hover:underline">
              contact support
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
