import { supabase } from '@/lib/supabase';
import { ServiceType, TaskType } from '@/types/ai';

// Map AI task types to service types for database storage
const taskToServiceType: Record<TaskType, ServiceType> = {
  'contract-drafting': 'contract_draft',
  'compliance-check': 'compliance_check',
  // These will be logged as contract_draft for now since they're contract-related
  'case-summary': 'contract_draft',
  'loophole-detection': 'contract_draft',
  'clause-classification': 'contract_draft'
};

export interface UsageHistoryItem {
  id: string;
  user_id: string;
  service_type: ServiceType;
  created_at: string;
  prompt_title: string | null;
  prompt_output: string | null;
}

export async function recordUsage(
  userId: string, 
  taskType: TaskType, 
  promptTitle?: string, 
  promptOutput?: string
): Promise<void> {
  const serviceType = taskToServiceType[taskType];
  
  try {
    const { error } = await supabase
      .from('usage_history')
      .insert({
        user_id: userId,
        service_type: serviceType,
        prompt_title: promptTitle || null,
        prompt_output: promptOutput || null
      });

    if (error) {
      console.error('Error recording usage:', error);
      throw error;
    }
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
    // Get the user's total allocated credits
    const { data: userData, error: userError } = await supabase
      .from('users')
      .select('total_credits')
      .eq('id', userId)
      .single();

    if (userError) throw userError;

    // Get count of usage history entries
    const { count: usedCredits, error: usageError } = await supabase
      .from('usage_history')
      .select('id', { count: 'exact' })
      .eq('user_id', userId);

    if (usageError) throw usageError;

    const totalCredits = userData?.total_credits || 1000; // Default to 1000 if not set
    const used = usedCredits || 0;
    
    return {
      used,
      total: totalCredits,
      remaining: totalCredits - used
    };
  } catch (err) {
    console.error('Failed to get user credits:', err);
    throw err;
  }
}

export async function getRecentActivity(userId: string, limit: number = 5): Promise<UsageHistoryItem[]> {
  try {
    const { data, error } = await supabase
      .from('usage_history')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching recent activity:', error);
      throw error;
    }

    return data || [];
  } catch (err) {
    console.error('Failed to fetch recent activity:', err);
    throw err;
  }
}
