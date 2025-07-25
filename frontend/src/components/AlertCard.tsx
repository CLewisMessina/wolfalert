'use client'

import { useState } from 'react'
import { AlertCard as AlertCardType } from '@/types'
import { ChevronDown, Bookmark, X, ExternalLink } from 'lucide-react'
import { clsx } from 'clsx'

interface AlertCardProps {
  alert: AlertCardType
  onSave: (articleId: string) => void
  onDismiss: (articleId: string) => void
  onExpand?: (articleId: string) => void
  className?: string
}

const AlertCard = ({ alert, onSave, onDismiss, onExpand, className }: AlertCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const { article, insight, time_ago, is_primary } = alert

  // Get impact type styling
  const getImpactStyling = () => {
    switch (insight.impact_type) {
      case 'threat':
        return {
          badge: 'badge-threat',
          glow: 'threat-glow',
          emoji: '⚠️',
          label: 'CRITICAL THREAT',
          color: 'text-red-400'
        }
      case 'opportunity':
        return {
          badge: 'badge-opportunity',
          glow: 'opportunity-glow',
          emoji: '📈',
          label: 'OPPORTUNITY',
          color: 'text-green-400'
        }
      case 'watch':
        return {
          badge: 'badge-watch',
          glow: 'watch-glow',
          emoji: '👁️',
          label: 'WATCH',
          color: 'text-blue-400'
        }
      default:
        return {
          badge: 'badge-watch',
          glow: 'watch-glow',
          emoji: '👁️',
          label: 'WATCH',
          color: 'text-blue-400'
        }
    }
  }

  const styling = getImpactStyling()

  const handleToggleExpand = () => {
    const newExpanded = !isExpanded
    setIsExpanded(newExpanded)
    if (newExpanded) {
      onExpand?.(article.id)
    }
  }

  const handleSave = async () => {
    setIsLoading(true)
    try {
      onSave(article.id)
      // Show success feedback here
    } catch (error) {
      console.error('Error saving alert:', error)
      // Show error feedback here
    } finally {
      setIsLoading(false)
    }
  }

  const handleDismiss = async () => {
    setIsLoading(true)
    try {
      onDismiss(article.id)
      // Show success feedback here
    } catch (error) {
      console.error('Error dismissing alert:', error)
      // Show error feedback here
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={clsx(className, styling.glow)}>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <span className={styling.badge}>
              {styling.emoji} {styling.label}
            </span>
            <div className="w-2 h-2 bg-current rounded-full animate-pulse" style={{ color: styling.color.replace('text-', '') }}></div>
            <span className="text-xs text-gray-400">
              {time_ago} • {article.source_name}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-xs text-gray-400">Impact Score</div>
          <div className={clsx("text-lg font-bold", styling.color)}>
            {insight.impact_score.toFixed(2)}
          </div>
        </div>
      </div>
      
      {/* Title */}
      <h2 className={clsx(
        "font-bold text-white mb-6 leading-tight",
        is_primary ? "text-2xl" : "text-lg"
      )}>
        {article.title}
      </h2>
      
      {/* Impact Reasoning */}
      <div className={clsx(
        "border rounded-xl p-6 mb-6",
        insight.impact_type === 'threat' && "bg-red-500/10 border-red-500/20",
        insight.impact_type === 'opportunity' && "bg-green-500/10 border-green-500/20",
        insight.impact_type === 'watch' && "bg-blue-500/10 border-blue-500/20"
      )}>
        <h3 className={clsx("text-sm font-semibold mb-3 flex items-center", styling.color)}>
          <span className="w-2 h-2 bg-current rounded-full mr-2"></span>
          {insight.impact_type === 'threat' && 'Why This Threatens Your Business'}
          {insight.impact_type === 'opportunity' && 'Why This Is An Opportunity'}
          {insight.impact_type === 'watch' && 'Why This Matters To Monitor'}
        </h3>
        <p className={clsx(
          "text-gray-200 leading-relaxed",
          is_primary ? "text-lg" : "text-sm"
        )}>
          {insight.impact_reasoning}
        </p>
      </div>
      
      {/* Expandable Summary */}
      <div className="border-t border-white/10 pt-6">
        <button 
          onClick={handleToggleExpand}
          className="flex items-center justify-between w-full text-left hover:bg-white/5 p-3 rounded-lg transition-all duration-200"
          aria-expanded={isExpanded}
        >
          <span className="text-sm font-medium text-gray-300">
            {isExpanded ? 'Hide' : 'Show'} Technical Summary
          </span>
          <ChevronDown 
            className={clsx(
              "w-4 h-4 text-gray-400 transition-transform duration-200",
              isExpanded && "rotate-180"
            )} 
          />
        </button>
        
        {isExpanded && (
          <div className="mt-4 p-4 glass-morphism rounded-lg animate-slide-up">
            <p className="text-gray-300 leading-relaxed text-sm">
              {insight.summary}
            </p>
          </div>
        )}
      </div>
      
      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-6 border-t border-white/10">
        <div className="flex space-x-3">
          <button 
            onClick={handleSave}
            disabled={isLoading}
            className="btn-secondary flex items-center space-x-2 disabled:opacity-50"
            title="Save to Report"
          >
            <Bookmark className="w-4 h-4" />
            <span>Save to Report</span>
            {isLoading && <div className="loading-spinner w-4 h-4"></div>}
          </button>
          
          <button 
            onClick={handleDismiss}
            disabled={isLoading}
            className="btn-ghost flex items-center space-x-2 disabled:opacity-50"
            title="Not Relevant"
          >
            <X className="w-4 h-4" />
            <span>Not Relevant</span>
          </button>
        </div>
        
        <a 
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-wolf-accent hover:text-purple-400 transition-colors flex items-center space-x-1"
        >
          <span>Read Original Article</span>
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}

export default AlertCard