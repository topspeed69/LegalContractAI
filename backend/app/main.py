"""
LegalContractAI Backend - FastAPI Application
Main entry point for the backend API
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import drafting_router, compliance_router, health_router, reports_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LegalContractAI API",
    description="Backend API for AI-powered legal contract drafting and compliance checking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # Add your production frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(drafting_router)
app.include_router(compliance_router)
app.include_router(reports_router)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "LegalContractAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "contract_drafting": "/api/drafting/draft",
            "compliance_check": "/api/compliance/check",
            "structured_reports": "/api/reports/generate"
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler - runs when the application starts
    """
    logger.info("=" * 60)
    logger.info("LegalContractAI Backend Starting...")
    logger.info("=" * 60)
    
    # Verify agents are available
    try:
        from app.agents import ingestion_agent, clause_agent, compliance_agent, risk_agent, merge_agent
        logger.info("✓ All agents loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load agents: {str(e)}")
    
    # Verify LLM client
    try:
        from app.llms import get_gemini_client
        client = get_gemini_client()
        logger.info("✓ LLM client initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize LLM client: {str(e)}")
        logger.warning("Make sure GEMINI_API_KEY is set in environment variables")
    
    logger.info("=" * 60)
    logger.info("API Documentation available at: /docs")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler - runs when the application stops
    """
    logger.info("LegalContractAI Backend shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
