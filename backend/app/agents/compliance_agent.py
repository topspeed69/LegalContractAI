"""
Compliance Agent - Legal Snippet Search and LLM Analysis
Used in: Compliance Check Service

Purpose:
- Search for relevant legal snippets using keyword matching
- Build LLM prompt comparing clause vs legal requirements
- Parse LLM response for compliance issues
- Return structured analysis
"""

import logging
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

from app.RAG.rag import get_rag_response

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ComplianceAgent:
    """
    Performs compliance analysis on contract clauses.
    Uses keyword-based legal snippet search + LLM analysis.
    """

    # Top N snippets to include in analysis
    TOP_N_SNIPPETS = 3

    # Legal texts directory (relative to backend root)
    LEGAL_TEXTS_DIR = "legal_texts"

    def __init__(self, legal_texts_path: Optional[str] = None, use_rag: bool = True):
        """
        Initialize the compliance agent.

        Args:
            legal_texts_path: Optional custom path to legal texts directory
        """
        self.legal_texts_path = legal_texts_path or self._get_default_legal_texts_path()
        self.use_rag = use_rag
        logger.info(f"ComplianceAgent initialized with legal texts path: {self.legal_texts_path}")

    def _get_default_legal_texts_path(self) -> str:
        """
        Get default path to legal_texts directory.
        """
        # Start from current file location and go up to backend root
        current_dir = Path(__file__).parent.parent.parent
        legal_texts_dir = current_dir / self.LEGAL_TEXTS_DIR

        # Create directory if it doesn't exist
        legal_texts_dir.mkdir(exist_ok=True)

        return str(legal_texts_dir)

    async def run(
        self,
        clause: str,
        jurisdiction: str,
        llm_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for compliance analysis.

        Args:
            clause: Single contract clause to analyze
            jurisdiction: Legal jurisdiction (e.g., "United States", "European Union")
            llm_client: Optional LLM client for analysis (must have async generate method)

        Returns:
            Dictionary containing:
            {
                "analysis_text": "raw LLM output",
                "snippets": [...],
                "parsed": {
                    "issue_summary": "...",
                    "risk_level": "low|medium|high",
                    "missing_requirements": [...],
                    "suggested_fix": "...",
                    "citations": [...]
                }
            }
        """
        try:
            logger.info(f"Analyzing clause for jurisdiction: {jurisdiction}")

            # Step 1: Retrieve context via RAG or local snippets
            rag_bundle = await self._fetch_rag_context(clause, jurisdiction)

            if rag_bundle and rag_bundle.get("context_chunks"):
                snippets = [
                    {
                        "text": chunk.get("text", ""),
                        "source": chunk.get("source", "RAG"),
                        "score": 1.0
                    }
                    for chunk in rag_bundle.get("context_chunks", [])
                ]
                rag_findings = rag_bundle.get("rag_findings", [])
                logger.info("Using %s RAG context chunk(s)", len(snippets))
            else:
                snippets = await self._search_legal_snippets(clause, jurisdiction)
                rag_findings = []
                logger.info("Falling back to keyword search with %s snippet(s)", len(snippets))

            if not snippets:
                logger.warning("No legal snippets found, using fallback analysis")
                return self._fallback_analysis(clause)

            # Step 2: Build LLM prompt
            prompt = self._build_llm_prompt(
                clause=clause,
                jurisdiction=jurisdiction,
                snippets=snippets,
                rag_findings=rag_findings,
                rag_draft=rag_bundle.get("drafted_contract") if rag_bundle else None
            )

            # Step 3: Call LLM for analysis
            if llm_client:
                analysis_text = await self._call_llm(llm_client, prompt)
            else:
                logger.warning("No LLM client provided, using mock analysis")
                analysis_text = self._mock_llm_response(clause, snippets)

            # Step 4: Parse LLM response
            parsed = self._parse_llm_response(analysis_text, snippets)
            parsed = self._merge_rag_findings(parsed, rag_findings)

            result = {
                "analysis_text": analysis_text,
                "snippets": snippets,
                "parsed": parsed,
                "rag_context": rag_bundle
            }
    async def _fetch_rag_context(
        self,
        clause: str,
        jurisdiction: str
    ) -> Optional[Dict[str, Any]]:
        """Use the shared RAG pipeline to retrieve grounded context."""
        if not self.use_rag:
            return None

        try:
            rag_payload = await get_rag_response(clause, jurisdiction=jurisdiction)
            return {
                "context_chunks": rag_payload.get("context_chunks", []),
                "rag_findings": rag_payload.get("compliance_report", []),
                "drafted_contract": rag_payload.get("drafted_contract", "")
            }
        except Exception as exc:
            logger.warning("RAG pipeline unavailable, reason: %s", exc)
            return None

            logger.info(f"Compliance analysis completed: {parsed.get('risk_level', 'unknown')} risk")
            return result

        except Exception as e:
            logger.error(f"Error during compliance analysis: {str(e)}", exc_info=True)
            raise

    async def _search_legal_snippets(
        self,
        clause: str,
        jurisdiction: str
    ) -> List[Dict[str, str]]:
        """
        Search for relevant legal snippets using keyword matching.

        Args:
            clause: Clause text to match against
            jurisdiction: Legal jurisdiction to filter by

        Returns:
            List of top N matching snippets with scores
        """
        # Extract keywords from clause
        keywords = self._extract_keywords(clause)

        # Search through legal text files
        snippet_scores = []

        legal_texts_path = Path(self.legal_texts_path)

        if not legal_texts_path.exists():
            logger.warning(f"Legal texts directory not found: {legal_texts_path}")
            return []

        # Search through all .txt and .md files
        for file_path in legal_texts_path.rglob("*.txt"):
            try:
                snippet_data = self._search_file(file_path, keywords, jurisdiction)
                snippet_scores.extend(snippet_data)
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {e}")

        for file_path in legal_texts_path.rglob("*.md"):
            try:
                snippet_data = self._search_file(file_path, keywords, jurisdiction)
                snippet_scores.extend(snippet_data)
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {e}")

        # Sort by score and take top N
        snippet_scores.sort(key=lambda x: x["score"], reverse=True)
        top_snippets = snippet_scores[:self.TOP_N_SNIPPETS]

        return [
            {
                "text": s["text"],
                "source": s["source"],
                "score": s["score"]
            }
            for s in top_snippets
        ]

    def _search_file(
        self,
        file_path: Path,
        keywords: List[str],
        jurisdiction: str
    ) -> List[Dict[str, Any]]:
        """
        Search a single file for matching snippets.
        """
        snippets = []

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Split into paragraphs or sections
        sections = self._split_into_sections(content)

        for section in sections:
            score = self._calculate_match_score(section, keywords, jurisdiction)

            if score > 0:
                snippets.append({
                    "text": section.strip(),
                    "source": file_path.name,
                    "score": score
                })

        return snippets

    def _split_into_sections(self, content: str) -> List[str]:
        """
        Split legal document into searchable sections.
        """
        # Try splitting by double newlines (paragraphs)
        sections = [s.strip() for s in content.split('\n\n') if s.strip()]

        if len(sections) < 2:
            # Try splitting by single newlines
            sections = [s.strip() for s in content.split('\n') if s.strip()]

        # Filter out very short sections
        sections = [s for s in sections if len(s) > 50]

        return sections

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from clause text.
        """
        # Convert to lowercase
        text_lower = text.lower()

        # Legal-specific important terms
        legal_terms = [
            'termination', 'liability', 'indemnification', 'confidentiality',
            'breach', 'remedy', 'dispute', 'arbitration', 'jurisdiction',
            'force majeure', 'severability', 'assignment', 'notice',
            'warranty', 'representation', 'covenant', 'obligation',
            'rights', 'responsibilities', 'payment', 'delivery',
            'intellectual property', 'privacy', 'data', 'compliance',
            'regulatory', 'statute', 'law', 'regulation', 'requirement'
        ]

        # Find matching legal terms
        keywords = [term for term in legal_terms if term in text_lower]

        # Extract potential important words (nouns/verbs)
        # Remove common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'shall', 'can'}

        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        filtered_words = [w for w in words if w not in stopwords]

        # Get most common words
        word_freq = Counter(filtered_words)
        common_words = [word for word, _ in word_freq.most_common(10)]

        # Combine legal terms and common words
        keywords.extend(common_words)

        return list(set(keywords))  # Remove duplicates

    def _calculate_match_score(
        self,
        section: str,
        keywords: List[str],
        jurisdiction: str
    ) -> float:
        """
        Calculate relevance score for a section.
        """
        section_lower = section.lower()
        score = 0.0

        # Keyword matching
        for keyword in keywords:
            if keyword in section_lower:
                score += 1.0

        # Jurisdiction bonus
        if jurisdiction.lower() in section_lower:
            score += 2.0

        # Length penalty for very long sections
        if len(section) > 1000:
            score *= 0.8

        return score

    def _build_llm_prompt(
        self,
        clause: str,
        jurisdiction: str,
        snippets: List[Dict[str, str]],
        rag_findings: Optional[List[Dict[str, Any]]] = None,
        rag_draft: Optional[str] = None
    ) -> str:
        """
        Build LLM prompt for compliance analysis.
        """
        snippet_text = "\n\n".join([
            f"Legal Reference {i+1} (from {s['source']}):\n{s['text']}"
            for i, s in enumerate(snippets)
        ])

        rag_findings_text = ""
        if rag_findings:
            formatted = []
            for idx, finding in enumerate(rag_findings, 1):
                formatted.append(
                    f"RAG Finding {idx}:\n"
                    f"Clause: {finding.get('clause', 'N/A')}\n"
                    f"Risk: {finding.get('risk_level', 'unknown')}\n"
                    f"Recommendation: {finding.get('fix', 'No fix provided')}\n"
                    f"Citations: {', '.join(finding.get('citations', []))}"
                )
            rag_findings_text = "\n\n".join(formatted)

        rag_draft_text = ""
        if rag_draft:
            rag_draft_text = f"\n\nRAG Suggested Rewrite:\n{rag_draft}"

        prompt = f"""You are a legal compliance expert analyzing a contract clause for compliance issues.

Jurisdiction: {jurisdiction}

Contract Clause to Analyze:
{clause}

Relevant Legal References:
{snippet_text}

Insights sourced from the Retrieval-Augmented Generation pipeline:
{rag_findings_text or 'No prior findings; rely on legal references above.'}
{rag_draft_text}

Please analyze the contract clause against the legal references and provide a JSON response with the following structure:
{{
    "issue_summary": "Brief summary of any compliance issues or confirmation of compliance",
    "risk_level": "low|medium|high",
    "missing_requirements": ["list of any missing legal requirements"],
    "suggested_fix": "Specific text or changes to make the clause compliant",
    "citations": ["list of relevant legal reference sources"]
}}

Respond ONLY with valid JSON. Do not include any other text or explanation outside the JSON structure."""

        return prompt

    def _merge_rag_findings(
        self,
        parsed: Dict[str, Any],
        rag_findings: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Blend RAG findings into parsed output for richer downstream signals."""
        if not rag_findings:
            return parsed

        merged = parsed.copy()
        citations = merged.get("citations", []) or []
        missing_requirements = merged.get("missing_requirements", []) or []

        for finding in rag_findings:
            rag_citations = finding.get("citations", []) or []
            citations.extend(rag_citations)

            fix = finding.get("fix")
            if fix and fix not in missing_requirements:
                missing_requirements.append(fix)

        # Deduplicate citations preserving order
        seen = set()
        unique_citations = []
        for cite in citations:
            if cite and cite not in seen:
                seen.add(cite)
                unique_citations.append(cite)

        merged["citations"] = unique_citations
        merged["missing_requirements"] = missing_requirements
        merged["rag_findings"] = rag_findings
        return merged

    async def _call_llm(self, llm_client: Any, prompt: str) -> str:
        """
        Call LLM client for analysis.
        """
        try:
            # Assume llm_client has a generate method
            if hasattr(llm_client, 'generate'):
                response = await llm_client.generate(prompt)
            elif hasattr(llm_client, '__call__'):
                response = await llm_client(prompt)
            else:
                raise ValueError("LLM client must have generate method or be callable")

            return response

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._mock_llm_response("", [])

    def _mock_llm_response(self, clause: str, snippets: List[Dict[str, str]]) -> str:
        """
        Generate mock LLM response for testing without LLM.
        """
        return json.dumps({
            "issue_summary": "This is a mock compliance analysis. The clause appears generally compliant but may require review by legal counsel.",
            "risk_level": "low",
            "missing_requirements": ["Specific jurisdiction clause may be needed"],
            "suggested_fix": "Consider adding explicit reference to governing law.",
            "citations": [s["source"] for s in snippets[:2]]
        })

    def _parse_llm_response(
        self,
        analysis_text: str,
        snippets: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.
        """
        try:
            # Try to extract JSON from response
            # Sometimes LLM adds extra text, so find JSON block
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)

                # Validate required fields
                return {
                    "issue_summary": parsed.get("issue_summary", "No summary provided"),
                    "risk_level": parsed.get("risk_level", "medium").lower(),
                    "missing_requirements": parsed.get("missing_requirements", []),
                    "suggested_fix": parsed.get("suggested_fix", "No fix suggested"),
                    "citations": parsed.get("citations", [s["source"] for s in snippets])
                }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON: {e}")

        # Fallback parsing
        return self._fallback_parsing(analysis_text, snippets)

    def _fallback_parsing(
        self,
        analysis_text: str,
        snippets: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Fallback parsing when JSON parsing fails.
        """
        # Heuristic risk detection
        text_lower = analysis_text.lower()

        if any(word in text_lower for word in ['high risk', 'critical', 'violation', 'non-compliant', 'illegal']):
            risk_level = "high"
        elif any(word in text_lower for word in ['medium risk', 'concern', 'missing', 'should']):
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "issue_summary": analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text,
            "risk_level": risk_level,
            "missing_requirements": [],
            "suggested_fix": "Please review with legal counsel",
            "citations": [s["source"] for s in snippets]
        }

    def _fallback_analysis(self, clause: str) -> Dict[str, Any]:
        """
        Provide fallback analysis when no snippets found.
        """
        return {
            "analysis_text": "No relevant legal references found for this clause.",
            "snippets": [],
            "parsed": {
                "issue_summary": "Unable to perform detailed compliance analysis due to lack of reference materials.",
                "risk_level": "medium",
                "missing_requirements": ["Legal reference materials needed"],
                "suggested_fix": "Consult with legal counsel for jurisdiction-specific requirements.",
                "citations": []
            }
        }


# Singleton instance
agent = ComplianceAgent()


async def run(
    clause: str,
    jurisdiction: str,
    llm_client: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Convenience function to run the compliance agent.

    Args:
        clause: Contract clause text
        jurisdiction: Legal jurisdiction
        llm_client: Optional LLM client

    Returns:
        Compliance analysis results
    """
    return await agent.run(clause, jurisdiction, llm_client)
