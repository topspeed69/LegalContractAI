"""
Hybrid LLM Client - Smart Fallback between OpenAI and Gemini
"""

import os
import logging
import random
from typing import Optional, Dict, Any, List
from app.llms.openai_client import OpenAIClient, get_openai_client
from app.llms.gemini_client import GeminiClient, get_gemini_client

logger = logging.getLogger(__name__)

class HybridLLMClient:
    """
    LLM Client that orchestrates calls between OpenAI and Gemini.
    Strategies:
    1. Primary/Secondary: Try Primary first (check rate limit), if fail/limited, try Secondary.
    2. Load Balancing (Future): Distribute load.
    
    Current Logic:
    - Default to OpenAI as Primary (better quality generally).
    - If OpenAI rate limited (429 or local rate limiter blocked), switch to Gemini.
    - If both fail, raise exception.
    """

    def __init__(self, primary_provider: str = "openai", model: Optional[str] = None):
        self.primary_provider = primary_provider
        
        self.openai_client = None
        try:
            self.openai_client = get_openai_client()
        except Exception:
            logger.warning("HybridClient: OpenAI client not available (missing key?)")

        self.gemini_client = None
        try:
            self.gemini_client = get_gemini_client()
        except Exception:
             logger.warning("HybridClient: Gemini client not available (missing key?)")

    @property
    def chat_model(self):
        """Return a LangChain-compatible ChatOpenAI model for agent use."""
        if self.openai_client and hasattr(self.openai_client, 'chat_model'):
            return self.openai_client.chat_model
        raise AttributeError("No LangChain-compatible chat model available. OpenAI client is not configured.")

    async def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """
        Generate text with fallback.
        """
        # Determine execution order
        clients = self._get_execution_order()

        errors = []
        for client_name, client in clients:
            if not client:
                continue
                
            try:
                # 1. Check local rate limiter before making call (Fast fail)
                if not await client.rate_limiter.try_acquire():
                    logger.warning(f"HybridClient: {client_name} rate limiter blocked. Switching provider.")
                    continue
                
                # 2. Attempt generation
                logger.info(f"HybridClient: Attempting generation with {client_name}")
                return await client.generate(prompt, temperature, max_tokens, skip_rate_limit=True)
            
            except Exception as e:
                # Check for rate limit errors in exception
                # OpenAI: 429, Gemini: 429 or ResourceExhausted
                error_str = str(e).lower()
                is_rate_limit = "429" in error_str or "too many requests" in error_str or "resource exhausted" in error_str or "quota" in error_str
                
                if is_rate_limit:
                    logger.warning(f"HybridClient: {client_name} hit API rate limit (429). Switching provider.")
                    errors.append(f"{client_name}: Rate Limit")
                else:
                    logger.error(f"HybridClient: {client_name} failed with non-rate-limit error: {e}")
                    errors.append(f"{client_name}: {str(e)}")
                    # For non-rate limit errors (like Bad Request), maybe we SHOULDN'T switch?
                    # For now, let's switch for robustness, unless it's a prompt issue.
        
        raise Exception(f"HybridClient: All providers failed. Errors: {errors}")

    async def generate_contract(self, metadata: Dict[str, Any], requirements: str) -> str:
        """
        Generate contract with fallback.
        """
        clients = self._get_execution_order()
        errors = []

        for client_name, client in clients:
            if not client: continue
            
            try:
                if not await client.rate_limiter.try_acquire():
                    logger.warning(f"HybridClient: {client_name} rate limiter blocked. Switching.")
                    continue

                logger.info(f"HybridClient: Generating contract with {client_name}")
                return await client.generate_contract(metadata, requirements, skip_rate_limit=True)

            except Exception as e:
                logger.warning(f"HybridClient: {client_name} failed contract gen: {e}")
                errors.append(f"{client_name}: {e}")

        raise Exception(f"HybridClient: Contract generation failed. Errors: {errors}")

    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Route to Gemini preferably as it supports PDFs natively.
        If OpenAI is primary and PDF is present, we might want to FORCE Gemini or use OpenAI fallback (text only).
        """
        # If PDFs are present, PREFER Gemini because OpenAI implementation is text-only fallback currently
        if pdf_paths:
            # Force Gemini first if PDFs exist
            clients = [("Gemini", self.gemini_client), ("OpenAI", self.openai_client)]
        else:
             clients = self._get_execution_order()

        errors = []
        for client_name, client in clients:
            if not client: continue

            try:
                if not await client.rate_limiter.try_acquire():
                     continue
                
                return await client.generate_with_pdfs(system_prompt, user_prompt, pdf_paths, temperature, max_tokens, skip_rate_limit=True)
            except Exception as e:
                errors.append(f"{client_name}: {e}")
        
        raise Exception(f"HybridClient: Generation with PDFs failed. Errors: {errors}")


    def _get_execution_order(self):
        """
        Returns list of (name, client) tuples in order of preference.
        """
        order = []
        if self.primary_provider == "openai":
            if self.openai_client: order.append(("OpenAI", self.openai_client))
            if self.gemini_client: order.append(("Gemini", self.gemini_client))
        else:
            if self.gemini_client: order.append(("Gemini", self.gemini_client))
            if self.openai_client: order.append(("OpenAI", self.openai_client))
        return order


# Global instance
_hybrid_client: Optional['HybridLLMClient'] = None

def get_hybrid_client() -> 'HybridLLMClient':
    global _hybrid_client
    if _hybrid_client is None:
        _hybrid_client = HybridLLMClient()
    return _hybrid_client
