
export interface APIResponse {
  success: boolean;
  data?: string;
  error?: string;
}

export interface AIFormProps {
  title: string;
  description: string;
  placeholder?: string;
  taskType: "case-summary" | "clause-classification" | "loophole-detection" | "contract-drafting";
  additionalFields?: React.ReactNode;
}

export interface UsageHistoryItem {
  id: string;
  user_id: string;
  service_type: 'contract_draft' | 'compliance_check';
  created_at: string;
  prompt_title: string | null;
  prompt_output: string | null;
}
