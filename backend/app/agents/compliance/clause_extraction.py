
from app.agents.state import ContractState
from app.llms import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)

class ClauseExtractorAgent:
    async def process(self, state: ContractState):
        logger.info("ClauseExtractorAgent: Extracting clauses")
        
        provider = state.metadata.get("provider", "google")
        llm = get_llm_client(provider=provider, use_fast=True)
        prompt = f"""
        Extract ALL legal clauses from the following contract text.
        For each clause, provide:
        1. A concise title/heading.
        2. The exact text of the clause.
        3. The type of clause (e.g., Liability, Termination, Payment, etc.).

        Return ONLY a JSON list of objects:
        [
          {{"id": "1", "title": "...", "text": "...", "type": "..."}},
          ...
        ]

        Text:
        {state.raw_text}
        """
        
        try:
            response = await llm.generate(prompt)
            # Basic JSON extraction from response string
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                state.clauses = json.loads(json_match.group(0))
            else:
                # Fallback if LLM fails to provide clean JSON
                state.clauses = [{"id": "1", "text": state.raw_text, "type": "Unclassified"}]
        except Exception as e:
            logger.error(f"Clause extraction failed: {e}")
            state.clauses = [{"id": "1", "text": state.raw_text, "type": "Error Fallback"}]

        
        state.add_audit_log("ClauseExtractor", "Extract", f"Extracted {len(state.clauses)} clauses")
