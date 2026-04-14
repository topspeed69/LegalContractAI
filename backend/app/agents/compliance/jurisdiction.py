
from app.agents.state import ContractState
from app.llms import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)

class JurisdictionResolverAgent:
    async def process(self, state: ContractState):
        logger.info("JurisdictionResolverAgent: Determining jurisdiction")
        
        # Simple heuristic or LLM call
        # If user provided jurisdiction in metadata, use that.
        if state.metadata.get("jurisdiction"):
             state.jurisdiction = {"country": "India", "region": state.metadata.get("jurisdiction")} # normalizing
             state.add_audit_log("JurisdictionResolver", "Check", f"Used metadata: {state.jurisdiction}")
             return

        # Else, use LLM to detect

        provider = state.metadata.get("provider", "google")
        llm = get_llm_client(provider=provider, use_fast=True)
        prompt = f"""
        Analyze the following contract text and identify the governing law and jurisdiction (Country and State/Region).
        
        Return ONLY a JSON object:
        {{
            "country": "...",
            "region": "..."
        }}
        
        Text:
        {state.raw_text[:3000]}
        """
        
        try:
             response = await llm.generate(prompt)
             import re
             json_match = re.search(r'\{.*\}', response, re.DOTALL)
             if json_match:
                 state.jurisdiction = json.loads(json_match.group(0))
             else:
                 state.jurisdiction = {"country": "India", "region": "Unknown"}
             state.add_audit_log("JurisdictionResolver", "Inference", f"Detected: {state.jurisdiction}")
        except Exception as e:
             logger.error(f"Jurisdiction detection failed: {e}")
             state.jurisdiction = {"country": "India", "error": str(e)}
