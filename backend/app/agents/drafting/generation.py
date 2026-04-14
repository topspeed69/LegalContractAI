
from app.agents.state import ContractState
from app.llms import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)

class GenerationAgent:
    """Generates contract clauses using the LLM based on state context."""

    async def process(self, state: ContractState):
        logger.info("GenerationAgent: Generating contract clauses via LLM")

        llm = get_llm_client()

        # Build a rich prompt from everything the previous agents added to state
        contract_type = state.metadata.get("contract_type", "General Agreement")
        jurisdiction = state.metadata.get("jurisdiction", "United States")
        parties = state.metadata.get("parties", [])
        detected_intent = state.metadata.get("detected_intent", contract_type)
        selected_template = state.metadata.get("selected_template", "Standard")
        policy_warnings = state.metadata.get("policy_warnings", [])

        parties_text = "\n".join([f"- {p}" for p in parties]) if parties else "- Party A\n- Party B"
        warnings_text = "\n".join([f"⚠ {w}" for w in policy_warnings]) if policy_warnings else "None"

        # Try to fetch relevant clauses/examples from RAG
        rag_context = ""
        try:
            from app.RAG.pinecone_store import pinecone_service
            from app.config import INDEX_STATUTES # Using statutes index for now, ideally should be a contracts index
            
            # Simple query to find relevant legal text
            # Simple query to find relevant legal text
            query = f"{contract_type} {detected_intent} {jurisdiction}"
            docs = pinecone_service.search(INDEX_STATUTES, query, k=3)
            
            if docs:
                examples = "\n\n".join([f"--- Example Clause ---\n{d.page_content}" for d in docs])
                rag_context = f"\n\nHere are some relevant legal text examples from {jurisdiction} to consider:\n{examples}\n"
                logger.info(f"GenerationAgent: Injected {len(docs)} RAG documents into prompt")
        except Exception as e:
            logger.warning(f"GenerationAgent: RAG retrieval failed, proceeding without context: {e}")
            rag_context = ""

        system_prompt = f"""You are an expert legal contract drafter. Generate a complete, professional legal contract.

RULES:
1. Output ONLY the contract text in well-structured Markdown format.
2. Do NOT include any preamble like "Here is the contract" or "I've drafted".
3. Do NOT include any commentary or explanations outside the contract.
4. Use clear headings (##), numbered clauses (1., 1.1, etc.), and proper legal language.
5. Include standard legal boilerplate appropriate for the jurisdiction.
6. The contract must be comprehensive and ready for legal review.
7. Include signature blocks at the end.

{rag_context}"""

        user_prompt = f"""Draft a {detected_intent} contract with the following details:

**Contract Type:** {contract_type}

**Parties:**
{parties_text}

**Jurisdiction:** {jurisdiction}

**Selected Template Style:** {selected_template}

**User Requirements:**
{state.raw_text}

**Policy Warnings to Address:**
{warnings_text}

Generate a complete, professional legal agreement covering:
- Definitions and Interpretation
- Scope of Work / Subject Matter
- Term and Duration
- Payment Terms (if applicable)
- Representations and Warranties
- Confidentiality
- Intellectual Property (if applicable)
- Indemnification and Liability
- Termination
- Dispute Resolution
- Governing Law ({jurisdiction})
- General Provisions (Force Majeure, Amendments, Notices, Severability, Entire Agreement)
- Signature Blocks

Customize all clauses specifically for {jurisdiction} law and {detected_intent} context.
Output ONLY the final contract in Markdown. No explanations."""

        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            generated_text = await llm.generate(full_prompt, temperature=0.3, max_tokens=6000)

            # Parse the generated text into clause objects
            # Split by major headings (##) to create structured clauses
            clauses = []
            sections = generated_text.split("\n## ")

            for i, section in enumerate(sections):
                section = section.strip()
                if not section:
                    continue

                # First section won't have ## prefix stripped
                if i == 0 and not section.startswith("#"):
                    # This is likely a preamble or title
                    clauses.append({
                        "title": "Preamble",
                        "text": section,
                        "type": "llm_generated"
                    })
                else:
                    # Extract title from first line
                    lines = section.split("\n", 1)
                    title = lines[0].strip().lstrip("# ").strip()
                    text = f"## {section}" if i > 0 else section
                    clauses.append({
                        "title": title,
                        "text": text,
                        "type": "llm_generated"
                    })

            # If parsing produced nothing useful, wrap entire text as one clause
            if not clauses:
                clauses = [{
                    "title": "Full Contract",
                    "text": generated_text,
                    "type": "llm_generated"
                }]

            state.drafted_clauses = clauses
            state.add_audit_log(
                "Generation", "Generate",
                f"LLM generated {len(clauses)} clauses ({len(generated_text)} chars)"
            )
            logger.info(f"GenerationAgent: LLM produced {len(clauses)} clauses, {len(generated_text)} chars")

        except Exception as e:
            logger.error(f"GenerationAgent LLM call failed: {e}", exc_info=True)
            # Provide a meaningful error instead of silent failure
            state.drafted_clauses = [{
                "title": "Error",
                "text": f"Contract generation failed: {str(e)}. Please try again.",
                "type": "error"
            }]
            state.add_audit_log("Generation", "Error", f"LLM generation failed: {str(e)}")
