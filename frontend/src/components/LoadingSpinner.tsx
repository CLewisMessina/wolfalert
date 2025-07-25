// components/LoadingSpinner.tsx
'use client'

import { clsx } from 'clsx'

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  message?: string
  className?: string
}

export const LoadingSpinner = ({ 
  size = 'medium', 
  message,
  className 
}: LoadingSpinnerProps) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  }

  return (
    <div className={clsx('flex flex-col items-center justify-center', className)}>
      <div className={clsx(
        'animate-spin rounded-full border-2 border-gray-700 border-t-wolf-accent',
        sizeClasses[size]
      )} />
      {message && (
        <p className="mt-4 text-sm text-gray-400 animate-pulse">
          {message}
        </p>
      )}
    </div>
  )
}