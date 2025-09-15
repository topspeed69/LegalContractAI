export type TaskType = 'case-summary' | 'loophole-detection' | 'clause-classification' | 'contract-drafting' | 'compliance-check';

export type ServiceType = 'contract_draft' | 'compliance_check';

export interface AIFormProps {
  title: string;
  description: string;
  placeholder?: string;
  taskType: TaskType;
  additionalFields?: React.ReactNode;
}