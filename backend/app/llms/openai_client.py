
"""
LLM Client - OpenAI Integration for Backend
Compatible replacement for GeminiClient
"""

import os
import logging
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class OpenAIClient:
    """
    OpenAI LLM client for backend services.
    Compatible with compliance_agent and other agents.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (defaults to OPENAI_MODEL env var or gpt-4o)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        self.chat_model = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=0.3
        )

        from app.utils.rate_limiter import RateLimiter
        # OpenAI Rate Limits: 20 RPM, 1 RPS (Software Limit)
        self.rate_limiter = RateLimiter(rpm=20, rps=1.0)
        
        logger.info(f"OpenAIClient initialized with model: {self.model}")

    async def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096, skip_rate_limit: bool = False) -> str:
        """
        Generate text using OpenAI API.

        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum output tokens

        Returns:
            Generated text response
        """
        try:
            # Update temperature if different
            if temperature != self.chat_model.temperature:
                self.chat_model.temperature = temperature
                
            messages = [HumanMessage(content=prompt)]
            
            if skip_rate_limit:
                 response = await self.chat_model.ainvoke(messages)
            else:
                async with self.rate_limiter:
                    response = await self.chat_model.ainvoke(messages)
            
            return response.content

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
            raise

    async def generate_contract(self, metadata: Dict[str, Any], requirements: str, skip_rate_limit: bool = False) -> str:
        """
        Generate a contract using metadata and requirements.

        Args:
            metadata: Contract metadata (parties, jurisdiction, etc.)
            requirements: User requirements and specifications

        Returns:
            Generated contract text in Markdown
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
            if skip_rate_limit:
                response = await self.chat_model.ainvoke(messages)
            else:
                async with self.rate_limiter:
                    response = await self.chat_model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error in generate_contract: {str(e)}", exc_info=True)
            raise
    
    # Mock support for generate_with_pdfs since OpenAI doesn't support file URIs the same way Gemini does
    # or implement it if needed using vision/file search. For now, just a placeholder or text-only fallback.
    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096, skip_rate_limit: bool = False) -> Dict[str, Any]:
        """
        Generate content, ignoring PDF attachments for now or treating them as text if parsed.
        """
        logger.warning("OpenAIClient.generate_with_pdfs called. PDF attachments are currently not supported in this client. Using text prompt only.")
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        text = await self.generate(full_prompt, temperature, max_tokens, skip_rate_limit=skip_rate_limit)
        return {"text": text}

# Global client instance
_openai_client: Optional[OpenAIClient] = None

def get_openai_client(model: Optional[str] = None) -> OpenAIClient:
    """
    Get or create singleton OpenAI client instance.
    """
    global _openai_client
    if _openai_client is None or (model and _openai_client.model != model):
        # We allow creating a new instance if a specific model is requested
        return OpenAIClient(model=model)
    return _openai_client
