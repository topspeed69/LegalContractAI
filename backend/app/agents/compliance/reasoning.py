
from app.agents.state import ContractState
from app.llms import get_llm_client
import logging

import json

logger = logging.getLogger(__name__)

class ComplianceReasoningAgent:
    async def process(self, state: ContractState, status_queue = None):
        logger.info("ComplianceReasoningAgent: Analyzing compliance")
        
        provider = state.metadata.get("provider", "google")
        llm = get_llm_client(provider=provider)
        
        import asyncio
        semaphore = asyncio.Semaphore(5)  # Limit concurrency to avoid aggressive rate limits
        findings = {}
        total_clauses = len(state.clauses)

        async def analyze_clause(clause, index):
            async with semaphore:
                if status_queue:
                    await status_queue.put({
                        "event": "status", 
                        "data": {
                            "stage": "Reasoning", 
                            "agent": "ComplianceReasoning", 
                            "message": f"Analyzing clause {index+1}/{total_clauses}: {clause.get('title', 'Unknown')}"
                        }
                    })

                if state.retrieved_statutes:
                    statutes_text = "\n".join([f"- {s.get('source')} (Section {s.get('section')}): {s.get('text')}" for s in state.retrieved_statutes])
                    guidance_text = f"Relevant Statutes:\n{statutes_text}"
                else:
                    guidance_text = f"No specific statutes retrieved. Analyze based on general legal principles for contracts in {state.jurisdiction.get('country', 'India')}."

                prompt = f"""
                Analyze the following legal clause for compliance against the provided statutes and common legal standards in {state.jurisdiction.get('country', 'India')}.

                Clause Title: {clause.get('title')}
                Clause Text: {clause.get('text')}

                {guidance_text}

                Determine:
                1. Status: 'compliant', 'violation', or 'warning'.
                2. Risk Level: 'low', 'medium', or 'high'.
                3. Reason: Why it is or isn't compliance.
                4. Suggested Fix: How to make it compliant if it's not.

                Return ONLY a JSON object:
                {{
                    "status": "...",
                    "risk_level": "...",
                    "reason": "...",
                    "suggested_fix": "..."
                }}
                """
                
                try:
                    response = await llm.generate(prompt)
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        findings[clause['id']] = json.loads(json_match.group(0))
                    else:
                        findings[clause['id']] = {
                            "status": "warning",
                            "risk_level": "medium",
                            "reason": "LLM failed to parse analysis for this clause.",
                            "suggested_fix": "Review manually."
                        }
                except Exception as e:
                    logger.error(f"Reasoning failed for clause {clause['id']}: {e}")
                    findings[clause['id']] = {
                        "status": "error",
                        "risk_level": "high",
                        "reason": f"Analysis error: {str(e)}",
                        "suggested_fix": "Contact support."
                    }

        # Fire all tasks in parallel
        tasks = [analyze_clause(clause, i) for i, clause in enumerate(state.clauses)]
        await asyncio.gather(*tasks)
            
        state.compliance_findings = findings
        state.add_audit_log("ComplianceReasoning", "Analyze", f"Analyzed {len(state.clauses)} clauses with LLM reasoning (parallelized)")
