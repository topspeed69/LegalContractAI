import os
import logging
from .nvidia_client import NvidiaClient, get_nvidia_client

logger = logging.getLogger(__name__)

def get_llm_client(provider: str = None, use_fast: bool = False):
    """
    Factory to get the appropriate LLM client.
    Defaults to Nvidia NIM.
    """
    from app.config import NVIDIA_MODEL_SMART, NVIDIA_MODEL_FAST
    
    selected_model = NVIDIA_MODEL_FAST if use_fast else NVIDIA_MODEL_SMART

    # Default to nvidia
    return get_nvidia_client(model=selected_model)

__all__ = ['NvidiaClient', 'get_llm_client', 'get_nvidia_client']
