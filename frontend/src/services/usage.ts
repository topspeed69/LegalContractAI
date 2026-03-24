import { supabase } from '@/lib/supabase';
import { ServiceType, TaskType } from '@/types/ai';

const taskToServiceType: Record<TaskType, ServiceType> = {
  'contract-drafting': 'contract_draft',
  'compliance-check': 'compliance_check',
  'case-summary': 'case_summary',
  'loophole-detection': 'loophole_detection',
  'clause-classification': 'clause_classification',
  'legal-research': 'legal_research',
  'chat-assistant': 'chat_assistant'
};

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export interface UsageHistoryItem {
  id: string;
  user_id: string;
  service_type: ServiceType;
  created_at: string;
  prompt_title: string | null;
  prompt_output?: string | null;
}

export async function recordUsage(
  userId: string,
  taskType: TaskType,
  promptTitle?: string,
  promptOutput?: string
): Promise<void> {
  const serviceType = taskToServiceType[taskType];

  try {
    // 1. Record in history via backend (which handles encryption)
    const response = await fetch(`${API_BASE_URL}/api/usage/record`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        service_type: serviceType,
        prompt_title: promptTitle || null,
        prompt_output: promptOutput || null
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to record usage via backend: ${response.statusText}`);
    }

    // 2. Decrement logic removed - managed by AIForm.tsx to avoid double counting
  } catch (err) {
    console.error('Failed to record usage:', err);
    throw err;
  }
}

export interface CreditInfo {
  used: number;
  total: number;
  remaining: number;
}

export async function getUserCredits(userId: string): Promise<CreditInfo> {
  try {
    const defaultTotal = parseInt(import.meta.env.VITE_DEFAULT_CREDITS || '5');

    // Get the user's credits from user_credits table
    const { data: creditData, error: creditError } = await supabase
      .from('user_credits')
      .select('credits_remaining, credits_used_today')
      .eq('user_id', userId)
      .single();

    // If no record exists, they might be a new user, default to env value
    if (creditError && creditError.code !== 'PGRST116') { // PGRST116 is 'no rows'
      throw creditError;
    }

    const remaining = creditData ? creditData.credits_remaining : defaultTotal;
    const used = defaultTotal - remaining;

    return {
      used,
      total: defaultTotal,
      remaining
    };
  } catch (err) {
    console.error('Failed to get user credits:', err);
    return {
      used: 0,
      total: 5,
      remaining: 5
    };
  }
}

export async function getRecentActivity(userId: string, limit: number = 5): Promise<UsageHistoryItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/usage/history?user_id=${userId}`);
    if (!response.ok) throw new Error("Failed to fetch history");
    const data = await response.json();
    return (data.history || []).slice(0, limit);
  } catch (err) {
    console.error('Failed to fetch recent activity:', err);
    throw err;
  }
}

/**
 * Fetch full activity details (including heavy output) for a specific item
 */
export async function getActivityDetail(activityId: string): Promise<UsageHistoryItem | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/usage/history/${activityId}`);
    if (!response.ok) throw new Error("Failed to fetch activity detail");
    return await response.json();
  } catch (err) {
    console.error('Failed to fetch activity detail:', err);
    throw err;
  }
}
