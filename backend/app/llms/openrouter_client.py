"""
LLM Client - OpenRouter Integration for Backend
Compatible replacement for GeminiClient and OpenAIClient
"""

import os
import logging
from typing import Optional, Dict, Any, List
import httpx
import json

logger = logging.getLogger(__name__)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class OpenRouterClient:
    """
    OpenRouter LLM client for backend services.
    Compatible with compliance_agent and other agents.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenRouter client.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/hunter-alpha")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided. Set OPENROUTER_API_KEY environment variable.")
        
        # Initialize standard ChatOpenAI with explicit parameters for both new and old langchain versions
        self.chat_model = ChatOpenAI(
            api_key=self.api_key,
            openai_api_key=self.api_key,
            model=self.model,
            base_url="https://openrouter.ai/api/v1",
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,
            max_retries=2
        )

        # Disabled rate limiter to prevent async deadlocks during orchestration
        logger.info(f"OpenRouterClient initialized with model: {self.model}")

    async def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096, skip_rate_limit: bool = False) -> str:
        """
        Generate text using OpenRouter API via HTTPX.
        """
        try:
            if temperature != self.chat_model.temperature:
                self.chat_model.temperature = temperature
                
            messages = [HumanMessage(content=prompt)]
            
            # Using direct ainvoke without rate limiter locks to prevent deadlock
            response = await self.chat_model.ainvoke(messages)
            
            return response.content

        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}", exc_info=True)
            raise

    async def generate_contract(self, metadata: Dict[str, Any], requirements: str, skip_rate_limit: bool = False) -> str:
        """
        Generate a contract using metadata and requirements.
        """
        parties = metadata.get("parties", [])
        jurisdiction = metadata.get("jurisdiction", "United States")
        purpose = metadata.get("purpose", "General Agreement")
        term = metadata.get("term", "12 months")

        parties_text = "\n".join([
            f"- {p['name']} ({p['role']})" for p in parties
        ])

        system_instruction = """You are a professional contract drafter. Create a comprehensive, legally sound contract in Markdown format.

IMPORTANT RULES:
1. Respond ONLY with the contract text in Markdown
2. Do NOT include any preamble like "Here is the contract" or "I've drafted"
3. Do NOT include any commentary or explanations outside the contract
4. Include proper sections: Title, Parties, Recitals, Terms, Signatures
5. Use clear headings and numbered clauses
6. Include standard legal language appropriate for the jurisdiction
"""

        user_prompt = f"""Draft a {purpose} contract with the following details:

**Parties:**
{parties_text}

**Jurisdiction:** {jurisdiction}
**Contract Term:** {term}

**User Requirements:**
{requirements}

Generate a complete, professional contract in Markdown format."""

        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=user_prompt)
        ]

        try:
            response = await self.chat_model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error in generate_contract: {str(e)}", exc_info=True)
            raise
    
    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096, skip_rate_limit: bool = False) -> Dict[str, Any]:
        """
        Generate content, ignoring PDF attachments for now or treating them as text if parsed.
        """
        logger.warning("OpenRouterClient.generate_with_pdfs called. PDF attachments are currently not supported in this client. Using text prompt only.")
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        text = await self.generate(full_prompt, temperature, max_tokens, skip_rate_limit=skip_rate_limit)
        return {"text": text}

# Global client instance
_openrouter_client: Optional[OpenRouterClient] = None

def get_openrouter_client(model: Optional[str] = None) -> OpenRouterClient:
    """
    Get or create singleton OpenRouter client instance.
    """
    global _openrouter_client
    if _openrouter_client is None or (model and _openrouter_client.model != model):
        return OpenRouterClient(model=model)
    return _openrouter_client
