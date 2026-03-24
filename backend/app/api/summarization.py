from fastapi import APIRouter, HTTPException
from app.schemas import CaseSummaryRequest, CaseSummaryResponse, ErrorResponse
import logging

router = APIRouter(
    prefix="/api/summarization",
    tags=["Case Summarization"]
)

logger = logging.getLogger(__name__)

@router.post(
    "/summarize-case",
    response_model=CaseSummaryResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Summarize a legal judgment"
)
async def summarize_case(request: CaseSummaryRequest):
    try:
        from app.config import OPENROUTER_API_KEY
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from pydantic import BaseModel, Field
        from typing import List

        # Define output structure for the LLM
        class CaseSummaryOutput(BaseModel):
            summary: str = Field(description="A concise summary of the case")
            key_holdings: List[str] = Field(description="List of key holdings or rulings")
            citations: List[str] = Field(description="List of relevant citations mentioned")

        if not OPENROUTER_API_KEY:
             logger.warning("OPENROUTER_API_KEY not found. Returning dummy response.")
             return CaseSummaryResponse(
                summary="[Simulation] This is a simulated summary. The case discusses contract breach and damages.",
                key_holdings=["Holding 1: Contract was valid", "Holding 2: Breach occurred"],
                citations=["Section 73", "Hadley v Baxendale"]
            )

        from app.llms import get_llm_client
        client = get_llm_client()
        llm = client.chat_model
        
        parser = JsonOutputParser(pydantic_object=CaseSummaryOutput)

        prompt = PromptTemplate(
            template="""You are an expert legal assistant. Summarize the following legal case text.
            Extract key holdings and relevant citations.
            
            Format the output as JSON with the following keys:
            - summary: A concise summary of the case.
            - key_holdings: A list of the court's key rulings.
            - citations: A list of acts, sections, or cases cited in the text.
            
            Case Text:
            {case_text}
            
            {format_instructions}
            """,
            input_variables=["case_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        
        result = await chain.ainvoke({"case_text": request.case_text[:15000]}) # Limit text to avoid context window issues
        
        return CaseSummaryResponse(
            summary=result.get("summary", "Summary generation failed."),
            key_holdings=result.get("key_holdings", []),
            citations=result.get("citations", [])
        )

    except Exception as e:
        logger.error(f"Error in summarize_case: {e}")
        raise HTTPException(status_code=500, detail=str(e))
