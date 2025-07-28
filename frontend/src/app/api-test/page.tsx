// src/app/api-test/page.tsx
/**
 * API Test Page
 * Single Responsibility: Provide a dedicated page for testing API connectivity during Phase 2
 * 
 * This page:
 * - Tests API endpoints in isolation
 * - Shows configuration details
 * - Validates Phase 2 implementation
 * - Will be removed after Phase 2 completion
 */

'use client'

import { useEffect } from 'react'
import ApiTest from '@/components/dev/ApiTest'
import { logConfig, config } from '@/config/env'

export default function ApiTestPage() {
  useEffect(() => {
    // Log configuration on page load
    logConfig()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-wolf-bg via-slate-900 to-wolf-primary">
      <div className="container-wolf py-8">
        <div className="max-w-4xl mx-auto">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              🔧 Phase 2: API Testing
            </h1>
            <p className="text-gray-400">
              Testing API client integration with the backend. Environment: {config.env}
            </p>
          </div>

          {/* API Test Component */}
          <ApiTest />

          {/* Instructions */}
          <div className="mt-8 p-6 bg-gray-800 rounded-lg border border-gray-700">
            <h2 className="text-lg font-bold text-white mb-3">Phase 2 Checklist:</h2>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-center space-x-2">
                <span className="text-green-400">✅</span>
                <span>API client created with proper error handling</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-green-400">✅</span>
                <span>Environment configuration centralized</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-yellow-400">🔄</span>
                <span>Test API connection (click "Test Connection" above)</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-yellow-400">🔄</span>
                <span>Test profile creation (click "Test Create Profile" above)</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-gray-400">⏸️</span>
                <span>Create basic UI components (next step)</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}