import logging
from app.agents.state import ContractState
from app.agents.compliance.ingestion import IngestionAgent
from app.agents.compliance.jurisdiction import JurisdictionResolverAgent
from app.agents.compliance.clause_extraction import ClauseExtractorAgent
from app.agents.compliance.statute_retrieval import StatuteRetrievalAgent
from app.agents.compliance.reasoning import ComplianceReasoningAgent
from app.agents.compliance.remediation import RemediationAgent
from app.agents.compliance.risk_scoring import RiskScoringAgent

logger = logging.getLogger(__name__)

class ComplianceOrchestrator:
    def __init__(self):
        self.ingestion = IngestionAgent()
        self.jurisdiction = JurisdictionResolverAgent()
        self.extractor = ClauseExtractorAgent()
        self.retriever = StatuteRetrievalAgent()
        self.reasoner = ComplianceReasoningAgent()
        self.remediator = RemediationAgent()
        self.risk_scorer = RiskScoringAgent()

    async def run(self, raw_text: str, metadata: dict = None, status_queue = None) -> ContractState:
        # 1. Initialize State
        state = ContractState(raw_text=raw_text, metadata=metadata or {})
        state.add_audit_log("Orchestrator", "Start", "Compliance check initiated")

        if status_queue:
            await status_queue.put({"event": "status", "data": {"stage": "Ingestion", "agent": "IngestionAgent"}})

        # 2. Ingestion (Fast)
        await self.ingestion.process(state)
        
        if status_queue:
            await status_queue.put({"event": "status", "data": {"stage": "Jurisdiction", "agent": "JurisdictionResolver"}})

        # 3. Jurisdiction (Fast)
        await self.jurisdiction.process(state)
        
        if status_queue:
            await status_queue.put({"event": "status", "data": {"stage": "Extraction", "agent": "ClauseExtractor"}})

        # 4. Clause Extraction (Fast)
        await self.extractor.process(state)
        
        if status_queue:
            await status_queue.put({"event": "status", "data": {"stage": "Retrieval", "agent": "StatuteRetrieval (RAG)"}})

        # 5. Statute Retrieval (RAG) (Fast)
        await self.retriever.process(state)
        
        if status_queue:
            await status_queue.put({"event": "status", "data": {"stage": "Reasoning", "agent": "ComplianceReasoning (Smart)"}})

        # 6. Compliance Reasoning (Thinking) (Smart)
        await self.reasoner.process(state, status_queue=status_queue)
        
        if status_queue:
            await status_queue.put({"event": "status", "data": {"stage": "Remediation", "agent": "RemediationAgent"}})

        # 7. Remediation (Smart/Fast)
        await self.remediator.process(state)
        
        if status_queue:
            await status_queue.put({"event": "status", "data": {"stage": "Risk Scoring", "agent": "RiskScorer"}})

        # 8. Risk Scoring
        await self.risk_scorer.process(state)

        state.add_audit_log("Orchestrator", "End", "Compliance check completed")
        return state
