"""
LLM Client - Nvidia NIM Integration for Backend
"""

import os
import logging
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class NvidiaClient:
    """
    Nvidia NIM LLM client for backend services.
    Compatible with compliance_agent and other agents.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Nvidia NIM client using official OpenAI library as requested.
        """
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.model = model or os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2-thinking")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
        if not self.api_key:
            raise ValueError("Nvidia API key not provided. Set NVIDIA_API_KEY environment variable.")
        
        # Initialize official OpenAI async client
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

        logger.info(f"NvidiaClient initialized with model: {self.model}")

    @property
    def chat_model(self):
        """
        Returns a LangChain-compatible ChatOpenAI instance.
        """
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            temperature=0.3
        )

    async def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 16384, skip_rate_limit: bool = False) -> str:
        """
        Generate text using Nvidia NIM API via openai SDK.
        """
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9
            )
            
            message = completion.choices[0].message
            # Some NIM models send reasoning content
            reasoning = getattr(message, "reasoning_content", "") or ""
            content = message.content or ""
            
            # If we want to return both, we could format it, but usually standard string is expected
            if reasoning:
                return f"{reasoning}\n\n{content}"
            return content

        except Exception as e:
            logger.error(f"Error calling Nvidia NIM API: {str(e)}", exc_info=True)
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

        system_instruction = "You are a professional contract drafter. Create a comprehensive, legally sound contract in Markdown format.\n\nIMPORTANT RULES:\n1. Respond ONLY with the contract text in Markdown\n2. Do NOT include any preamble like \"Here is the contract\"\n3. Do NOT include any commentary or explanations outside the contract\n4. Include proper sections: Title, Parties, Recitals, Terms, Signatures\n5. Use clear headings and numbered clauses\n6. Include standard legal language appropriate for the jurisdiction"

        user_prompt = f"Draft a {purpose} contract with the following details:\n\n**Parties:**\n{parties_text}\n\n**Jurisdiction:** {jurisdiction}\n**Contract Term:** {term}\n\n**User Requirements:**\n{requirements}\n\nGenerate a complete, professional contract in Markdown format."

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]

        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=4096,
                top_p=0.9
            )
            message = completion.choices[0].message
            reasoning = getattr(message, "reasoning_content", "") or ""
            content = message.content or ""
            
            if reasoning:
                return f"{reasoning}\n\n{content}"
            return content
            
        except Exception as e:
            logger.error(f"Error in generate_contract (Nvidia): {str(e)}", exc_info=True)
            raise
    
    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096, skip_rate_limit: bool = False) -> Dict[str, Any]:
        """
        Generate content, ignoring PDF attachments for now.
        """
        logger.warning("NvidiaClient.generate_with_pdfs called. PDF attachments are currently not supported in this client. Using text prompt only.")
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        text = await self.generate(full_prompt, temperature, max_tokens, skip_rate_limit=skip_rate_limit)
        return {"text": text}

# Global client instance
_nvidia_client: Optional[NvidiaClient] = None

def get_nvidia_client(model: Optional[str] = None) -> NvidiaClient:
    """
    Get or create singleton Nvidia client instance.
    """
    global _nvidia_client
    if _nvidia_client is None or (model and _nvidia_client.model != model):
        _nvidia_client = NvidiaClient(model=model)
    return _nvidia_client
