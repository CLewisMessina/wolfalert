// src/utils/api.ts
/**
 * API Client for WolfAlert Backend
 * Single Responsibility: Handle all HTTP communication with the FastAPI backend
 * 
 * This file manages:
 * - API base configuration
 * - HTTP request/response handling
 * - Error handling and status codes
 * - Type-safe API calls
 */

import { UserProfile, CreateProfileRequest, ApiResponse } from '@/types'

// API Configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api-dev.wolfalert.app'
const API_TIMEOUT = 10000 // 10 seconds

/**
 * Custom API Error class for better error handling
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Generic API request handler with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  
  // Default headers
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  // Request configuration
  const config: RequestInit = {
    ...options,
    headers: defaultHeaders,
    // Add timeout using AbortController
    signal: AbortSignal.timeout(API_TIMEOUT),
  }

  try {
    console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`)
    
    const response = await fetch(url, config)
    
    // Handle non-JSON responses (like health checks)
    const contentType = response.headers.get('content-type')
    const isJsonResponse = contentType?.includes('application/json') ?? false
    
    let data: any
    if (isJsonResponse) {
      data = await response.json()
    } else {
      data = await response.text()
    }

    // Success response
    if (response.ok) {
      console.log(`✅ API Success: ${response.status}`, data)
      return data
    }

    // Error response
    console.error(`❌ API Error: ${response.status}`, data)
    throw new ApiError(
      data?.detail || data?.message || `HTTP ${response.status}`,
      response.status,
      data
    )

  } catch (error) {
    // Network or timeout errors
    if (error instanceof ApiError) {
      throw error
    }
    
    console.error('🚫 Network Error:', error)
    throw new ApiError(
      'Network error - please check your connection',
      0,
      error
    )
  }
}

/**
 * Profile API operations
 * Each function has a single responsibility for one API operation
 */
export const profileApi = {
  /**
   * Get all profiles for the current session
   */
  async getProfiles(sessionId?: string): Promise<UserProfile[]> {
    const params = new URLSearchParams()
    if (sessionId) {
      params.append('session_id', sessionId)
    }
    params.append('active_only', 'true')
    
    const query = params.toString()
    const endpoint = `/api/profiles${query ? `?${query}` : ''}`
    
    return apiRequest<UserProfile[]>(endpoint, {
      method: 'GET',
    })
  },

  /**
   * Get a specific profile by ID
   */
  async getProfile(profileId: string): Promise<UserProfile> {
    return apiRequest<UserProfile>(`/api/profiles/${profileId}`, {
      method: 'GET',
    })
  },

  /**
   * Create a new profile
   */
  async createProfile(
    profileData: CreateProfileRequest,
    sessionId?: string
  ): Promise<UserProfile> {
    const params = new URLSearchParams()
    if (sessionId) {
      params.append('session_id', sessionId)
    }
    
    const query = params.toString()
    const endpoint = `/api/profiles${query ? `?${query}` : ''}`
    
    return apiRequest<UserProfile>(endpoint, {
      method: 'POST',
      body: JSON.stringify(profileData),
    })
  },

  /**
   * Update an existing profile
   */
  async updateProfile(
    profileId: string,
    updates: Partial<Pick<UserProfile, 'profile_name' | 'is_active'>>
  ): Promise<UserProfile> {
    return apiRequest<UserProfile>(`/api/profiles/${profileId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    })
  },

  /**
   * Soft delete a profile (set is_active = false)
   */
  async deleteProfile(profileId: string): Promise<void> {
    return apiRequest<void>(`/api/profiles/${profileId}`, {
      method: 'DELETE',
    })
  },

  /**
   * Get profile hash for AI analysis caching
   */
  async getProfileHash(profileId: string): Promise<{
    profile_id: number
    profile_hash: string
    industry: string
    department: string
    role_level: string
  }> {
    return apiRequest(`/api/profiles/${profileId}/hash`, {
      method: 'GET',
    })
  },
}

/**
 * Health check operations
 */
export const healthApi = {
  /**
   * Check overall service health
   */
  async checkHealth(): Promise<{
    status: string
    service: string
    database: string
    version: string
  }> {
    return apiRequest('/health', {
      method: 'GET',
    })
  },

  /**
   * Test database connectivity
   */
  async testDatabase(): Promise<{
    database: string
    test_query: string
    tables_found: string[]
    tables_expected: string[]
  }> {
    return apiRequest('/api/test-db', {
      method: 'GET',
    })
  },
}

/**
 * Utility function to check if API is available
 */
export async function checkApiConnection(): Promise<boolean> {
  try {
    await healthApi.checkHealth()
    return true
  } catch (error) {
    console.error('API connection failed:', error)
    return false
  }
}

/**
 * Get API base URL for debugging
 */
export function getApiBaseUrl(): string {
  return API_BASE
}
