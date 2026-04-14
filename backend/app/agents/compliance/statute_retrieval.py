from app.agents.state import ContractState
from app.config import INDEX_STATUTES
from app.RAG.pinecone_store import pinecone_service
import logging

logger = logging.getLogger(__name__)

class StatuteRetrievalAgent:
    async def process(self, state: ContractState):
        logger.info("StatuteRetrievalAgent: Retrieving relevant statutes")
        
        country = state.jurisdiction.get("country", "India")
        jurisdiction_filter = {"jurisdiction": country}
        
        try:
             # Construct query from contract type and key clauses if available
             query = f"Contract laws in {country} regarding {state.metadata.get('contract_type', 'general contracts')}"
             
             # Search for relevant statutes using integrated inference and filter
             docs = pinecone_service.search(
                 index_name=INDEX_STATUTES,
                 query=query,
                 k=5,
                 filter=jurisdiction_filter
             )
             
             if not docs:
                 logger.warning(f"No statutes found for {country}. Proceeding with general fallback.")
                 state.retrieved_statutes = []
             else:
                 state.retrieved_statutes = [
                     {"source": doc.metadata.get("source", "Unknown"), 
                      "section": doc.metadata.get("section", "N/A"), 
                      "text": doc.page_content}
                     for doc in docs
                 ]
                 logger.info(f"Retrieved {len(state.retrieved_statutes)} statutes")
                 
             state.add_audit_log("StatuteRetrieval", "Search", f"Retrieved {len(state.retrieved_statutes)} statutes")
             
        except Exception as e:
             logger.error(f"Statute retrieval failed: {e}")
             state.add_audit_log("StatuteRetrieval", "Error", str(e))
             # Ensure we don't crash, just proceed with empty list
             state.retrieved_statutes = []
