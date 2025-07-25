'use client'

import { useState, useEffect } from 'react'
import { UserProfile, DashboardData } from '@/types'
import Header from '@/components/Header'
import StatsBar from '@/components/StatsBar'
import AlertCard from '@/components/AlertCard'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorMessage from '@/components/ErrorMessage'

// Mock data for development - will be replaced with API calls
const mockProfile: UserProfile = {
  id: '1',
  profile_name: 'Marketing • SaaS • Mid-level',
  industry: 'technology',
  department: 'marketing',
  role_level: 'manager',
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

const mockDashboardData: DashboardData = {
  profile: mockProfile,
  stats: {
    threats: 3,
    opportunities: 7,
    watch: 12,
    total_alerts: 22
  },
  primary_alert: {
    article: {
      id: '1',
      url: 'https://openai.com/blog/example',
      title: 'OpenAI Launches Advanced Customer Service AI That Outperforms Human Agents',
      content: 'Sample content...',
      source_name: 'OpenAI Blog',
      source_reliability: 'high',
      published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      fetched_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      is_processed: true,
      processing_attempts: 1
    },
    insight: {
      id: '1',
      article_id: '1',
      profile_hash: 'abc123',
      summary: 'OpenAI\'s new system integrates with existing CRM platforms and handles complex multi-step issues across chat, email, and voice channels.',
      impact_reasoning: 'Customer expectations will shift dramatically. If competitors adopt this 94% accurate AI system, they\'ll offer instant, 24/7 support at lower costs. Your current support model may suddenly look slow and expensive, potentially losing customers who expect AI-level responsiveness.',
      impact_type: 'threat',
      impact_score: 0.94,
      processing_time_ms: 1500,
      created_at: new Date().toISOString()
    },
    time_ago: '2 hours ago',
    is_primary: true
  },
  secondary_alerts: [
    {
      article: {
        id: '2',
        url: 'https://google.com/blog/example',
        title: 'Google Releases Free AI Marketing Attribution Tool for SMBs',
        content: 'Sample content...',
        source_name: 'Google Blog',
        source_reliability: 'high',
        published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        fetched_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        is_processed: true,
        processing_attempts: 1
      },
      insight: {
        id: '2',
        article_id: '2',
        profile_hash: 'abc123',
        summary: 'Google\'s free tool could level the playing field with larger competitors who use expensive attribution software.',
        impact_reasoning: 'Competitive advantage opportunity: This free tool could level the playing field with larger competitors who use expensive attribution software, potentially improving your ROI tracking by 40-60%.',
        impact_type: 'opportunity',
        impact_score: 0.78,
        processing_time_ms: 1200,
        created_at: new Date().toISOString()
      },
      time_ago: '4 hours ago'
    },
    {
      article: {
        id: '3',
        url: 'https://microsoft.com/blog/example',
        title: 'Microsoft Copilot Integrates with Salesforce and HubSpot',
        content: 'Sample content...',
        source_name: 'Microsoft Blog',
        source_reliability: 'high',
        published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        fetched_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        is_processed: true,
        processing_attempts: 1
      },
      insight: {
        id: '3',
        article_id: '3',
        profile_hash: 'abc123',
        summary: 'Microsoft Copilot now integrates with major CRM platforms for AI-powered insights.',
        impact_reasoning: 'Monitor for workflow impact: If your team uses either CRM, this could streamline operations and provide AI insights for lead scoring within 3-6 months.',
        impact_type: 'watch',
        impact_score: 0.65,
        processing_time_ms: 1100,
        created_at: new Date().toISOString()
      },
      time_ago: '6 hours ago'
    }
  ],
  last_updated: '2 hours ago',
  next_refresh: '1h 23m',
  source_count: 47
}

export default function HomePage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Simulate API call
    const loadDashboard = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        // In production, this would be an actual API call:
        // const response = await fetch('/api/dashboard/1')
        // const data = await response.json()
        
        setDashboardData(mockDashboardData)
      } catch (err) {
        setError('Failed to load dashboard data')
        console.error('Dashboard load error:', err)
      } finally {
        setIsLoading(false)
      }
    }

    loadDashboard()
  }, [])

  const handleSaveAlert = (articleId: string) => {
    console.log('Saving alert:', articleId)
    // TODO: Implement save to report functionality
  }

  const handleDismissAlert = (articleId: string) => {
    console.log('Dismissing alert:', articleId)
    // TODO: Implement dismiss functionality
  }

  const handleExpandAlert = (articleId: string) => {
    console.log('Expanding alert:', articleId)
    // TODO: Implement expand functionality
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" message="Loading your intelligence dashboard..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message={error} onRetry={() => window.location.reload()} />
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message="No dashboard data available" />
      </div>
    )
  }

  return (
    <>
      <Header currentProfile={dashboardData.profile} />
      
      <main className="container-wolf py-8">
        {/* Stats Bar */}
        <StatsBar stats={dashboardData.stats} className="mb-8 animate-fade-in" />

        {/* Primary Alert Card */}
        {dashboardData.primary_alert && (
          <div className="mb-8 animate-slide-up">
            <AlertCard
              alert={dashboardData.primary_alert}
              onSave={handleSaveAlert}
              onDismiss={handleDismissAlert}
              onExpand={handleExpandAlert}
              className="alert-card-primary"
            />
          </div>
        )}

        {/* Secondary Alert Cards */}
        {dashboardData.secondary_alerts.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
            {dashboardData.secondary_alerts.map((alert, index) => (
              <div 
                key={alert.article.id} 
                className="animate-slide-up"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <AlertCard
                  alert={alert}
                  onSave={handleSaveAlert}
                  onDismiss={handleDismissAlert}
                  onExpand={handleExpandAlert}
                  className="alert-card cursor-pointer"
                />
              </div>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="text-center animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <div className="glass-morphism inline-flex items-center px-6 py-3 rounded-full">
            <div className="w-2 h-2 bg-wolf-accent rounded-full animate-pulse mr-3"></div>
            <span className="text-sm text-gray-300">
              Last updated {dashboardData.last_updated} • {dashboardData.stats.total_alerts} alerts from {dashboardData.source_count} sources • Next refresh in {dashboardData.next_refresh}
            </span>
          </div>
        </div>
      </main>
    </>
  )
}