'use client'

import { DashboardStats } from '@/types'
import { clsx } from 'clsx'
import { AlertTriangle, TrendingUp, Eye, Activity } from 'lucide-react'

interface StatsBarProps {
  stats: DashboardStats
  className?: string
}

const StatsBar = ({ stats, className }: StatsBarProps) => {
  const statItems = [
    {
      key: 'threats',
      value: stats.threats,
      label: 'Threats',
      color: 'text-red-400',
      bgColor: 'hover:bg-red-500/10',
      icon: AlertTriangle
    },
    {
      key: 'opportunities',
      value: stats.opportunities,
      label: 'Opportunities',
      color: 'text-green-400',
      bgColor: 'hover:bg-green-500/10',
      icon: TrendingUp
    },
    {
      key: 'watch',
      value: stats.watch,
      label: 'Watch',
      color: 'text-blue-400',
      bgColor: 'hover:bg-blue-500/10',
      icon: Eye
    },
    {
      key: 'total_alerts',
      value: stats.total_alerts,
      label: 'Total Alerts',
      color: 'text-wolf-accent',
      bgColor: 'hover:bg-wolf-accent/10',
      icon: Activity
    }
  ]

  return (
    <div className={clsx('grid grid-cols-2 md:grid-cols-4 gap-4', className)}>
      {statItems.map((item) => {
        const Icon = item.icon
        
        return (
          <div
            key={item.key}
            className={clsx(
              'glass-morphism p-4 rounded-xl transition-all duration-200 cursor-pointer',
              item.bgColor
            )}
            role="button"
            tabIndex={0}
            title={`${item.value} ${item.label}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className={clsx('text-2xl font-bold', item.color)}>
                {item.value}
              </div>
              <Icon className={clsx('w-5 h-5', item.color)} />
            </div>
            <div className="text-xs text-gray-400 uppercase tracking-wider font-medium">
              {item.label}
            </div>
            
            {/* Optional: Progress indicator for relative values */}
            {item.key !== 'total_alerts' && (
              <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={clsx(
                    'h-full transition-all duration-500 rounded-full',
                    item.key === 'threats' && 'bg-red-400',
                    item.key === 'opportunities' && 'bg-green-400',
                    item.key === 'watch' && 'bg-blue-400'
                  )}
                  style={{
                    width: `${Math.min((item.value / stats.total_alerts) * 100, 100)}%`
                  }}
                />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default StatsBar