// src/config/env.ts
/**
 * Environment Configuration
 * Single Responsibility: Centralize all environment variable handling and validation
 * 
 * This file manages:
 * - Environment variable validation
 * - Default values for development
 * - Type-safe configuration access
 * - Environment-specific settings
 */

/**
 * Application environment types
 */
export type Environment = 'development' | 'staging' | 'production'

/**
 * Configuration interface for type safety
 */
interface AppConfig {
  // Environment
  env: Environment
  isDev: boolean
  isProd: boolean
  
  // API Configuration
  api: {
    baseUrl: string
    timeout: number
  }
  
  // Features flags
  features: {
    enableMockData: boolean
    enableDebugLogs: boolean
    enableAnalytics: boolean
  }
  
  // UI Configuration
  ui: {
    defaultTheme: 'dark' | 'light'
    animationsEnabled: boolean
  }
}

/**
 * Get environment with validation
 */
function getEnvironment(): Environment {
  const env = process.env.NEXT_PUBLIC_ENV?.toLowerCase()
  
  switch (env) {
    case 'production':
    case 'prod':
      return 'production'
    case 'staging':
    case 'stage':
      return 'staging'
    case 'development':
    case 'dev':
    default:
      return 'development'
  }
}

/**
 * Get API base URL with fallbacks
 */
function getApiBaseUrl(): string {
  // Check environment variable first
  const envUrl = process.env.NEXT_PUBLIC_API_URL
  if (envUrl) {
    return envUrl.replace(/\/$/, '') // Remove trailing slash
  }
  
  // Environment-specific defaults
  const env = getEnvironment()
  switch (env) {
    case 'production':
      return 'https://api.wolfalert.app'
    case 'staging':
      return 'https://staging-api.wolfalert.app'
    case 'development':
    default:
      return 'https://api-dev.wolfalert.app'
  }
}

/**
 * Validate required environment variables
 */
function validateEnvironment(): void {
  const required: string[] = [
    // Add any required environment variables here
    // 'NEXT_PUBLIC_API_URL', // Optional with fallback
  ]
  
  const missing = required.filter(key => !process.env[key])
  
  if (missing.length > 0) {
    console.error('❌ Missing required environment variables:', missing)
    // In development, warn but don't crash
    if (getEnvironment() === 'production') {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`)
    }
  }
}

/**
 * Create and export configuration
 */
function createConfig(): AppConfig {
  // Validate environment on startup
  validateEnvironment()
  
  const env = getEnvironment()
  
  return {
    // Environment
    env,
    isDev: env === 'development',
    isProd: env === 'production',
    
    // API Configuration
    api: {
      baseUrl: getApiBaseUrl(),
      timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000', 10),
    },
    
    // Feature flags
    features: {
      enableMockData: env === 'development',
      enableDebugLogs: env !== 'production',
      enableAnalytics: env === 'production',
    },
    
    // UI Configuration
    ui: {
      defaultTheme: 'dark', // WolfAlert uses dark theme
      animationsEnabled: true,
    },
  }
}

// Export singleton configuration
export const config = createConfig()

// Export individual sections for convenience
export const { env, isDev, isProd } = config
export const { api, features, ui } = config

/**
 * Debug function to log configuration (development only)
 */
export function logConfig(): void {
  if (features.enableDebugLogs) {
    console.log('🔧 WolfAlert Configuration:', {
      environment: env,
      apiBaseUrl: api.baseUrl,
      features,
    })
  }
}

/**
 * Utility to check if a feature is enabled
 */
export function isFeatureEnabled(feature: keyof typeof features): boolean {
  return features[feature]
}
