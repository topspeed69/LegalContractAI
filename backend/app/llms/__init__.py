import os
import logging
from .nvidia_client import NvidiaClient, get_nvidia_client

logger = logging.getLogger(__name__)

def get_llm_client(provider: str = None, use_fast: bool = False):
    """
    Factory to get the appropriate LLM client.
    Defaults to Nvidia NIM.
    """
    NVIDIA_FAST = os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2-thinking")
    
    selected_model = None
    if use_fast:
        selected_model = NVIDIA_FAST

    # Default to nvidia
    return get_nvidia_client(model=selected_model)

__all__ = ['NvidiaClient', 'get_llm_client', 'get_nvidia_client']
