from fastapi import APIRouter, HTTPException
from app.schemas import LegalResearchRequest, LegalResearchResponse, Citation, ErrorResponse
from app.RAG.pinecone_store import pinecone_service
from app.config import INDEX_STATUTES, INDEX_REGULATIONS, NVIDIA_API_KEY
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

router = APIRouter(
    prefix="/api/research",
    tags=["Legal Research"]
)

logger = logging.getLogger(__name__)

from fastapi.responses import StreamingResponse
from app.utils.sse import sse_generator
import asyncio
import json

@router.post(
    "/legal-research",
    response_class=StreamingResponse,
    summary="Conduct legal research with RAG and streaming status"
)
async def legal_research(request: LegalResearchRequest):
    try:
        query = request.query
        logger.info(f"Received legal research query with streaming: {query}")

        async def run_pipeline():
            status_queue = asyncio.Queue()
            
            async def pipeline_worker():
                try:
                    await status_queue.put({"event": "status", "data": {"stage": "Query Analysis", "agent": "Researcher"}})
                    
                    # 1. Retrieval using integrated inference
                    await status_queue.put({"event": "status", "data": {"stage": "Legal Retrieval", "agent": "Researcher"}})
                    statute_docs = pinecone_service.search(INDEX_STATUTES, query, k=3)
                    regulation_docs = pinecone_service.search(INDEX_REGULATIONS, query, k=2)
                    
                    await status_queue.put({"event": "status", "data": {"stage": "Synthesis", "agent": "Researcher (Smart)"}})
                    all_docs = statute_docs + regulation_docs
                    
                    context_str = ""
                    citations = []
                    for i, doc in enumerate(all_docs):
                        source = doc.metadata.get("source", "Legal Database")
                        title = doc.metadata.get("title", f"Document {i+1}")
                        context_str += f"Source {i+1} ({title} - {source}):\n{doc.page_content}\n\n"
                        citations.append({
                            "title": title,
                            "source": source,
                            "text": doc.page_content[:200] + "..."
                        })

                    # 3. LLM Synthesis
                    from app.llms import get_llm_client
                    client = get_llm_client(use_fast=False) # Smart model
                    llm = client.chat_model
                    
                    prompt = PromptTemplate.from_template(
                        """You are an expert Indian legal research assistant. Use the provided context to answer the user's query comprehensively.
                        Context: {context}
                        User Query: {query}
                        Answer:"""
                    )
                    
                    chain = prompt | llm | StrOutputParser()
                    answer = await chain.ainvoke({"context": context_str, "query": query})
                    
                    await status_queue.put({"event": "result", "data": {"answer": answer, "citations": citations}})
                    await status_queue.put(None)
                except Exception as e:
                    logger.error(f"Error in research pipeline worker: {e}")
                    await status_queue.put({"event": "error", "data": str(e)})
                    await status_queue.put(None)

            asyncio.create_task(pipeline_worker())
            
            async for event in sse_generator(status_queue):
                yield event

        return StreamingResponse(run_pipeline(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error in legal_research: {e}")
        raise HTTPException(status_code=500, detail=str(e))
