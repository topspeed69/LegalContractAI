"""
LLM Client - Gemini Integration for Backend
Uses Google Gemini API similar to frontend implementation
"""

import os
import logging
import json
from typing import Optional, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Gemini LLM client for backend services.
    Compatible with compliance_agent and other agents.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model name (defaults to GEMINI_MODEL env var or gemini-2.0-flash-exp)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        logger.info(f"GeminiClient initialized with model: {self.model}")

    async def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """
        Generate text using Gemini API.

        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum output tokens

        Returns:
            Generated text response
        """
        try:
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature,
                    "responseMimeType": "text/plain"
                }
            }

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Gemini API error {response.status}: {error_text}")
                        raise Exception(f"Gemini API error: {error_text}")
                    
                    result = await response.json()
                    
                    # Parse response
                    candidates = result.get("candidates", [])
                    if candidates and len(candidates) > 0:
                        candidate = candidates[0]
                        parts = candidate.get("content", {}).get("parts", [])
                        if parts and len(parts) > 0:
                            text = "".join(part.get("text", "") for part in parts)
                            return text
                    
                    # Fallback
                    logger.warning("Unexpected Gemini response format")
                    return json.dumps(result)

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
            raise

    async def generate_contract(self, metadata: Dict[str, Any], requirements: str) -> str:
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

        prompt = f"""{system_instruction}

Draft a {purpose} contract with the following details:

**Parties:**
{parties_text}

**Jurisdiction:** {jurisdiction}
**Contract Term:** {term}

**User Requirements:**
{requirements}

Generate a complete, professional contract in Markdown format."""

        return await self.generate(prompt, temperature=0.3, max_tokens=4096)

    async def generate_with_pdfs(self, system_prompt: str, user_prompt: str, pdf_paths: Optional[list] = None, temperature: float = 0.2, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Generate content using Gemini and attach PDF templates as file references.

        Args:
            system_prompt: System-level instructions.
            user_prompt: The user-level prompt describing requirements.
            pdf_paths: List of local PDF absolute paths to include as file URIs.
            temperature: Sampling temperature.
            max_tokens: Maximum output tokens.

        Returns:
            Dict with key 'text' containing the generated contract.
        """
        try:
            files_payload = []
            if pdf_paths:
                for p in pdf_paths:
                    try:
                        # Ensure absolute path and convert to file URI
                        from pathlib import Path
                        path_obj = Path(p).resolve()
                        uri = f"file:///{path_obj.as_posix()}"
                        files_payload.append({
                            "file": {
                                "mime_type": "application/pdf",
                                "file_uri": uri
                            }
                        })
                    except Exception:
                        logger.warning(f"Skipping invalid PDF path: {p}")

            payload = {
                "prompt": {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                },
                "files": files_payload,
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature,
                    "responseMimeType": "text/plain"
                }
            }

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    text = await resp.text()
                    if resp.status != 200:
                        logger.error(f"Gemini API error {resp.status}: {text}")
                        raise Exception(f"Gemini API error: {text}")

                    try:
                        result = await resp.json()
                    except Exception:
                        # If response not JSON, return raw text
                        return {"text": text}

                    # Try to extract text from common Gemini response shapes
                    # 1) candidates -> content -> parts -> text
                    candidates = result.get("candidates") or []
                    if candidates:
                        candidate = candidates[0]
                        content = candidate.get("content") or {}
                        parts = content.get("parts") or []
                        if parts:
                            return {"text": "".join(p.get("text", "") for p in parts)}

                    # 2) outputs -> content -> list of output_text items
                    outputs = result.get("outputs") or []
                    if outputs:
                        out0 = outputs[0]
                        contents = out0.get("content") or []
                        texts = []
                        for c in contents:
                            if isinstance(c, dict) and c.get("type") == "output_text":
                                texts.append(c.get("text", ""))
                        if texts:
                            return {"text": "\n".join(texts)}

                    # Fallback: return stringified result
                    return {"text": json.dumps(result)}

        except Exception as e:
            logger.error(f"Error in generate_with_pdfs: {str(e)}", exc_info=True)
            raise


# Global client instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get or create singleton Gemini client instance.
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
