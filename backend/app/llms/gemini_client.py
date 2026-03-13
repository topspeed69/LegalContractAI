"""
LLM Client - Gemini Integration for Backend
Uses Google Gemini API similar to frontend implementation
"""

import os
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiClient:
    """
    Gemini LLM client for backend services using google-generativeai SDK.
    Compatible with compliance_agent and other agents.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model name (defaults to GEMINI_MODEL env var or gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        from app.utils.rate_limiter import RateLimiter
        # Gemini Rate Limits: 10 RPM (Flash 2.0 Free Tier)
        self.rate_limiter = RateLimiter(rpm=10)
        
        logger.info(f"GeminiClient initialized with model: {self.model_name}")

    async def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 25600, skip_rate_limit: bool = False) -> str:
        """
        Generate text using Gemini SDK.
        """
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            if skip_rate_limit:
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config=generation_config
                )
            else:
                async with self.rate_limiter:
                    response = await self.model.generate_content_async(
                        prompt,
                        generation_config=generation_config
                    )
            
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
            # Fallback for blocked content or other issues
            if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
                 logger.warning(f"Prompt blocked: {e.response.prompt_feedback}")
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

        prompt = f"""{system_instruction}

Draft a {purpose} contract with the following details:

**Parties:**
{parties_text}

**Jurisdiction:** {jurisdiction}
**Contract Term:** {term}

**User Requirements:**
{requirements}

Generate a complete, professional contract in Markdown format."""

        return await self.generate(prompt, temperature=0.3, max_tokens=4096, skip_rate_limit=skip_rate_limit)

    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096, skip_rate_limit: bool = False) -> Dict[str, Any]:
        """
        Generate content using Gemini and attach PDF templates.
        Uses the File API to upload PDFs.
        """
        try:
            parts = [f"{system_prompt}\n\n{user_prompt}"]
            uploaded_files = []
            
            if pdf_paths:
                for p in pdf_paths:
                    try:
                        # Upload file using the SDK
                        if os.path.exists(p):
                            logger.info(f"Uploading file for Gemini: {p}")
                            file_upload = genai.upload_file(p)
                            uploaded_files.append(file_upload)
                            parts.append(file_upload)
                        else:
                            logger.warning(f"PDF path not found: {p}")
                    except Exception as e:
                        logger.warning(f"Failed to upload PDF {p}: {e}")

            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            if skip_rate_limit:
                response = await self.model.generate_content_async(
                    parts,
                    generation_config=generation_config
                )
            else:
                async with self.rate_limiter:
                    response = await self.model.generate_content_async(
                        parts,
                        generation_config=generation_config
                    )
            
            return {"text": response.text}

        except Exception as e:
            logger.error(f"Error in generate_with_pdfs: {str(e)}", exc_info=True)
            raise


# Global client instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client(model: Optional[str] = None) -> GeminiClient:
    """
    Get or create singleton Gemini client instance.
    """
    global _gemini_client
    if _gemini_client is None or (model and _gemini_client.model != model):
        return GeminiClient(model=model)
    return _gemini_client
