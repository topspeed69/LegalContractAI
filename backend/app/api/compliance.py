"""
Compliance Check API Endpoint
SYSTEM 2: Uses compliance_service with multi-agent pipeline
"""

import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas import ComplianceCheckRequest, ComplianceCheckResponse, ComplianceIssue, ErrorResponse
from app.services.compliance_service import check_compliance as run_compliance_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/compliance",
    tags=["Compliance Check"]
)


from fastapi.responses import StreamingResponse
from app.utils.sse import sse_generator
import asyncio
import json

@router.post(
    "/check",
    response_class=StreamingResponse,
    summary="Check contract compliance",
    description="Analyze contract for compliance issues using multi-agent pipeline with streaming status"
)
async def check_compliance_endpoint(request: ComplianceCheckRequest):
    """Check contract compliance using streaming status updates."""
    try:
        logger.info("Starting compliance check request with streaming")
        
        contract_text = request.contract_text
        jurisdiction = request.jurisdiction or "United States"
        
        if len(contract_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Contract text too short")
        
        async def run_pipeline():
            status_queue = asyncio.Queue()
            
            async def pipeline_worker():
                from app.agents.compliance import ComplianceOrchestrator
                orchestrator = ComplianceOrchestrator()
                
                metadata = {
                    "jurisdiction": jurisdiction,
                    "request_source": "api",
                    "provider": request.provider or "nvidia"
                }
                
                final_state = await orchestrator.run(raw_text=contract_text, metadata=metadata, status_queue=status_queue)
                
                # Build the mapping response part (similar to previous implementation)
                compliance_report = []
                for clause_id, finding in final_state.compliance_findings.items():
                    clause_text = next((c["text"] for c in final_state.clauses if c["id"] == clause_id), "")
                    compliance_report.append({
                        "clause": clause_text,
                        "heading": f"Clause {clause_id}",
                        "risk_level": finding.get("risk_level", "low").lower(),
                        "fix": finding.get("suggested_fix", "No fix recommended"),
                        "issue_summary": finding.get("reason", "Analyzed for compliance"),
                        "citations": finding.get("citations", [])
                    })

                high_count = sum(1 for issue in compliance_report if issue["risk_level"] == "high")
                med_count = sum(1 for issue in compliance_report if issue["risk_level"] == "medium")
                low_count = sum(1 for issue in compliance_report if issue["risk_level"] == "low")
                
                summary = {
                    "total_clauses": len(final_state.clauses or []),
                    "high_risk": high_count,
                    "medium_risk": med_count,
                    "low_risk": low_count,
                    "risk_level": final_state.risk_summary.get("risk_level", "Low"),
                    "overall_score": final_state.risk_summary.get("overall_score", 100)
                }
                
                # Emit the final result
                result_payload = {
                    "drafted_contract": final_state.final_contract or contract_text,
                    "compliance_report": compliance_report,
                    "summary": summary,
                    "report_markdown": final_state.final_contract # or generate report_md if needed
                }
                
                await status_queue.put({"event": "result", "data": result_payload})
                await status_queue.put(None)

            asyncio.create_task(pipeline_worker())
            
            async for event in sse_generator(status_queue):
                yield event

        return StreamingResponse(run_pipeline(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error in check_compliance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
