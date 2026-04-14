from app.agents.state import ContractState
from app.llms import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)

class PolicyCheckAgent:
    """Validates contract requests against policy guidelines using LLM."""

    async def process(self, state: ContractState):
        logger.info("PolicyCheckAgent: Checking policies via LLM")

        llm = get_llm_client(use_fast=True)

        prompt = f"""You are a legal policy compliance reviewer. Analyze the following contract drafting request for any policy violations or risks.

**User Request:**
{state.raw_text}

**Detected Intent:** {state.metadata.get('detected_intent', 'Unknown')}
**Jurisdiction:** {state.metadata.get('jurisdiction', 'Not specified')}

Check for:
1. Requests for illegal or unenforceable contract terms
2. Potentially unethical clauses
3. Terms that may violate public policy in the given jurisdiction
4. Missing critical protective clauses
5. Any red flags that should be addressed

Respond in valid JSON only (no markdown fences, no explanation):
{{
  "allowed": true/false,
  "policy_warnings": ["<list of warnings or concerns, empty if none>"],
  "suggestions": ["<list of suggested additions or modifications>"],
  "block_reason": "<reason if blocked, null if allowed>"
}}"""

        try:
            response = await llm.generate(prompt, temperature=0.1, max_tokens=1000)

            # Strip markdown code fences if present
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()

            parsed = json.loads(clean)

            allowed = parsed.get("allowed", True)
            warnings = parsed.get("policy_warnings", [])
            suggestions = parsed.get("suggestions", [])

            state.metadata["policy_warnings"] = warnings
            state.metadata["policy_suggestions"] = suggestions

            if not allowed:
                block_reason = parsed.get("block_reason", "Policy violation detected")
                state.metadata["policy_block"] = block_reason
                state.add_audit_log("PolicyCheck", "Block", f"Blocked: {block_reason}")
                logger.warning(f"PolicyCheckAgent: Request blocked — {block_reason}")
            else:
                state.add_audit_log(
                    "PolicyCheck", "Pass",
                    f"Policy check passed with {len(warnings)} warning(s)"
                )
                logger.info(f"PolicyCheckAgent: Passed with {len(warnings)} warnings")

        except json.JSONDecodeError:
            logger.warning("PolicyCheckAgent: Could not parse LLM response, allowing by default")
            state.metadata["policy_warnings"] = []
            state.add_audit_log("PolicyCheck", "Fallback", "Parse error, allowed by default")

        except Exception as e:
            logger.error(f"PolicyCheckAgent failed: {e}", exc_info=True)
            state.metadata["policy_warnings"] = []
            state.add_audit_log("PolicyCheck", "Error", f"LLM call failed: {str(e)}, allowed by default")
