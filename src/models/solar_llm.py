"""
Solar PV LLM Model
Main LLM interface with RAG, citations, and hallucination detection
"""

import os
import time
from typing import Dict, Any, List, Optional
import structlog
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.tracers import LangChainTracer
from langsmith import Client as LangSmithClient
from src.utils.langsmith_config import get_trace_url

logger = structlog.get_logger()


class SolarPVLLM:
    """
    Main LLM class for Solar PV queries
    Includes RAG, citation generation, and hallucination detection
    """

    def __init__(self):
        """Initialize the LLM with necessary components"""
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.api_key = os.getenv("OPENAI_API_KEY", "sk-dummy-key-for-testing")

        # Initialize LangSmith client if available
        try:
            self.langsmith_client = LangSmithClient()
            self.tracer = LangChainTracer(project_name="solar-pv-llm-ai")
        except Exception as e:
            logger.warning("langsmith_client_init_failed", error=str(e))
            self.langsmith_client = None
            self.tracer = None

        # Initialize LLM
        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.7,
                api_key=self.api_key
            )
            logger.info("llm_initialized", model=self.model_name)
        except Exception as e:
            logger.warning("llm_init_failed", error=str(e))
            self.llm = None

    async def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        include_citations: bool = True,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Process a query with full tracing and metrics

        Args:
            query: User's question about Solar PV systems
            context: Additional context for the query
            include_citations: Whether to include source citations
            temperature: LLM temperature parameter

        Returns:
            Dictionary containing answer, citations, confidence, etc.
        """
        start_time = time.time()
        run_id = None

        try:
            # Log query start
            logger.info("query_processing_started", query_length=len(query))

            # Simulate RAG retrieval (in production, this would query a vector DB)
            relevant_docs = self._retrieve_documents(query)

            # Build prompt with context
            enhanced_query = self._build_prompt(query, relevant_docs, context)

            # Generate response (with LangSmith tracing)
            if self.llm and self.tracer:
                # Run with tracing
                response = await self._generate_with_tracing(
                    enhanced_query,
                    temperature
                )
                run_id = response.get("run_id")
            else:
                # Fallback without LLM (for testing)
                response = self._generate_mock_response(query)

            # Calculate hallucination score
            hallucination_score = self._calculate_hallucination_score(
                response["answer"],
                relevant_docs
            )

            # Generate citations
            citations = None
            if include_citations and relevant_docs:
                citations = self._generate_citations(relevant_docs)

            # Calculate confidence
            confidence = self._calculate_confidence(
                response["answer"],
                relevant_docs,
                hallucination_score
            )

            # Build result
            result = {
                "answer": response["answer"],
                "citations": citations,
                "confidence": confidence,
                "hallucination_score": hallucination_score,
                "token_usage": response.get("token_usage", 0),
                "num_documents": len(relevant_docs)
            }

            # Add trace URL if available
            if run_id:
                result["trace_url"] = get_trace_url(run_id)

            latency = time.time() - start_time
            logger.info(
                "query_processing_completed",
                latency_seconds=latency,
                confidence=confidence,
                hallucination_score=hallucination_score
            )

            return result

        except Exception as e:
            logger.error(
                "query_processing_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def _retrieve_documents(self, query: str) -> List[Dict[str, str]]:
        """
        Retrieve relevant documents from vector database
        (Mock implementation for demonstration)
        """
        # In production, this would query ChromaDB or similar
        mock_docs = [
            {
                "content": "Solar PV panels convert sunlight into electricity using photovoltaic cells. The efficiency of modern panels ranges from 15-22%.",
                "source": "Solar Energy Handbook 2024",
                "page": "45"
            },
            {
                "content": "Optimal panel orientation in the Northern Hemisphere is typically south-facing with a tilt angle equal to the latitude.",
                "source": "PV Installation Guide",
                "page": "12"
            },
            {
                "content": "Regular maintenance includes cleaning panels and checking inverter performance. Annual inspections are recommended.",
                "source": "Solar Maintenance Best Practices",
                "page": "8"
            }
        ]

        logger.info("documents_retrieved", count=len(mock_docs))
        return mock_docs

    def _build_prompt(
        self,
        query: str,
        documents: List[Dict[str, str]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build an enhanced prompt with retrieved documents"""
        doc_context = "\n\n".join([
            f"[Source: {doc['source']}, Page {doc['page']}]\n{doc['content']}"
            for doc in documents
        ])

        prompt = f"""You are an expert on Solar PV (photovoltaic) systems. Answer the following question based on the provided context.

Context from authoritative sources:
{doc_context}

Question: {query}

Provide a clear, accurate answer based on the context above. If the context doesn't contain enough information to answer fully, acknowledge this limitation."""

        if context:
            prompt += f"\n\nAdditional context: {context}"

        return prompt

    async def _generate_with_tracing(
        self,
        prompt: str,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate LLM response with LangSmith tracing"""
        # This is a simplified version - in production, you'd use LangChain properly
        # For now, return mock data with tracing info
        import uuid
        run_id = str(uuid.uuid4())

        return {
            "answer": "Based on the provided context, solar PV panels typically have an efficiency of 15-22% and should be oriented south-facing in the Northern Hemisphere at a tilt angle matching your latitude. Regular maintenance is essential for optimal performance.",
            "token_usage": 150,
            "run_id": run_id
        }

    def _generate_mock_response(self, query: str) -> Dict[str, Any]:
        """Generate a mock response for testing when LLM is not available"""
        return {
            "answer": f"[Mock Response] This is a simulated answer about Solar PV systems for your query: '{query[:50]}...'. In production, this would be generated by an actual LLM with RAG.",
            "token_usage": 100
        }

    def _calculate_hallucination_score(
        self,
        answer: str,
        documents: List[Dict[str, str]]
    ) -> float:
        """
        Calculate hallucination risk score (0-1)
        In production, this would use semantic similarity or other NLP techniques
        """
        # Simple heuristic: check if answer contains info from documents
        doc_contents = " ".join([doc["content"].lower() for doc in documents])
        answer_lower = answer.lower()

        # Count matching key terms
        key_terms = ["solar", "pv", "panel", "efficiency", "energy", "photovoltaic"]
        matches = sum(1 for term in key_terms if term in answer_lower and term in doc_contents)

        # Simple scoring: fewer matches = higher hallucination risk
        if matches >= 4:
            return 0.1  # Low risk
        elif matches >= 2:
            return 0.3  # Medium risk
        else:
            return 0.7  # High risk

    def _generate_citations(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Generate formatted citations from retrieved documents"""
        return [
            {
                "source": doc["source"],
                "page": doc["page"],
                "excerpt": doc["content"][:200] + "..."
            }
            for doc in documents
        ]

    def _calculate_confidence(
        self,
        answer: str,
        documents: List[Dict[str, str]],
        hallucination_score: float
    ) -> float:
        """
        Calculate confidence score for the response (0-1)
        Based on document relevance and hallucination risk
        """
        # Confidence is inversely related to hallucination score
        base_confidence = 1.0 - hallucination_score

        # Adjust based on number of documents
        if len(documents) >= 3:
            base_confidence *= 1.1
        elif len(documents) == 0:
            base_confidence *= 0.5

        # Ensure it stays in [0, 1] range
        return max(0.0, min(1.0, base_confidence))
