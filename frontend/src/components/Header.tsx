'use client'

import { useState } from 'react'
import { UserProfile } from '@/types'
import { ChevronDown, Plus, FileText } from 'lucide-react'

interface HeaderProps {
  currentProfile: UserProfile
  profiles?: UserProfile[]
  onProfileSelect?: (profile: UserProfile) => void
  onAddProfile?: () => void
  onGenerateReport?: () => void
}

const Header = ({ 
  currentProfile, 
  profiles = [currentProfile],
  onProfileSelect,
  onAddProfile,
  onGenerateReport 
}: HeaderProps) => {
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false)

  const formatProfileDisplay = (profile: UserProfile) => {
    const departmentMap: Record<string, string> = {
      marketing: 'Marketing',
      engineering: 'Engineering',
      sales: 'Sales',
      executive: 'Executive',
      it: 'IT',
      operations: 'Operations',
      customer_service: 'Customer Service'
    }
    
    const industryMap: Record<string, string> = {
      technology: 'Technology',
      electric: 'Electric Utilities',
      broadband: 'Broadband',
      municipal: 'Municipal',
      financial: 'Financial',
      healthcare: 'Healthcare'
    }
    
    const roleMap: Record<string, string> = {
      individual: 'Individual',
      manager: 'Manager',
      director: 'Director',
      executive: 'Executive',
      c_level: 'C-Level'
    }

    return `${departmentMap[profile.department]} • ${industryMap[profile.industry]} • ${roleMap[profile.role_level]}`
  }

  const handleProfileSelect = (profile: UserProfile) => {
    onProfileSelect?.(profile)
    setIsProfileDropdownOpen(false)
  }

  return (
    <header className="glass-morphism border-b border-white/10 sticky top-0 z-50">
      <div className="container-wolf py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-r from-wolf-accent to-purple-600 rounded-lg flex items-center justify-center animate-glow">
                <span className="text-xl font-bold">🐺</span>
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gradient">WolfAlert</h1>
              <p className="text-xs text-gray-400">AI Intelligence Dashboard</p>
            </div>
          </div>
          
          {/* Profile Selector & Actions */}
          <div className="flex items-center space-x-4">
            {/* Profile Selector */}
            <div className="relative">
              <button
                onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                className="glass-morphism px-4 py-2 rounded-lg text-sm bg-transparent border-0 focus:ring-2 focus:ring-wolf-accent flex items-center space-x-2 hover:bg-white/10 transition-all duration-200"
                aria-expanded={isProfileDropdownOpen}
                aria-haspopup="true"
              >
                <span className="text-white">{formatProfileDisplay(currentProfile)}</span>
                <ChevronDown 
                  className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
                    isProfileDropdownOpen ? 'rotate-180' : ''
                  }`} 
                />
              </button>
              
              {/* Dropdown Menu */}
              {isProfileDropdownOpen && (
                <div className="absolute right-0 mt-2 w-72 glass-morphism rounded-lg shadow-xl border border-white/20 py-2 z-50">
                  {profiles.map((profile) => (
                    <button
                      key={profile.id}
                      onClick={() => handleProfileSelect(profile)}
                      className={`w-full text-left px-4 py-3 text-sm hover:bg-white/10 transition-colors duration-200 ${
                        profile.id === currentProfile.id ? 'bg-white/5 text-wolf-accent' : 'text-white'
                      }`}
                    >
                      <div className="font-medium">{profile.profile_name}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {formatProfileDisplay(profile)}
                      </div>
                    </button>
                  ))}
                  
                  {/* Add Profile Option */}
                  <div className="border-t border-white/10 mt-2 pt-2">
                    <button
                      onClick={() => {
                        onAddProfile?.()
                        setIsProfileDropdownOpen(false)
                      }}
                      className="w-full text-left px-4 py-3 text-sm text-wolf-accent hover:bg-white/10 transition-colors duration-200 flex items-center space-x-2"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Add New Profile</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
            
            {/* Generate Report Button */}
            <button 
              onClick={onGenerateReport}
              className="btn-secondary flex items-center space-x-2"
              title="Generate Intelligence Report"
            >
              <FileText className="w-4 h-4" />
              <span className="hidden sm:inline">Generate Report</span>
            </button>
            
            {/* Add Profile Button */}
            <button 
              onClick={onAddProfile}
              className="btn-primary flex items-center space-x-2"
              title="Add New Profile"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">Add Profile</span>
            </button>
          </div>
        </div>
      </div>
      
      {/* Click outside to close dropdown */}
      {isProfileDropdownOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsProfileDropdownOpen(false)}
          aria-hidden="true"
        />
      )}
    </header>
  )
}

export default Header