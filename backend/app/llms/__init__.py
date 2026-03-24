import os
from .nvidia_client import NvidiaClient, get_nvidia_client
from .openrouter_client import OpenRouterClient, get_openrouter_client
from .hybrid_client import HybridLLMClient, get_hybrid_client

def get_llm_client(provider: str = None, use_fast: bool = False):
    """
    Factory to get the appropriate LLM client.
    Prioritizes passed provider, then OpenRouter, then Nvidia.
    """
    OPENROUTER_FAST = "openai/gpt-4o-mini"
    NVIDIA_FAST = "moonshotai/kimi-k2-thinking"
    
    selected_model = None
    if use_fast:
        if provider == "openrouter" or (not provider and os.getenv("OPENROUTER_API_KEY")):
            selected_model = OPENROUTER_FAST
        elif provider == "nvidia" or (not provider and os.getenv("NVIDIA_API_KEY")):
            selected_model = NVIDIA_FAST

    if provider == "nvidia":
        return get_nvidia_client(model=selected_model)
    
    # Default to openrouter, effectively bypassing HybridLLMClient logic
    return get_openrouter_client(model=selected_model)

__all__ = ['NvidiaClient', 'OpenRouterClient', 'HybridLLMClient', 'get_llm_client', 'get_nvidia_client', 'get_openrouter_client', 'get_hybrid_client']
