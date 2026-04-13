from fastapi import APIRouter, HTTPException, Query
from app.schemas import ChatRequest, ChatResponse, ErrorResponse, Citation
from app.config import NVIDIA_API_KEY, INDEX_STATUTES, INDEX_CASES, INDEX_REGULATIONS
from app.llms import get_llm_client
from app.RAG.pinecone_store import pinecone_service
from app.services.encryption import encryption_service
from app.services.supabase_service import db_service

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
import logging
import json
import base64

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat Assistant"]
)

logger = logging.getLogger(__name__)

# --- Tools Definition ---

@tool
def get_legal_context(query: str):
    """
    Search for Indian legal context, statutes, case laws, and regulations from the knowledge base.
    Use this for any specific legal questions, section queries, or precedent lookups.
    """
    try:
        # Statutes
        statute_store = pinecone_service.get_vector_store(INDEX_STATUTES)
        statute_docs = statute_store.similarity_search(query, k=2)
        
        # Case Law
        case_store = pinecone_service.get_vector_store(INDEX_CASES)
        case_docs = case_store.similarity_search(query, k=2)
        
        context = []
        for doc in statute_docs + case_docs:
            source = doc.metadata.get("source", "Unknown")
            title = doc.metadata.get("title", "Legal Doc")
            context.append({
                "source": source,
                "title": title,
                "content": doc.page_content
            })
        return context
    except Exception as e:
        logger.error(f"RAG Tool Error: {e}")
        return "Failed to retrieve legal context."

@tool
def get_platform_navigation(intent: str):
    """
    Find the URL route for a specific platform tool.
    Input should be the feature name the user is looking for.
    Returns: The route string (e.g., '/contract-drafting') or None if no match.
    """
    routes = {
        # Contract Drafting — supports ALL contract types: NDA, employment, service, lease, partnership, etc.
        "drafting": "/contract-drafting",
        "contract-drafting": "/contract-drafting",
        "contract drafting": "/contract-drafting",
        "draft": "/contract-drafting",
        "contract": "/contract-drafting",
        "create contract": "/contract-drafting",
        "nda": "/contract-drafting",
        "non-disclosure agreement": "/contract-drafting",
        "non disclosure agreement": "/contract-drafting",
        "non disclosure": "/contract-drafting",
        "confidentiality agreement": "/contract-drafting",
        "employment agreement": "/contract-drafting",
        "employment contract": "/contract-drafting",
        "service agreement": "/contract-drafting",
        "service contract": "/contract-drafting",
        "lease agreement": "/contract-drafting",
        "rental agreement": "/contract-drafting",
        "partnership agreement": "/contract-drafting",
        "partnership deed": "/contract-drafting",
        "sale agreement": "/contract-drafting",
        "sale deed": "/contract-drafting",
        "vendor agreement": "/contract-drafting",
        "freelance contract": "/contract-drafting",
        "consulting agreement": "/contract-drafting",
        "mou": "/contract-drafting",
        "memorandum of understanding": "/contract-drafting",
        "power of attorney": "/contract-drafting",
        "will": "/contract-drafting",
        "loan agreement": "/contract-drafting",
        "franchise agreement": "/contract-drafting",
        "joint venture agreement": "/contract-drafting",
        "licensing agreement": "/contract-drafting",
        "license agreement": "/contract-drafting",
        "indemnity agreement": "/contract-drafting",
        "indemnity bond": "/contract-drafting",
        "affidavit": "/contract-drafting",
        "letter of intent": "/contract-drafting",
        "terms of service": "/contract-drafting",
        "privacy policy": "/contract-drafting",
        "shareholder agreement": "/contract-drafting",
        "operating agreement": "/contract-drafting",
        # Compliance Check
        "compliance": "/compliance-check",
        "compliance-check": "/compliance-check",
        "compliance check": "/compliance-check",
        "check compliance": "/compliance-check",
        "regulatory check": "/compliance-check",
        "regulation check": "/compliance-check",
        "legal compliance": "/compliance-check",
        "compliance review": "/compliance-check",
        "compliance audit": "/compliance-check",
        # Legal Research
        "research": "/legal-research",
        "legal-research": "/legal-research",
        "legal research": "/legal-research",
        "case law": "/legal-research",
        "statute": "/legal-research",
        "statutes": "/legal-research",
        "find law": "/legal-research",
        "search law": "/legal-research",
        "legal precedent": "/legal-research",
        "section lookup": "/legal-research",
        # Case Summary
        "summarization": "/case-summary",
        "case-summary": "/case-summary",
        "case summary": "/case-summary",
        "summary": "/case-summary",
        "summarize": "/case-summary",
        "case summarization": "/case-summary",
        "summarize judgment": "/case-summary",
        "summarize case": "/case-summary",
        "judgment summary": "/case-summary",
        # Loophole Detection
        "loopholes": "/loophole-detection",
        "loophole-detection": "/loophole-detection",
        "loophole detection": "/loophole-detection",
        "loophole": "/loophole-detection",
        "find loopholes": "/loophole-detection",
        "detect loopholes": "/loophole-detection",
        "contract gaps": "/loophole-detection",
        "missing clauses": "/loophole-detection",
        # Clause Classification / Risk Analysis
        "classification": "/clause-classification",
        "clause-classification": "/clause-classification",
        "clause classification": "/clause-classification",
        "classify": "/clause-classification",
        "clause": "/clause-classification",
        "risk analysis": "/clause-classification",
        "clause analysis": "/clause-classification",
        "analyze clauses": "/clause-classification",
        "clause risk": "/clause-classification",
        # Chat
        "chat": "/chat-assistant",
        "chat-assistant": "/chat-assistant",
        "advisor": "/chat-assistant",
        # Dashboard & History
        "dashboard": "/dashboard",
        "history": "/activity-history",
        "activity": "/activity-history",
        "activity history": "/activity-history",
    }
    result = routes.get(intent.lower().strip())
    return result if result else None

@router.post(
    "/chat-assistant",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Smart Advisory Chat Assistant"
)
async def chat_assistant(request: ChatRequest):
    try:
        user_message = request.message
        user_id = request.user_id
        logger.info(f"Received smart chat message: {user_message} (User: {user_id})")

        # 1. Store original user message if user logged in (encrypted)
        if user_id:
            try:
                enc_user_msg = encryption_service.encrypt(user_message)
                db_service.store_chat_message(user_id, encrypted_data=enc_user_msg)
            except Exception as e:
                logger.error(f"Failed to store encrypted user message: {e}")

        if not NVIDIA_API_KEY:
            # Simulation response
            reply = "[Simulation] I am a legal assistant. I can help you draft contracts, check compliance, or research laws."
            if user_id:
                try:
                    enc_reply = encryption_service.encrypt(reply)
                    db_service.store_chat_message(user_id, encrypted_data=enc_reply)
                except Exception as e:
                    logger.error(f"Failed to store encrypted simulation reply: {e}")
            
            return ChatResponse(
                reply=reply,
                intent="general_prompt",
                suggested_action=None
            )

        client = get_llm_client(request.provider if hasattr(request, 'provider') else None, use_fast=True)
        
        # Try LangChain agent path (requires OpenAI chat_model)
        try:
            llm = client.chat_model
        except AttributeError:
            # Fallback: use hybrid generate() for non-OpenAI providers
            logger.info("chat_model not available, using generate() fallback")
            fallback_prompt = f"""You are a highly intelligent Indian Legal AI Advisor on the LegalAssist platform.

You have TWO roles:
1. **General Assistant**: For general legal questions, greetings, or conversational queries, respond helpfully. Set intent to "general" and suggested_action to null.
2. **Platform Navigator**: When the user wants to USE a specific platform feature, set intent to "navigation" and provide the correct suggested_action route.

Here are ALL the platform features, what they do, and their EXACT routes:

1. **Contract Drafting** → "/contract-drafting"
   - Generates professional legal contracts/documents using AI agents.
   - Supports ALL contract types: NDA (Non-Disclosure Agreement), Employment Agreements, Service Agreements, Lease/Rental Agreements, Partnership Agreements/Deeds, Sale Agreements/Deeds, Vendor Agreements, Freelance/Consulting Contracts, MOU (Memorandum of Understanding), Power of Attorney, Wills, Loan Agreements, Franchise Agreements, Joint Venture Agreements, Licensing Agreements, Indemnity Bonds, Affidavits, Letters of Intent, Terms of Service, Privacy Policies, Shareholder Agreements, Operating Agreements, and any other legal document.
   - User provides: contract type, parties, jurisdiction, requirements, key terms.
   - Use this when the user wants to draft, create, write, generate, or make ANY type of contract or legal document.

2. **Compliance Check** → "/compliance-check"
   - Analyzes existing contract text for compliance issues against Indian regulations.
   - Identifies high/medium/low risk clauses and suggests fixes with legal citations.
   - Uses a multi-agent pipeline: Ingestion → Jurisdiction → Extraction → Retrieval → Reasoning → Remediation → Risk Scoring.
   - Use this when the user wants to check, review, audit, or verify compliance of a contract.

3. **Legal Research** → "/legal-research"
   - RAG-powered legal research across Indian statutes, case laws, and regulations.
   - Searches Pinecone knowledge base and provides cited answers.
   - Use this when the user wants to research, look up, find, or search for specific laws, sections, acts, precedents, or legal information.

4. **Case Summary** → "/case-summary"
   - Summarizes legal judgments and court orders using AI.
   - Extracts key holdings, citations, and rulings from case text.
   - Use this when the user wants to summarize a case, judgment, court order, or legal ruling.

5. **Loophole Detection** → "/loophole-detection"
   - Scans contracts for loopholes, gaps, ambiguities, and missing clauses.
   - Identifies potential legal vulnerabilities in contract text.
   - Use this when the user wants to find loopholes, gaps, weaknesses, or missing clauses in a contract.

6. **Clause Classification / Risk Analysis** → "/clause-classification"
   - Analyzes individual contract clauses and classifies their risk levels.
   - Provides risk explanations and recommendations for each clause.
   - Use this when the user wants to analyze, classify, or assess risk of specific clauses in a contract.

7. **Activity History** → "/activity-history"
   - View past generated documents and chat history.

8. **Dashboard** → "/dashboard"
   - Overview of platform usage, credits, and recent activity.

CRITICAL RULES:
- For simple questions like "hello", "how are you", "what can you do", "explain X" → intent MUST be "general" and suggested_action MUST be null.
- ONLY set suggested_action to a route when the user EXPLICITLY wants to navigate to or use a feature (e.g., "I want to draft a contract", "draft an NDA", "check compliance", "take me to compliance check").
- ANY request to draft/create/write ANY type of contract or document → MUST use "/contract-drafting".
- NEVER return a route like "/chat-assistant" or "null" as suggested_action. If unsure, set suggested_action to null.
- suggested_action must be EXACTLY one of the routes listed above, or null.

Return ONLY a valid JSON object (no markdown, no extra text):
{{"reply": "your helpful response", "intent": "general|navigation", "suggested_action": "/route-here-or-null", "citations": null}}

User message: {user_message}"""
            raw_output = await client.generate(fallback_prompt, temperature=0.3)
            try:
                import re as _re
                _match = _re.search(r'(\{.*\})', raw_output, _re.DOTALL)
                if _match:
                    result = json.loads(_match.group(1))
                else:
                    result = {"reply": raw_output, "intent": "general", "suggested_action": None, "citations": None}
            except Exception:
                result = {"reply": raw_output, "intent": "general", "suggested_action": None, "citations": None}
            
            # Sanitize suggested_action: only allow valid routes
            valid_routes = {
                "/contract-drafting", "/compliance-check", "/legal-research",
                "/case-summary", "/loophole-detection", "/clause-classification",
                "/activity-history", "/dashboard"
            }
            suggested_action = result.get("suggested_action")
            if suggested_action and suggested_action not in valid_routes:
                logger.warning(f"Invalid suggested_action from LLM: {suggested_action}, setting to None")
                suggested_action = None
            
            final_reply = result.get("reply", raw_output)
            if user_id:
                try:
                    enc_assistant_msg = encryption_service.encrypt(final_reply)
                    db_service.store_chat_message(user_id, encrypted_data=enc_assistant_msg)
                except Exception as e:
                    logger.error(f"Failed to store encrypted assistant reply: {e}")
            
            return ChatResponse(
                reply=final_reply,
                intent=result.get("intent", "general"),
                suggested_action=suggested_action,
                citations=None
            )

        # Define the Agent (OpenAI path)
        tools = [get_legal_context, get_platform_navigation]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a highly intelligent Indian Legal AI Advisor on the LegalAssist platform.
            
            You have TWO roles:
            1. General Assistant: For greetings, legal questions, or conversational queries, respond helpfully with intent "general" and suggested_action null.
            2. Platform Navigator: When the user EXPLICITLY wants to use a platform feature, use 'get_platform_navigation' to find the correct route.
            
            Here are ALL the platform features you can navigate users to:
            
            1. Contract Drafting ("/contract-drafting"): Generates professional legal contracts using AI agents. Supports ALL types: NDA, Employment Agreement, Service Agreement, Lease/Rental, Partnership, Sale Deed, Vendor Agreement, Freelance/Consulting, MOU, Power of Attorney, Will, Loan Agreement, Franchise, Joint Venture, Licensing, Indemnity, Affidavit, Letter of Intent, Terms of Service, Privacy Policy, Shareholder Agreement, and more.
            2. Compliance Check ("/compliance-check"): Analyzes existing contracts for compliance issues against Indian regulations. Identifies risk levels and suggests fixes.
            3. Legal Research ("/legal-research"): RAG-powered research across Indian statutes, case laws, and regulations with cited answers.
            4. Case Summary ("/case-summary"): AI-powered summarization of legal judgments, court orders, and rulings.
            5. Loophole Detection ("/loophole-detection"): Scans contracts for loopholes, gaps, ambiguities, and missing clauses.
            6. Clause Classification ("/clause-classification"): Risk analysis and classification of individual contract clauses.
            7. Activity History ("/activity-history"): Past documents and chat history.
            8. Dashboard ("/dashboard"): Usage overview, credits, and recent activity.
            
            Guidelines:
            1. Directness: Keep responses helpful but concise.
            2. Feature Routing: ONLY use 'get_platform_navigation' when the user explicitly wants to navigate to a feature (e.g., "draft a contract", "draft an NDA", "check compliance").
            3. ANY request to draft/create/write ANY type of contract or document → navigate to "draft" or "nda" etc. via 'get_platform_navigation'.
            4. For simple questions, greetings, or general legal queries, DO NOT use any tools. Just respond directly with intent "general".
            5. Routing Integrity: You MUST use the exact routes returned by the tool. NEVER invent routes.
            6. If 'get_platform_navigation' returns None, set suggested_action to null.
            7. For legal context queries, use 'get_legal_context' and cite sources.
            
            Response Format: You MUST return a JSON-compatible string:
            {{ "reply": "...", "intent": "research|navigation|general", "suggested_action": "/route|null", "citations": [{{ "title": "...", "source": "...", "text": "..." }}]|null }}
            """),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        response = await agent_executor.ainvoke({"input": user_message})
        output = response.get("output", "{}")

        try:
            import re
            json_match = re.search(r'(\{.*\})', output, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = {"reply": output, "intent": "general", "suggested_action": None, "citations": None}
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse agent JSON: {e}. Output was: {output}")
            result = {"reply": output, "intent": "general", "suggested_action": None, "citations": None}

        # 2. Store assistant reply if user logged in (encrypted)
        final_reply = result.get("reply", "I can help with that.")
        if user_id:
            try:
                enc_assistant_msg = encryption_service.encrypt(final_reply)
                db_service.store_chat_message(user_id, encrypted_data=enc_assistant_msg)
            except Exception as e:
                logger.error(f"Failed to store encrypted assistant reply: {e}")

        # Map list of dicts to Citation objects if present
        citations = []
        if result.get("citations"):
            for c in result["citations"]:
                citations.append(Citation(title=c.get("title"), source=c.get("source"), text=c.get("text")))

        return ChatResponse(
            reply=final_reply,
            intent=result.get("intent", "general"),
            suggested_action=result.get("suggested_action"),
            citations=citations if citations else None
        )

    except Exception as e:
        logger.error(f"Error in chat_assistant agent: {e}")
        return ChatResponse(
            reply="I encountered an error processing your query. Please try again.",
            intent="error",
            suggested_action=None
        )

@router.get(
    "/history",
    summary="Get encrypted/plaintext chat history"
)
async def get_history(user_id: str = Query(..., description="User ID to fetch history for")):
    try:
        raw_messages = db_service.get_chat_history(user_id)
        formatted_messages = []
        
        for msg in raw_messages:
            content = msg.get("content") # Legacy plaintext
            is_encrypted = msg.get("is_encrypted", False)
            encrypted_content_b64 = msg.get("encrypted_content")
            
            if is_encrypted and encrypted_content_b64:
                try:
                    # Supabase returns bytes as Base64 strings or hex sometimes via Python client
                    # The library usually handles it, but let's be safe
                    if isinstance(encrypted_content_b64, str):
                        # Some Supabase implementations return '\x...' hex strings
                        if encrypted_content_b64.startswith('\\x'):
                            encrypted_bytes = bytes.fromhex(encrypted_content_b64[2:])
                        else:
                            encrypted_bytes = base64.b64decode(encrypted_content_b64)
                    else:
                        encrypted_bytes = encrypted_content_b64
                    
                    decrypted_content = encryption_service.decrypt(encrypted_bytes)
                    content = decrypted_content
                except Exception as e:
                    logger.error(f"Failed to decrypt message {msg.get('id')}: {e}")
                    content = "[Error: Decryption Failed]"
            
            formatted_messages.append({
                "id": str(msg.get("id")),
                "content": content,
                "role": "user" if msg.get("user_id") == user_id else "assistant", # Simplified role logic for history
                "created_at": msg.get("created_at"),
                "is_encrypted": is_encrypted
            })
            
        return formatted_messages
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")
