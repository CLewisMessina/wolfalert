// components/ErrorMessage.tsx
'use client'

import { AlertCircle, RefreshCw } from 'lucide-react'
import { clsx } from 'clsx'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
  className?: string
}

export const ErrorMessage = ({ 
  message, 
  onRetry,
  className 
}: ErrorMessageProps) => {
  return (
    <div className={clsx(
      'glass-morphism rounded-xl p-8 text-center max-w-md mx-auto',
      className
    )}>
      <div className="flex justify-center mb-4">
        <AlertCircle className="w-12 h-12 text-red-400" />
      </div>
      
      <h3 className="text-lg font-semibold text-white mb-2">
        Something went wrong
      </h3>
      
      <p className="text-gray-400 mb-6">
        {message}
      </p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-primary flex items-center space-x-2 mx-auto"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Try Again</span>
        </button>
      )}
    </div>
  )
}

// Export default for compatibility
export default LoadingSpinner