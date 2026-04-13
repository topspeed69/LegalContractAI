from fastapi import APIRouter, HTTPException
from app.schemas import LegalResearchRequest, LegalResearchResponse, Citation, ErrorResponse
from app.RAG.pinecone_store import pinecone_service
from app.config import INDEX_STATUTES, INDEX_CASES, INDEX_REGULATIONS, NVIDIA_API_KEY
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

router = APIRouter(
    prefix="/api/research",
    tags=["Legal Research"]
)

logger = logging.getLogger(__name__)

@router.post(
    "/legal-research",
    response_model=LegalResearchResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Conduct legal research with RAG"
)
async def legal_research(request: LegalResearchRequest):
    try:
        query = request.query
        logger.info(f"Received legal research query: {query}")

        # 1. Retrieve from Pinecone (Statutes and Cases)
        # We search multiple indexes to get a comprehensive view
        
        # Statutes
        statute_store = pinecone_service.get_vector_store(INDEX_STATUTES)
        statute_docs = statute_store.similarity_search(query, k=3)
        
        # Regulations
        reg_store = pinecone_service.get_vector_store(INDEX_REGULATIONS)
        reg_docs = reg_store.similarity_search(query, k=2)

        # Case Law
        case_store = pinecone_service.get_vector_store(INDEX_CASES)
        case_docs = case_store.similarity_search(query, k=2)
        
        all_docs = statute_docs + reg_docs + case_docs
        
        # 2. Format Context
        context_str = ""
        citations = []
        
        for i, doc in enumerate(all_docs):
            source = doc.metadata.get("source", "Unknown Source")
            title = doc.metadata.get("title", "Legal Document")
            content = doc.page_content
            context_str += f"Source {i+1} ({title} - {source}):\n{content}\n\n"
            
            citations.append(Citation(
                title=title,
                source=source,
                text=content[:200] + "..." # Snippet
            ))
            
        if not all_docs:
             logger.warning("No RAG documents retrieved. Proceeding with general knowledge fallback.")
             context_str = "No specific legal documents found in the database. Please answer based on general legal principles."

        # 3. Synthesize with LLM
        if not NVIDIA_API_KEY:
            logger.warning("NVIDIA_API_KEY not found. Returning dummy response.")
            return LegalResearchResponse(
                answer="[Simulation] This is a simulated answer. Section 10 of the Indian Contract Act states that all agreements are contracts if they are made by the free consent of parties competent to contract.",
                citations=[
                    Citation(
                        title="Indian Contract Act, 1872",
                        source="Section 10",
                        text="All agreements are contracts if they are made by the free consent of parties competent to contract..."
                    ),
                    Citation(
                        title="Mohori Bibee v Dharmodas Ghose",
                        source="1903",
                        text="The Privy Council held that a contract with a minor is void-ab-initio."
                    )
                ]
            )

        from app.llms import get_llm_client
        client = get_llm_client()
        llm = client.chat_model
        
        prompt = PromptTemplate.from_template(
            """You are an expert Indian legal research assistant. Use the provided context to answer the user's query comprehensively.
            Cite the specific statutes, sections, or cases from the context in your answer.
            If the context does not contain the answer, state that you cannot find specific legal authority in the provided database, but provide general legal principles if known (clearly marking them as general knowledge).
            
            Context:
            {context}
            
            User Query: {query}
            
            Answer:"""
        )
        
        chain = prompt | llm | StrOutputParser()
        answer = await chain.ainvoke({"context": context_str, "query": query})
        
        return LegalResearchResponse(
            answer=answer,
            citations=citations
        )

    except Exception as e:
        logger.error(f"Error in legal_research: {e}")
        raise HTTPException(status_code=500, detail=str(e))
