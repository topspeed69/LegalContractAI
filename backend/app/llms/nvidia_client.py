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
        from app.config import LLM_MAX_RETRIES, LLM_TIMEOUT
        
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.model = model or os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
        if not self.api_key:
            raise ValueError("Nvidia API key not provided. Set NVIDIA_API_KEY environment variable.")
        
        # Initialize official OpenAI async client with improved resilience
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            max_retries=LLM_MAX_RETRIES,
            timeout=LLM_TIMEOUT
        )

        logger.info(f"NvidiaClient initialized for model: {self.model} (Max Retries: {LLM_MAX_RETRIES}, Timeout: {LLM_TIMEOUT}s)")

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
        Generate text using Nvidia NIM API via openai SDK with internal streaming
        to prevent read timeouts and better capture reasoning_content.
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                stream=True
            )
            
            content_chunks = []
            reasoning_chunks = []
            
            async for chunk in stream:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                
                # Accummulate content
                if hasattr(delta, "content") and delta.content is not None:
                    content_chunks.append(delta.content)
                
                # Accumulate reasoning (some models use reasoning_content)
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    reasoning_chunks.append(reasoning)

            full_content = "".join(content_chunks).strip()
            full_reasoning = "".join(reasoning_chunks).strip()

            if full_reasoning:
                logger.debug(f"NvidiaClient ({self.model}) reasoning: {full_reasoning[:300]}...")
            
            # Additional cleanup for models that might put <think> tags in the main content
            import re
            full_content = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()
            
            if not full_content and full_reasoning:
                # Fallback if content is empty but we have reasoning (uncommon but possible)
                logger.warning("NvidiaClient: Empty content but found reasoning. Using reasoning as content.")
                return full_reasoning

            return full_content

        except Exception as e:
            from app.config import NVIDIA_MODEL_SMART, NVIDIA_MODEL_FAST
            
            # If this is the "smart" model failing, attempt fallback to "fast" model
            if self.model == NVIDIA_MODEL_SMART and not skip_rate_limit:
                logger.warning(f"Smart model ({self.model}) failed. Attempting fallback to fast model: {NVIDIA_MODEL_FAST} (Error: {str(e)})")
                try:
                    fallback_client = get_nvidia_client(model=NVIDIA_MODEL_FAST)
                    return await fallback_client.generate(prompt, temperature, max_tokens, skip_rate_limit=True)
                except Exception as fallback_err:
                    logger.error(f"Fallback model also failed: {str(fallback_err)}")
                    raise e
            
            logger.error(f"Error calling Nvidia NIM API ({self.model}): {str(e)}")
            raise

    async def generate_contract(self, metadata: Dict[str, Any], requirements: str, skip_rate_limit: bool = False) -> str:
        """
        Generate a contract using metadata and requirements.
        Uses internal streaming for better stability.
        """
        parties = metadata.get("parties", [])
        jurisdiction = metadata.get("jurisdiction", "United States")
        purpose = metadata.get("purpose", "General Agreement")
        term = metadata.get("term", "12 months")

        parties_text = "\n".join([f"- {p['name']} ({p['role']})" for p in parties])

        system_instruction = "You are a professional contract drafter. Create a comprehensive, legally sound contract in Markdown format.\n"
        user_prompt = f"Draft a {purpose} contract with the following details:\n\n**Parties:**\n{parties_text}\n\n**Jurisdiction:** {jurisdiction}\n**Contract Term:** {term}\n\n**User Requirements:**\n{requirements}"

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=5120,
                top_p=0.9,
                stream=True
            )
            
            content_chunks = []
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content is not None:
                    content_chunks.append(delta.content)
            
            full_content = "".join(content_chunks).strip()
            
            import re
            full_content = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()
            
            return full_content
            
        except Exception as e:
            from app.config import NVIDIA_MODEL_SMART, NVIDIA_MODEL_FAST
            
            if self.model == NVIDIA_MODEL_SMART and not skip_rate_limit:
                logger.warning(f"Smart model contract generation failed. Error: {str(e)}. Falling back to fast model.")
                try:
                    fallback_client = get_nvidia_client(model=NVIDIA_MODEL_FAST)
                    return await fallback_client.generate_contract(metadata, requirements, skip_rate_limit=True)
                except Exception as fe:
                    logger.error(f"Fallback failed during contract drafting: {fe}")
                    raise e
            
            logger.error(f"Error in generate_contract ({self.model}): {str(e)}")
            raise
    
    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096, skip_rate_limit: bool = False) -> Dict[str, Any]:
        """
        Generate content, ignoring PDF attachments for now.
        """
        logger.warning("NvidiaClient.generate_with_pdfs called. Using text prompt only.")
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        text = await self.generate(full_prompt, temperature, max_tokens, skip_rate_limit=skip_rate_limit)
        return {"text": text}

# Global clients registry
_nvidia_clients: Dict[str, NvidiaClient] = {}

def get_nvidia_client(model: Optional[str] = None) -> NvidiaClient:
    """
    Get or create a Nvidia client instance for a specific model.
    """
    from app.config import NVIDIA_MODEL_FAST, NVIDIA_MODEL_SMART
    
    # Logic to decide default model if none provided
    target_model = model or NVIDIA_MODEL_FAST
    
    if target_model not in _nvidia_clients:
        _nvidia_clients[target_model] = NvidiaClient(model=target_model)
    
    return _nvidia_clients[target_model]
