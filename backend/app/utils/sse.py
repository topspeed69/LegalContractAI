import json
from typing import Any, AsyncGenerator

def format_sse(data: Any, event: str = "message") -> str:
    """
    Format data as a Server-Sent Event (SSE).
    """
    # Always use json.dumps for data to handle multi-line strings / escaping correctly
    data = json.dumps(data)
    
    return f"event: {event}\ndata: {data}\n\n"

async def sse_generator(queue) -> AsyncGenerator[str, None]:
    """
    Consume from an async queue and yield SSE events.
    """
    while True:
        try:
            item = await queue.get()
            if item is None: # Termination signal
                break
                
            event_type = item.get("event", "status")
            yield format_sse(item.get("data"), event=event_type)
            
        except Exception:
            break
