// Core TypeScript type definitions for WolfAlert
// Single responsibility: Define all shared types and interfaces

// ===== USER PROFILE TYPES =====
export type Industry = 'electric' | 'broadband' | 'municipal' | 'technology' | 'financial' | 'healthcare';

export type Department = 'engineering' | 'marketing' | 'sales' | 'executive' | 'operations' | 'it' | 'customer_service';

export type RoleLevel = 'individual' | 'manager' | 'director' | 'executive' | 'c_level';

export interface UserProfile {
  id: string;
  profile_name: string;
  industry: Industry;
  department: Department;
  role_level: RoleLevel;
  user_session_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateProfileRequest {
  profile_name: string;
  industry: Industry;
  department: Department;
  role_level: RoleLevel;
}

// ===== ARTICLE TYPES =====
export type ImpactType = 'threat' | 'opportunity' | 'watch';

export type SourceReliability = 'high' | 'medium' | 'community';

export interface Article {
  id: string;
  url: string;
  title: string;
  content: string;
  source_name: string;
  source_reliability: SourceReliability;
  published_at: string;
  fetched_at: string;
  expires_at: string;
  is_processed: boolean;
  processing_attempts: number;
}

export interface ArticleInsight {
  id: string;
  article_id: string;
  profile_hash: string;
  summary: string;
  impact_reasoning: string;
  impact_type: ImpactType;
  impact_score: number;
  processing_time_ms: number;
  created_at: string;
}

// ===== DASHBOARD TYPES =====
export interface AlertCard {
  article: Article;
  insight: ArticleInsight;
  time_ago: string;
  is_primary?: boolean;
}

export interface DashboardStats {
  threats: number;
  opportunities: number;
  watch: number;
  total_alerts: number;
}

export interface DashboardData {
  profile: UserProfile;
  stats: DashboardStats;
  primary_alert?: AlertCard;
  secondary_alerts: AlertCard[];
  last_updated: string;
  next_refresh: string;
  source_count: number;
}

// ===== RSS SOURCE TYPES =====
export type SourceType = 'official_blog' | 'community' | 'research' | 'product_releases' | 'news';

export interface RSSSource {
  id: string;
  name: string;
  url: string;
  source_type: SourceType;
  reliability: SourceReliability;
  company?: string;
  industries: Industry[];
  weight: number;
  is_active: boolean;
  last_fetched?: string;
  fetch_frequency_hours: number;
}

// ===== INTERACTION TYPES =====
export type InteractionAction = 'viewed' | 'saved' | 'dismissed' | 'not_relevant' | 'expanded';

export interface UserInteraction {
  id: string;
  profile_id: string;
  article_id: string;
  action: InteractionAction;
  interaction_time: string;
}

export interface TrackInteractionRequest {
  profile_id: string;
  article_id: string;
  action: InteractionAction;
}

// ===== REPORT TYPES =====
export interface Report {
  id: string;
  profile_id: string;
  title: string;
  content: ReportContent;
  generated_at: string;
  expires_at: string;
}

export interface ReportContent {
  included_articles: string[]; // Article IDs
  time_range: {
    start: string;
    end: string;
  };
  alert_types: ImpactType[];
  summary: string;
}

export interface GenerateReportRequest {
  profile_id: string;
  title: string;
  time_range_days: number;
  alert_types: ImpactType[];
}

// ===== API RESPONSE TYPES =====
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

// ===== UI STATE TYPES =====
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}

export interface UIState {
  loading: LoadingState;
  error: ErrorState;
}

// ===== COMPONENT PROP TYPES =====
export interface AlertCardProps {
  alert: AlertCard;
  onSave: (articleId: string) => void;
  onDismiss: (articleId: string) => void;
  onExpand?: (articleId: string) => void;
  className?: string;
}

export interface ProfileSelectorProps {
  profiles: UserProfile[];
  selectedProfile?: UserProfile;
  onProfileSelect: (profile: UserProfile) => void;
  onAddProfile: () => void;
  className?: string;
}

export interface StatsBarProps {
  stats: DashboardStats;
  className?: string;
}

// ===== UTILITY TYPES =====
export type Optional<T, K extends keyof T> = Pick<Partial<T>, K> & Omit<T, K>;

export type WithId<T> = T & { id: string };

export type WithTimestamps<T> = T & {
  created_at: string;
  updated_at: string;
};

// ===== CONFIGURATION TYPES =====
export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
  };
  ai: {
    model: string;
    maxTokens: number;
    temperature: number;
  };
  rss: {
    fetchIntervalHours: number;
    maxArticlesPerSource: number;
  };
  cache: {
    ttlHours: number;
  };
}

// ===== FORM TYPES =====
export interface ProfileFormData {
  profile_name: string;
  industry: Industry;
  department: Department;
  role_level: RoleLevel;
}

export interface ProfileFormErrors {
  profile_name?: string;
  industry?: string;
  department?: string;
  role_level?: string;
}

// ===== CONSTANTS =====
export const INDUSTRIES: { value: Industry; label: string }[] = [
  { value: 'electric', label: 'Electric Utilities' },
  { value: 'broadband', label: 'Broadband/Telecom' },
  { value: 'municipal', label: 'Municipal Services' },
  { value: 'technology', label: 'Technology' },
  { value: 'financial', label: 'Financial Services' },
  { value: 'healthcare', label: 'Healthcare' },
];

export const DEPARTMENTS: { value: Department; label: string }[] = [
  { value: 'executive', label: 'Executive' },
  { value: 'engineering', label: 'Engineering' },
  { value: 'it', label: 'Information Technology' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'sales', label: 'Sales' },
  { value: 'operations', label: 'Operations' },
  { value: 'customer_service', label: 'Customer Service' },
];

export const ROLE_LEVELS: { value: RoleLevel; label: string }[] = [
  { value: 'individual', label: 'Individual Contributor' },
  { value: 'manager', label: 'Manager' },
  { value: 'director', label: 'Director' },
  { value: 'executive', label: 'Executive' },
  { value: 'c_level', label: 'C-Level' },
];

export const IMPACT_TYPES: { value: ImpactType; label: string; color: string }[] = [
  { value: 'threat', label: 'Critical Threat', color: 'text-red-400' },
  { value: 'opportunity', label: 'Opportunity', color: 'text-green-400' },
  { value: 'watch', label: 'Watch', color: 'text-blue-400' },
];