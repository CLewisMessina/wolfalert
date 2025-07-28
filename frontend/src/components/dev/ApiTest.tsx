// src/components/dev/ApiTest.tsx
/**
 * API Connection Test Component
 * Single Responsibility: Test and display API connection status for development
 * 
 * This component:
 * - Tests API connectivity on mount
 * - Displays connection status
 * - Shows API configuration
 * - Provides manual test buttons
 * 
 * Note: This is a development-only component for testing Phase 2
 */

'use client'

import { useState, useEffect } from 'react'
import { healthApi, profileApi, getApiBaseUrl, ApiError } from '@/utils/api'
import { config, isFeatureEnabled } from '@/config/env'
import { UserProfile } from '@/types'

interface ConnectionStatus {
  isConnected: boolean
  health?: any
  database?: any
  profiles?: UserProfile[]
  error?: string
  lastChecked?: Date
}

export default function ApiTest() {
  const [status, setStatus] = useState<ConnectionStatus>({
    isConnected: false,
    lastChecked: undefined,
  })
  const [isLoading, setIsLoading] = useState(false)

  // Test API connection on component mount
  useEffect(() => {
    testConnection()
  }, [])

  const testConnection = async () => {
    setIsLoading(true)
    
    try {
      // Test health endpoint
      const health = await healthApi.checkHealth()
      
      // Test database endpoint
      const database = await healthApi.testDatabase()
      
      // Test profiles endpoint (should return empty array if no profiles)
      const profiles = await profileApi.getProfiles()
      
      setStatus({
        isConnected: true,
        health,
        database,
        profiles,
        lastChecked: new Date(),
        error: undefined,
      })
      
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? `${error.message} (Status: ${error.status})`
        : error instanceof Error 
        ? error.message 
        : 'Unknown error'
      
      setStatus({
        isConnected: false,
        error: errorMessage,
        lastChecked: new Date(),
      })
    } finally {
      setIsLoading(false)
    }
  }

  const testCreateProfile = async () => {
    setIsLoading(true)
    
    try {
      const testProfile = {
        profile_name: `Test Profile ${Date.now()}`,
        industry: 'technology' as const,
        department: 'engineering' as const,
        role_level: 'manager' as const,
      }
      
      const createdProfile = await profileApi.createProfile(testProfile)
      
      // Refresh profiles list
      const profiles = await profileApi.getProfiles()
      
      setStatus(prev => ({
        ...prev,
        profiles,
        lastChecked: new Date(),
      }))
      
      alert(`✅ Profile created successfully! ID: ${createdProfile.id}`)
      
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? `${error.message} (Status: ${error.status})`
        : error instanceof Error 
        ? error.message 
        : 'Unknown error'
      
      alert(`❌ Failed to create profile: ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }

  // Only show this component in development
  if (!isFeatureEnabled('enableDebugLogs')) {
    return null
  }

  return (
    <div className="p-6 bg-gray-800 rounded-lg border border-gray-700 mb-6">
      <h2 className="text-xl font-bold mb-4 text-white">
        🔧 API Connection Test (Dev Only)
      </h2>
      
      {/* Configuration Info */}
      <div className="mb-4 p-3 bg-gray-900 rounded">
        <h3 className="font-semibold text-gray-300 mb-2">Configuration:</h3>
        <div className="text-sm text-gray-400 space-y-1">
          <div>Environment: <span className="text-blue-400">{config.env}</span></div>
          <div>API Base: <span className="text-blue-400">{getApiBaseUrl()}</span></div>
          <div>Timeout: <span className="text-blue-400">{config.api.timeout}ms</span></div>
          <div>Last Checked: <span className="text-blue-400">
            {status.lastChecked?.toLocaleTimeString() || 'Never'}
          </span></div>
        </div>
      </div>
      
      {/* Connection Status */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <div className={`w-3 h-3 rounded-full ${
            status.isConnected ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span className="text-white font-medium">
            {status.isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        {status.error && (
          <div className="text-red-400 text-sm p-2 bg-red-900/20 rounded">
            Error: {status.error}
          </div>
        )}
      </div>
      
      {/* Test Results */}
      {status.isConnected && (
        <div className="mb-4 space-y-3">
          {/* Health Status */}
          {status.health && (
            <div className="p-2 bg-green-900/20 rounded">
              <div className="text-green-400 text-sm font-medium">Health Check:</div>
              <div className="text-gray-300 text-xs">
                Service: {status.health.service} | 
                Database: {status.health.database} | 
                Version: {status.health.version}
              </div>
            </div>
          )}
          
          {/* Database Status */}
          {status.database && (
            <div className="p-2 bg-blue-900/20 rounded">
              <div className="text-blue-400 text-sm font-medium">Database:</div>
              <div className="text-gray-300 text-xs">
                Status: {status.database.database} | 
                Tables: {status.database.tables_found?.length || 0} found
              </div>
            </div>
          )}
          
          {/* Profiles Status */}
          {status.profiles && (
            <div className="p-2 bg-purple-900/20 rounded">
              <div className="text-purple-400 text-sm font-medium">Profiles:</div>
              <div className="text-gray-300 text-xs">
                {status.profiles.length} profile(s) found
                {status.profiles.length > 0 && (
                  <div className="mt-1">
                    Latest: {status.profiles[0]?.profile_name}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={testConnection}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 
                   text-white rounded text-sm font-medium transition-colors"
        >
          {isLoading ? 'Testing...' : 'Test Connection'}
        </button>
        
        {status.isConnected && (
          <button
            onClick={testCreateProfile}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 
                     text-white rounded text-sm font-medium transition-colors"
          >
            {isLoading ? 'Creating...' : 'Test Create Profile'}
          </button>
        )}
      </div>
    </div>
  )
}