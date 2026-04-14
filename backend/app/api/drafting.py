"""
Contract Drafting API Endpoint
Uses: ingestion_agent + LLM (no other agents)
"""

import logging
from fastapi import APIRouter, HTTPException, Response, status
from app.schemas import ContractDraftRequest
from app.services.draft_service import generate_draft

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/drafting",
    tags=["Contract Drafting"]
)


from fastapi.responses import StreamingResponse
from app.utils.sse import sse_generator
import asyncio
import json

@router.post(
    "/draft",
    summary="Draft a new contract",
    description="Generate a professional contract using Agentic Drafting Orchestrator"
)
async def draft_contract(request: ContractDraftRequest):
    """Draft a new contract using streaming status updates."""
    try:
        logger.info("Starting agentic contract drafting request with streaming")

        # Map ContractDraftRequest to metadata
        data = request.model_dump()
        
        parties = []
        if data.get("parties"):
            for p in data.get("parties"):
                name = p.get("name") if isinstance(p, dict) else getattr(p, "name", None)
                if name: parties.append(name)
        else:
            if data.get("party_a"): parties.append(data.get("party_a"))
            if data.get("party_b"): parties.append(data.get("party_b"))

        requirements_text = data.get("requirements", "")
        if data.get("key_terms"):
             requirements_text += f"\n\nKey Terms:\n{data.get('key_terms')}"
        if data.get("purpose"):
             requirements_text += f"\n\nPurpose:\n{data.get('purpose')}"

        metadata = {
            "contract_type": data.get("contract_type") or data.get("purpose") or "General",
            "jurisdiction": data.get("jurisdiction") or "",
            "parties": parties,
            "term": data.get("term") or ""
        }

        async def run_pipeline():
            status_queue = asyncio.Queue()
            
            async def pipeline_worker():
                from app.agents.drafting import DraftingOrchestrator
                orchestrator = DraftingOrchestrator()
                final_state = await orchestrator.run(
                    raw_requirements=requirements_text, 
                    metadata=metadata,
                    provider=data.get("provider"),
                    status_queue=status_queue
                )
                # Send the final result
                await status_queue.put({"event": "result", "data": final_state.final_contract})
                await status_queue.put(None) # Termination signal

            # Start worker in background
            asyncio.create_task(pipeline_worker())
            
            # Yield events from queue
            async for event in sse_generator(status_queue):
                yield event

        return StreamingResponse(run_pipeline(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error in agentic draft_contract: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
