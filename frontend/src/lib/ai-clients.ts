import { TaskType } from '@/types/ai';
import { supabase } from './supabase';

interface AIResponse {
  data: string | null;
  error: Error | null;
  metadata?: Record<string, any> | null;
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

type RouteConfig = {
  path: string;
  expects: 'text' | 'json';
  buildPayload: (content: string, options?: Record<string, any>) => Record<string, any>;
  transform: (payload: any) => { result: string; metadata?: Record<string, any> | null };
};

const defaultReportRoute = (taskType: TaskType): RouteConfig => ({
  path: '/api/reports/generate',
  expects: 'json',
  buildPayload: (content, options) => ({ task_type: taskType, content, ...options }),
  transform: (payload) => ({ result: payload.report_markdown, metadata: payload })
});

const ROUTES: Record<TaskType, RouteConfig> = {
  'contract-drafting': {
    path: '/api/drafting/draft',
    expects: 'text',
    buildPayload: (content, options) => ({
      requirements: content,
      purpose: options?.contractType || 'Contract generated via UI',
      jurisdiction: options?.jurisdiction || 'United States',
      key_terms: options?.keyTerms,
      parties: [
        { name: options?.partyA || 'Party A', role: 'Client' },
        { name: options?.partyB || 'Party B', role: 'Counterparty' }
      ]
    }),
    transform: (payload: string) => ({ result: payload, metadata: null })
  },
  'compliance-check': {
    path: '/api/compliance/check',
    expects: 'json',
    buildPayload: (content, options) => ({
      contract_text: content,
      jurisdiction: options?.jurisdiction || 'United States',
      standards: options?.standards || []
    }),
    transform: (payload) => ({
      result: payload.report_markdown || payload.drafted_contract || '',
      metadata: payload
    })
  },
  'case-summary': {
    path: '/api/summarization/summarize-case',
    expects: 'json',
    buildPayload: (content) => ({ case_text: content }),
    transform: (payload) => ({ result: payload.summary, metadata: payload })
  },
  'clause-classification': {
    path: '/api/analysis/analyze-clauses',
    expects: 'json',
    buildPayload: (content) => ({ text: content }),
    transform: (payload) => {
      // Handle potential raw string response (fallback)
      if (typeof payload === 'string') {
        return { result: payload, metadata: null };
      }

      // Format structured response into Markdown
      const summary = payload.summary || 'Analysis complete.';
      let markdown = `### Executive Summary\n\n${summary}\n\n### Detailed Risk Analysis\n\n`;

      if (payload.risks && Array.isArray(payload.risks) && payload.risks.length > 0) {
        payload.risks.forEach((risk: any, index: number) => {
          const riskIcon = risk.risk_level === 'High' ? '🔴' : risk.risk_level === 'Medium' ? '🟡' : '🟢';

          markdown += `#### ${index + 1}. ${riskIcon} ${risk.risk_level} Risk\n\n`;
          // Format clause text as a blockquote, truncating if extremely long to keep UI clean
          const clauseText = risk.clause_text ? risk.clause_text.trim() : '';
          markdown += `**Clause:**\n> "${clauseText}"\n\n`;

          markdown += `**Analysis:** ${risk.explanation}\n\n`;

          if (risk.recommendation) {
            markdown += `**Recommendation:** ${risk.recommendation}\n\n`;
          }

          markdown += `---\n\n`;
        });
      } else {
        markdown += `_No specific high-risk clauses identified in this document._\n`;
      }

      return {
        result: markdown,
        metadata: payload
      };
    }
  },
  'loophole-detection': {
    path: '/api/reports/generate',
    expects: 'json',
    buildPayload: (content) => ({ task_type: 'loophole-detection', content }),
    transform: (payload) => ({ result: payload.report_markdown, metadata: payload })
  },
  'legal-research': {
    path: '/api/research/legal-research',
    expects: 'json',
    buildPayload: (content, options) => ({ query: content, jurisdiction: options?.jurisdiction || 'India' }),
    transform: (payload) => {
      // Format citations as markdown
      const citations = payload.citations ? payload.citations.map((c: any) => `> **${c.title}** (${c.source})\n> ${c.text}`).join('\n\n') : '';
      return {
        result: `${payload.answer}\n\n### Citations\n${citations}`,
        metadata: payload
      };
    }
  },
  'chat-assistant': {
    path: '/api/chat/chat-assistant',
    expects: 'json',
    buildPayload: (content, options) => ({
      message: content,
      user_id: options?.userId
    }),
    transform: (payload) => ({ result: payload.reply, metadata: payload })
  }
};

export const aiClient = {
  async process(
    taskType: TaskType, 
    content: string, 
    options?: Record<string, any>,
    onStatus?: (stage: string, agent: string) => void
  ): Promise<AIResponse> {
    try {
      const route = ROUTES[taskType] ?? defaultReportRoute(taskType);

      // Fetch provider from session if not explicitly provided
      let provider = options?.provider;
      if (!provider) {
        const { data: { session } } = await supabase.auth.getSession();
        provider = session?.user?.user_metadata?.llm_provider || 'nvidia';
      }

      const payload = {
        ...route.buildPayload(content, options),
        provider
      };

      const response = await fetch(`${API_BASE_URL}${route.path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Backend request failed with status ${response.status}`);
      }

      // Handle Streaming vs Static Response
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('text/event-stream')) {
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let resultData = '';
        
        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const messages = buffer.split('\n\n');
          buffer = messages.pop() || ''; // Keep the last incomplete message in the buffer

          for (const message of messages) {
            if (!message.trim()) continue;
            
            const lines = message.split('\n');
            let eventType = 'message';
            let dataRaw = '';
            
            for (const line of lines) {
              if (line.startsWith('event: ')) {
                eventType = line.replace('event: ', '').trim();
              } else if (line.startsWith('data: ')) {
                dataRaw = line.replace('data: ', '').trim();
              }
            }

            if (dataRaw) {
              try {
                const data = JSON.parse(dataRaw);
                if (eventType === 'status') {
                  onStatus?.(data.stage, data.agent);
                } else if (eventType === 'result') {
                  resultData = data;
                }
              } catch (e) {
                if (eventType === 'result') resultData = dataRaw;
              }
            }
          }
        }

        const { result, metadata } = route.transform(resultData);
        return { data: result, error: null, metadata: metadata ?? null };
      } else {
        // Fallback for non-streaming routes
        const data = route.expects === 'text' ? await response.text() : await response.json();
        const { result, metadata } = route.transform(data);
        return { data: result, error: null, metadata: metadata ?? null };
      }
    } catch (error) {
      console.error('AI Processing Error:', error);
      return { data: null, error: error instanceof Error ? error : new Error('Processing failed') };
    }
  },

  async getHistory(userId: string): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/history?user_id=${userId}`);
      if (!response.ok) throw new Error("Failed to fetch history");
      return await response.json();
    } catch (error) {
      console.error("History Fetch Error:", error);
      return [];
    }
  }
};
