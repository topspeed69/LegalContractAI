from app.agents.state import ContractState
from app.llms import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)

class IntentAnalysisAgent:
    """Analyzes user requirements to extract contract intent and entities using LLM."""

    async def process(self, state: ContractState):
        logger.info("IntentAnalysisAgent: Analyzing requirements via LLM")

        llm = get_llm_client(use_fast=True)

        prompt = f"""Analyze the following contract request and extract structured information.

**User Request:**
{state.raw_text}

**Provided Metadata:**
- Contract Type: {state.metadata.get('contract_type', 'Not specified')}
- Jurisdiction: {state.metadata.get('jurisdiction', 'Not specified')}
- Parties: {state.metadata.get('parties', [])}

Respond in valid JSON only (no markdown fences, no explanation):
{{
  "detected_intent": "<the type of contract being requested, e.g. 'Service Agreement', 'NDA', 'Employment Contract'>",
  "detected_entities": ["<list of key actors/parties/organizations mentioned>"],
  "key_requirements": ["<list of the main requirements extracted from the request>"],
  "suggested_clauses": ["<list of clauses that should be included based on the request>"]
}}"""

        try:
            response = await llm.generate(prompt, temperature=0.1, max_tokens=1000)

            # Try to parse JSON from response
            # Strip markdown code fences if present
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()

            parsed = json.loads(clean)

            state.metadata["detected_intent"] = parsed.get("detected_intent", state.metadata.get("contract_type", "General"))
            state.metadata["detected_entities"] = parsed.get("detected_entities", [])
            state.metadata["key_requirements"] = parsed.get("key_requirements", [])
            state.metadata["suggested_clauses"] = parsed.get("suggested_clauses", [])

            state.add_audit_log(
                "IntentAnalysis", "Analyze",
                f"Detected intent: {state.metadata['detected_intent']}, "
                f"{len(state.metadata['detected_entities'])} entities, "
                f"{len(state.metadata['key_requirements'])} requirements"
            )
            logger.info(f"IntentAnalysisAgent: Detected intent={state.metadata['detected_intent']}")

        except json.JSONDecodeError as je:
            logger.warning(f"IntentAnalysisAgent: Could not parse JSON, using fallback. Error: {je}")
            # Fallback to metadata-based defaults
            state.metadata["detected_intent"] = state.metadata.get("contract_type", "General Agreement")
            state.metadata["detected_entities"] = state.metadata.get("parties", [])
            state.metadata["key_requirements"] = [state.raw_text[:200]]
            state.add_audit_log("IntentAnalysis", "Fallback", "Used metadata-based defaults due to parse error")

        except Exception as e:
            logger.error(f"IntentAnalysisAgent failed: {e}", exc_info=True)
            state.metadata["detected_intent"] = state.metadata.get("contract_type", "General Agreement")
            state.metadata["detected_entities"] = state.metadata.get("parties", [])
            state.add_audit_log("IntentAnalysis", "Error", f"LLM call failed: {str(e)}")
