
from fastapi import APIRouter, HTTPException, status
from app.schemas import ClauseAnalysisRequest, ClauseAnalysisResponse, ClauseRisk, ErrorResponse
from app.llms import get_llm_client
import logging

router = APIRouter(
    prefix="/api/analysis",
    tags=["Clause Analysis"]
)

logger = logging.getLogger(__name__)

@router.post(
    "/analyze-clauses",
    response_model=ClauseAnalysisResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Analyze contract clauses for risks"
)
async def analyze_clauses(request: ClauseAnalysisRequest):
    try:
        from app.config import OPENROUTER_API_KEY, INDEX_STATUTES
        from app.RAG.pinecone_store import pinecone_service
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from app.schemas import ClauseAnalysisResponse

        if not OPENROUTER_API_KEY:
             # Fallback if no key (for testing without billing)
             return ClauseAnalysisResponse(
                risks=[
                    {
                        "clause_text": request.text[:50] + "...",
                        "risk_level": "Medium",
                        "explanation": "[Simulation] Missing API Key. This is a simulated risk analysis.",
                        "recommendation": "Check API configuration."
                    }
                ],
                summary="Analysis complete (Simulated)."
            )

        # 1. Retrieve RAG Context
        rag_context = ""
        try:
            vector_store = pinecone_service.get_vector_store(INDEX_STATUTES)
            # Query for laws relevant to this text
            docs = vector_store.similarity_search(request.text[:500], k=3) 
            
            if docs:
                rag_context = "\n".join([f"- {d.page_content}" for d in docs])
                rag_context = f"\nRelevant Legal Statutes/Guidelines:\n{rag_context}\n"
            else:
                 logger.warning("No RAG documents retrieved for clause analysis. Using general principles.")
                 rag_context = "\nNo specific statutes found. Evaluate based on general legal principles and standard commercial risks.\n"
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}. Proceeding without context.")
            rag_context = "\n(RAG System Unavailable) Evaluate based on general legal principles.\n"

        # 2. Analyze with LLM (uses hybrid client for fallback)
        from app.llms import get_llm_client
        client = get_llm_client()
        llm = client.chat_model
        
        parser = JsonOutputParser(pydantic_object=ClauseAnalysisResponse)

        prompt = PromptTemplate(
            template="""You are an expert contract risk analyst. Analyze the following contract text.
            Identify key clauses and their risk levels (High, Medium, Low).
            Provide a brief explanation for each risk and a recommendation.

            Use the provided legal context if relevant.
            
            {rag_context}
            
            Contract Text:
            {text}
            
            {format_instructions}
            """,
            input_variables=["text", "rag_context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        
        result = await chain.ainvoke({"text": request.text[:15000], "rag_context": rag_context})
        
        return ClauseAnalysisResponse(
            risks=result.get("risks", []),
            summary=result.get("summary", "Analysis complete.")
        )

    except Exception as e:
        logger.error(f"Error in analyze_clauses: {e}")
        raise HTTPException(status_code=500, detail=str(e))
