import { Link } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import { 
  Rocket, 
  TrendingUp, 
  Users, 
  Sparkles, 
  Target,
  BarChart3,
  Zap,
  Shield,
  Globe,
  ArrowRight,
  Star,
  Brain,
  LineChart,
  Eye,
  Briefcase,
  Package,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AuroraBackground } from '@/components/ui/aurora-background'

// Intersection Observer hook for scroll animations
function useInView(options = {}) {
  const ref = useRef<HTMLDivElement>(null)
  const [isInView, setIsInView] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsInView(true)
      }
    }, { threshold: 0.1, ...options })

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [])

  return { ref, isInView }
}

// Animated section component
function AnimatedSection({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const { ref, isInView } = useInView()
  return (
    <div
      ref={ref}
      className={`transition-all duration-1000 ${isInView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'} ${className}`}
    >
      {children}
    </div>
  )
}

export function LandingPage() {
  return (
    <AuroraBackground showRadialGradient={false}>
      <div className="min-h-screen">
        {/* Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/20 dark:border-gray-700/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="Younicorn" className="h-10 w-auto" />
            </div>
            <div className="flex items-center gap-3">
              <Button variant="ghost" className="text-gray-900 dark:text-white hover:bg-white/10 dark:hover:bg-gray-800/50" asChild>
                <Link to="/login">Login</Link>
              </Button>
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white" asChild>
                <Link to="/auth/register">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

        {/* Hero Section */}
        <div className="relative overflow-hidden pt-32 pb-20">
          <div className="relative max-w-7xl mx-auto px-6 text-center">
          {/* Large Logo */}
            <div className="flex justify-center mb-8">
              <img src="/logo_notext.png" alt="Younicorn" className="h-72 w-auto" />
            </div>
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black mb-6 leading-tight">
            <span className="bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Here is your chance!
            </span>
            <span className="block bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              Don't Miss It.
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-700 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
            We connect exceptional founders with visionary investors. 
            <span className="font-bold text-purple-600 dark:text-purple-400"> AI-powered insights</span> to make smarter decisions, faster.
          </p>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12 max-w-4xl mx-auto">
            <AnimatedSection>
              <div className="bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 dark:border-gray-700/30 shadow-xl">
                <div className="text-4xl font-black bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">1,247</div>
                <div className="text-sm text-gray-900 dark:text-gray-100 font-medium">Startups Registered</div>
              </div>
            </AnimatedSection>
            <AnimatedSection>
              <div className="bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 dark:border-gray-700/30 shadow-xl">
                <div className="text-4xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">$2.4B</div>
                <div className="text-sm text-gray-900 dark:text-gray-100 font-medium">Amount Raised</div>
              </div>
            </AnimatedSection>
            <AnimatedSection>
              <div className="bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 dark:border-gray-700/30 shadow-xl">
                <div className="text-4xl font-black bg-gradient-to-r from-cyan-600 to-green-600 bg-clip-text text-transparent mb-2">856</div>
                <div className="text-sm text-gray-900 dark:text-gray-100 font-medium">Active Investors</div>
              </div>
            </AnimatedSection>
            <AnimatedSection>
              <div className="bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 dark:border-gray-700/30 shadow-xl">
                <div className="text-4xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-2">94%</div>
                <div className="text-sm text-gray-900 dark:text-gray-100 font-medium">Success Rate</div>
              </div>
            </AnimatedSection>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-2xl text-lg px-8 py-6" asChild>
              <Link to="/auth/register">
                <Rocket className="w-5 h-5 mr-2" />
                Start Your Journey
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 text-gray-900 dark:text-gray-100 hover:bg-white/30 dark:hover:bg-gray-900/30 text-lg px-8 py-6" asChild>
              <Link to="/startups">
                <Eye className="w-5 h-5 mr-2" />
                Explore Startups
              </Link>
            </Button>
          </div>
          </div>
        </div>

        {/* For Founders & Investors Split Section */}
        <div className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-8">
            {/* For Founders */}
            <AnimatedSection>
              <Card className="border border-white/30 dark:border-gray-700/30 shadow-2xl hover:shadow-3xl transition-all duration-500 hover:-translate-y-2 bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl overflow-hidden group h-full">
                <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-400/20 to-blue-400/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
                <CardContent className="p-10 relative">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl mb-6 group-hover:scale-110 transition-transform">
                    <Rocket className="w-8 h-8 text-white" />
                  </div>
                  <h2 className="text-4xl font-black mb-4 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                    For Founders
                  </h2>
                  <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
                    Get your startup in front of the right investors with AI-powered analysis
                  </p>
                  <ul className="space-y-4 mb-8">
                    {[
                      { icon: Sparkles, text: 'AI-Powered Analysis in Minutes' },
                      { icon: Target, text: 'Match with Perfect Investors' },
                      { icon: TrendingUp, text: 'Real-time Valuation Insights' },
                      { icon: Shield, text: 'Secure & Confidential' },
                      { icon: Zap, text: 'Fast-Track Funding Process' },
                    ].map((item, i) => (
                      <li key={i} className="flex items-start gap-3 group/item">
                        <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center group-hover/item:scale-110 transition-transform">
                          <item.icon className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-gray-700 dark:text-gray-300 font-medium">{item.text}</span>
                      </li>
                    ))}
                  </ul>
                  <Button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-lg py-6" asChild>
                    <Link to="/submit">
                      Submit Your Startup
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </AnimatedSection>

            {/* For Investors */}
            <AnimatedSection>
              <Card className="border border-white/30 dark:border-gray-700/30 shadow-2xl hover:shadow-3xl transition-all duration-500 hover:-translate-y-2 bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl overflow-hidden group h-full">
                <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-400/20 to-green-400/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
                <CardContent className="p-10 relative">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-cyan-600 to-green-600 rounded-2xl mb-6 group-hover:scale-110 transition-transform">
                    <TrendingUp className="w-8 h-8 text-white" />
                  </div>
                  <h2 className="text-4xl font-black mb-4 bg-gradient-to-r from-cyan-600 to-green-600 bg-clip-text text-transparent">
                    For Investors
                  </h2>
                  <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
                    Discover high-potential startups with data-driven insights
                  </p>
                  <ul className="space-y-4 mb-8">
                    {[
                      { icon: Brain, text: 'AI-Driven Deal Sourcing' },
                      { icon: BarChart3, text: 'Comprehensive Analytics' },
                      { icon: LineChart, text: 'Risk Assessment & Scoring' },
                      { icon: Users, text: 'Team Evaluation Insights' },
                      { icon: Globe, text: 'Market Opportunity Analysis' },
                    ].map((item, i) => (
                      <li key={i} className="flex items-start gap-3 group/item">
                        <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-br from-cyan-500 to-green-500 rounded-lg flex items-center justify-center group-hover/item:scale-110 transition-transform">
                          <item.icon className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-gray-700 dark:text-gray-300 font-medium">{item.text}</span>
                      </li>
                    ))}
                  </ul>
                  <Button className="w-full bg-gradient-to-r from-cyan-600 to-green-600 hover:from-cyan-700 hover:to-green-700 text-white text-lg py-6" asChild>
                    <Link to="/startups">
                      Browse Startups
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </AnimatedSection>
          </div>
        </div>
      </div>

        {/* Testimonials */}
        <AnimatedSection className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 border-purple-200 dark:border-purple-800">
              <Star className="w-4 h-4 mr-2" />
              Testimonials
            </Badge>
            <h2 className="text-5xl font-black mb-4 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Loved by Founders & Investors
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              See what our community has to say
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: 'Sarah Chen',
                role: 'Founder, TechFlow AI',
                avatar: '👩‍💼',
                text: 'Younicorn helped us raise $2M in seed funding within 3 months. The AI analysis gave investors confidence in our vision!',
                rating: 5,
              },
              {
                name: 'Michael Rodriguez',
                role: 'Partner, Venture Capital',
                avatar: '👨‍💼',
                text: 'The quality of deal flow has improved dramatically. AI-powered insights save us weeks of due diligence.',
                rating: 5,
              },
              {
                name: 'Priya Sharma',
                role: 'Founder, HealthTech Innovations',
                avatar: '👩‍⚕️',
                text: 'From submission to funding in 6 weeks! The platform made it incredibly easy to connect with the right investors.',
                rating: 5,
              },
            ].map((testimonial, i) => (
              <Card key={i} className="border border-white/30 dark:border-gray-700/30 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl">
                <CardContent className="p-8">
                  <div className="flex gap-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, j) => (
                      <Star key={j} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 mb-6 italic">
                    "{testimonial.text}"
                  </p>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full flex items-center justify-center text-2xl">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <div className="font-bold text-gray-900 dark:text-gray-100">{testimonial.name}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{testimonial.role}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </AnimatedSection>

        {/* Features Section */}
        <AnimatedSection className="py-32">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-20">
              <Badge className="mb-4 bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 border-purple-200 dark:border-purple-800">
                <Sparkles className="w-4 h-4 mr-2" />
                Platform Features
              </Badge>
              <h2 className="text-6xl font-black text-gray-900 dark:text-gray-100 mb-6">
                Everything You Need to
                <span className="block text-purple-600 dark:text-purple-400">
                  Succeed
                </span>
              </h2>
              <p className="text-xl text-gray-700 dark:text-gray-300 max-w-3xl mx-auto">
                Powered by cutting-edge AI technology to give you the competitive edge
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: Brain,
                  title: 'AI-Powered Analysis',
                  description: 'Advanced machine learning algorithms analyze team, market, product, and competition in minutes.',
                  gradient: 'from-purple-500 to-pink-500',
                },
                {
                  icon: Target,
                  title: 'Smart Matching',
                  description: 'Intelligent algorithms match startups with investors based on industry, stage, and investment thesis.',
                  gradient: 'from-blue-500 to-cyan-500',
                },
                {
                  icon: BarChart3,
                  title: 'Comprehensive Metrics',
                  description: 'Track key performance indicators, valuation, and growth metrics in real-time dashboards.',
                  gradient: 'from-green-500 to-emerald-500',
                },
                {
                  icon: Shield,
                  title: 'Secure & Private',
                  description: 'Bank-level encryption and strict access controls keep your sensitive data protected.',
                  gradient: 'from-orange-500 to-red-500',
                },
                {
                  icon: Zap,
                  title: 'Lightning Fast',
                  description: 'Get comprehensive analysis in minutes, not weeks. Make faster, data-driven decisions.',
                  gradient: 'from-yellow-500 to-orange-500',
                },
                {
                  icon: Users,
                  title: 'Collaborative Tools',
                  description: 'Share insights, collaborate with team members, and communicate directly with stakeholders.',
                  gradient: 'from-indigo-500 to-purple-500',
                },
              ].map((feature, i) => (
                <Card key={i} className="border border-white/30 dark:border-gray-700/30 bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl hover:bg-white/30 dark:hover:bg-gray-900/30 transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl group">
                  <CardContent className="p-8">
                    <div className={`inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br ${feature.gradient} rounded-2xl mb-6 group-hover:scale-110 transition-transform`}>
                      <feature.icon className="w-7 h-7 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-3">{feature.title}</h3>
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{feature.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </AnimatedSection>

        {/* CTA Section */}
        <AnimatedSection className="py-20 bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-500">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
            Ready to Transform Your Future?
          </h2>
          <p className="text-xl text-white/90 mb-10">
            Join thousands of founders and investors already using Younicorn
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-white text-purple-600 hover:bg-white/90 shadow-2xl text-lg px-10 py-7" asChild>
              <Link to="/auth/register">
                <Rocket className="w-6 h-6 mr-2" />
                Get Started Free
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 text-lg px-10 py-7" asChild>
              <Link to="/login" className="text-black">
                Sign In
                <ArrowRight className="w-6 h-6 ml-2" />
              </Link>
            </Button>
          </div>
        </div>
        </AnimatedSection>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <img src="/logo.png" alt="Younicorn" className="h-8 w-auto" />
                <span className="text-xl font-black">Younicorn</span>
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered platform connecting exceptional founders with visionary investors.
              </p>
            </div>
            <div>
              <h4 className="font-bold mb-4 text-gray-400">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link to="/startups" className="hover:text-white transition-colors">Browse Startups</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4 text-gray-400">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/about" className="hover:text-white transition-colors">About Us</Link></li>
                <li><Link to="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link to="/careers" className="hover:text-white transition-colors">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4 text-gray-400">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm text-gray-400">
            <p className="font-bold mb-4 text-gray-400">© 2024 Younicorn. All rights reserved. Built with ❤️ for founders and investors.</p>
          </div>
          </div>
        </footer>
      </div>
    </AuroraBackground>
  )
}
