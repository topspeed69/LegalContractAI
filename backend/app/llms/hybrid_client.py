"""
Hybrid LLM Client - Smart Fallback between OpenRouter and Nvidia
"""

import os
import logging
import random
from typing import Optional, Dict, Any, List
from app.llms.openrouter_client import OpenRouterClient, get_openrouter_client
from app.llms.nvidia_client import NvidiaClient, get_nvidia_client

logger = logging.getLogger(__name__)

class HybridLLMClient:
    """
    LLM Client that orchestrates calls between OpenRouter and Nvidia.
    Strategies:
    1. Primary/Secondary: Try Primary first (check rate limit), if fail/limited, try Secondary.
    2. Load Balancing (Future): Distribute load.
    
    Current Logic:
    - Default to OpenRouter as Primary (better quality generally).
    - If OpenRouter rate limited (429 or local rate limiter blocked), switch to Nvidia.
    - If both fail, raise exception.
    """

    def __init__(self, primary_provider: str = "openrouter", model: Optional[str] = None):
        self.primary_provider = primary_provider
        
        self.openrouter_client = None
        try:
            self.openrouter_client = get_openrouter_client()
        except Exception:
            logger.warning("HybridClient: OpenRouter client not available (missing key?)")

        self.nvidia_client = None
        try:
            self.nvidia_client = get_nvidia_client()
        except Exception:
             logger.warning("HybridClient: Nvidia client not available (missing key?)")

    @property
    def chat_model(self):
        """Return a LangChain-compatible ChatOpenAI model for agent use."""
        if self.openrouter_client and hasattr(self.openrouter_client, 'chat_model'):
            return self.openrouter_client.chat_model
        raise AttributeError("No LangChain-compatible chat model available. OpenRouter client is not configured.")

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
                # 2. Attempt generation
                logger.info(f"HybridClient: Attempting generation with {client_name}")
                return await client.generate(prompt, temperature, max_tokens, skip_rate_limit=True)
            
            except Exception as e:
                # Check for rate limit errors in exception
                # OpenRouter: 429, Nvidia: 429 or ResourceExhausted
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
                logger.info(f"HybridClient: Generating contract with {client_name}")
                return await client.generate_contract(metadata, requirements, skip_rate_limit=True)

            except Exception as e:
                logger.warning(f"HybridClient: {client_name} failed contract gen: {e}")
                errors.append(f"{client_name}: {e}")

        raise Exception(f"HybridClient: Contract generation failed. Errors: {errors}")

    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        No native PDF support for Nvidia or OpenRouter at the moment.
        """
        clients = self._get_execution_order()

        errors = []
        for client_name, client in clients:
            if not client: continue

            try:
                return await client.generate_with_pdfs(system_prompt, user_prompt, pdf_paths, temperature, max_tokens, skip_rate_limit=True)
            except Exception as e:
                errors.append(f"{client_name}: {e}")
        
        raise Exception(f"HybridClient: Generation with PDFs failed. Errors: {errors}")


    def _get_execution_order(self):
        """
        Returns list of (name, client) tuples in order of preference.
        """
        order = []
        if self.primary_provider == "openrouter":
            if self.openrouter_client: order.append(("OpenRouter", self.openrouter_client))
            if self.nvidia_client: order.append(("Nvidia", self.nvidia_client))
        else:
            if self.nvidia_client: order.append(("Nvidia", self.nvidia_client))
            if self.openrouter_client: order.append(("OpenRouter", self.openrouter_client))
        return order


# Global instance
_hybrid_client: Optional['HybridLLMClient'] = None

def get_hybrid_client() -> 'HybridLLMClient':
    global _hybrid_client
    if _hybrid_client is None:
        _hybrid_client = HybridLLMClient()
    return _hybrid_client
