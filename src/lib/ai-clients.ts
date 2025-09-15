import { TaskType } from '@/types/ai';

interface AIResponse {
  data: string | null;
  error: Error | null;
}

/**
 * Gemini (Google Generative) REST client using the official GenerateContent endpoint.
 * This implementation sends the API key in the `x-goog-api-key` header (recommended for browser keys)
 * and uses the `GenerateContentRequest` shape as documented.
 */
export const aiClient = {
  async process(taskType: TaskType, content: string): Promise<AIResponse> {
    try {
      const apiKey = import.meta.env.VITE_GEMINI_API_KEY;

      if (!apiKey) {
        throw new Error('Gemini API key missing in environment variables (VITE_GEMINI_API_KEY)');
      }

      // Strict system instruction to avoid model preambles and force direct output
      const systemInstruction =
        'Respond only with the exact requested content. Do NOT include any leading or trailing commentary, greetings, explanations, or meta-text such as "Okay, here is", "Sure", or "As requested". Do not add any extra prose outside the required output. Output must be valid Markdown or plain text as requested.';

      const prompts: Record<TaskType, string> = {
        'case-summary': 'You are a helpful legal assistant. Provide a concise legal case summary in Markdown. Keep it structured with headings, bullet points and a short conclusion.',
        'loophole-detection': 'You are a legal auditor. Analyze the provided legal document for potential loopholes and present findings as Markdown with headings and numbered issues.',
        'clause-classification': 'You are a clause classifier. Return a Markdown list grouping clauses by their classification with brief notes.',
        'contract-drafting': 'You are a contract drafter. Draft a professional contract in Markdown. Include sections, definitions, obligations, and signature placeholders.',
        'compliance-check': 'You are a compliance officer. Review the provided legal document for regulatory compliance issues. Return a detailed Markdown report with: 1) Executive Summary, 2) Compliance Findings (organized by regulation/standard), 3) Risk Level for each finding (High/Medium/Low), 4) Recommended Actions. Format with clear headings and bullet points.'
      };

      // Compose prompt: system instruction + task-specific prompt + user content (truncate input safely)
      const userPrompt = `${systemInstruction}\n\n${prompts[taskType]}\n\n${content.substring(0, 12000)}`;

      const model = import.meta.env.VITE_GEMINI_MODEL || 'gemini-2.5-flash';
      const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

      // Build GenerateContentRequest per docs: contents is an array of Content objects.
      const payload = {
        // single-turn: one content entry with a text part
        contents: [
          {
            parts: [
              { text: userPrompt }
            ]
          }
        ],
        // Provide a generationConfig that asks for plain text and reasonable length
        generationConfig: {
          // allow more tokens to avoid truncated outputs
          maxOutputTokens: 4096,
          temperature: 0.3,
          // request plain text output; we expect markdown in the text
          responseMimeType: 'text/plain'
        }
      };

      console.debug('[aiClient] Sending GenerateContent request to', endpoint, { payload });

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        // Use the header recommended by docs for API keys in browser contexts
        'x-goog-api-key': String(apiKey)
      };

      const res = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      });

      const json = await res.json();
      console.debug('[aiClient] GenerateContent response', res.status, json);

      if (!res.ok) {
        const msg = json?.error?.message || JSON.stringify(json) || `Gemini request failed with status ${res.status}`;
        throw new Error(msg);
      }

      // Parse the GenerateContentResponse
      // Response has `candidates[]` and each candidate has `content.parts[].text` per docs.
      const candidates = json?.candidates;
      let textResult: string | null = null;

      if (Array.isArray(candidates) && candidates.length > 0) {
        const candidate = candidates[0];
        const parts = candidate?.content?.parts;
        if (Array.isArray(parts) && parts.length > 0) {
          // join all part texts
          textResult = parts.map((p: any) => p?.text ?? '').join('');
        }
      }

      // fallback: some SDK examples return `response.text` — check for that
      textResult = textResult ?? json?.text ?? json?.response?.text ?? null;

      if (!textResult) {
        // as a last resort, stringify the main candidate or entire response
        textResult = JSON.stringify(json);
      }

  // Return raw string (do not trim) to avoid removing significant whitespace or content
  return { data: String(textResult), error: null };
    } catch (error) {
      console.error('AI Processing Error:', error);
      return { data: null, error: error instanceof Error ? error : new Error('Processing failed') };
    }
  }
};