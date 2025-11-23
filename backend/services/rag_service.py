"""
RAG (Retrieval Augmented Generation) service
Integrates vector store and LLM for enhanced question answering
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

from backend.services.vector_store_service import VectorStoreService
from backend.services.llm_service import LLMService
from backend.config import get_settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval Augmented Generation service
    Combines document retrieval with LLM generation for accurate, cited responses
    """

    def __init__(self):
        self.settings = get_settings()
        self.vector_store = VectorStoreService()
        self.llm = LLMService()
        logger.info("Initialized RAG service")

    def query(
        self,
        query_text: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Process query using RAG pipeline

        Steps:
        1. Generate embedding for query
        2. Retrieve relevant documents from vector store
        3. Build context from retrieved documents
        4. Generate response using LLM with context
        5. Extract citations if requested

        Args:
            query_text: User query
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
            include_citations: Whether to include source citations

        Returns:
            {
                "response": generated text,
                "confidence": confidence score,
                "retrieved_documents": list of retrieved docs,
                "citations": list of citations (if requested),
                "metadata": additional metadata
            }
        """
        start_time = datetime.utcnow()
        logger.info(f"Processing RAG query: {query_text[:100]}...")

        # Use configured defaults if not provided
        top_k = top_k or self.settings.rag_top_k
        similarity_threshold = similarity_threshold or self.settings.rag_similarity_threshold

        # Step 1: Generate query embedding
        logger.debug("Generating query embedding")
        query_embedding = self.llm.generate_embedding(query_text)

        # Step 2: Retrieve relevant documents
        logger.debug(f"Retrieving top {top_k} documents")
        retrieved_docs = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )

        if not retrieved_docs:
            logger.warning("No relevant documents found")
            return self._generate_fallback_response(query_text)

        # Step 3: Build context from retrieved documents
        context = self._build_context(retrieved_docs)

        # Step 4: Generate response with context
        prompt = self._build_prompt(query_text, context, include_citations)
        logger.debug("Generating LLM response")

        llm_response = self.llm.generate(prompt)

        # Step 5: Extract citations
        citations = []
        if include_citations:
            citations = self._extract_citations(
                llm_response["text"],
                retrieved_docs
            )

        # Calculate elapsed time
        elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        result = {
            "response": llm_response["text"],
            "confidence": llm_response["confidence"],
            "retrieved_documents": [
                {
                    "id": doc["id"],
                    "content": doc["content"],
                    "title": doc.get("title", ""),
                    "source_url": doc.get("source_url", ""),
                    "relevance_score": doc["score"]
                }
                for doc in retrieved_docs
            ],
            "citations": citations,
            "metadata": {
                "model_version": llm_response["model_version"],
                "latency_ms": elapsed_ms,
                "tokens": llm_response["metadata"].get("tokens", 0),
                "documents_retrieved": len(retrieved_docs)
            }
        }

        logger.info(f"RAG query completed in {elapsed_ms}ms with confidence {result['confidence']}")
        return result

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved documents

        Args:
            documents: List of retrieved documents with content and metadata

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, doc in enumerate(documents, 1):
            title = doc.get("title", "Document")
            content = doc["content"]
            source = doc.get("source_url", "")

            context_part = f"[Document {i}]"
            if title:
                context_part += f"\nTitle: {title}"
            if source:
                context_part += f"\nSource: {source}"
            context_part += f"\nContent: {content}\n"

            context_parts.append(context_part)

        context = "\n".join(context_parts)

        # Truncate if too long (to fit within token limits)
        max_context_length = 4000  # characters
        if len(context) > max_context_length:
            context = context[:max_context_length] + "... [truncated]"
            logger.warning(f"Context truncated to {max_context_length} characters")

        return context

    def _build_prompt(
        self,
        query: str,
        context: str,
        include_citations: bool
    ) -> str:
        """
        Build prompt for LLM with query and context

        Args:
            query: User query
            context: Retrieved document context
            include_citations: Whether to request citations

        Returns:
            Formatted prompt string
        """
        citation_instruction = ""
        if include_citations:
            citation_instruction = """
When referencing information from the provided documents, cite them using [Document N] format.
For example: "Solar panels typically have a 25-year warranty [Document 1]."
"""

        prompt = f"""You are a knowledgeable assistant specializing in Solar PV (Photovoltaic) systems.
Answer the user's question based on the provided context documents.

IMPORTANT INSTRUCTIONS:
- Use ONLY information from the provided documents to answer the question
- If the documents don't contain sufficient information to answer the question, say so clearly
- Be concise but comprehensive in your answer
- Use technical accuracy when discussing solar PV concepts
- Tailor your explanation to be understandable for users ranging from beginners to experts
{citation_instruction}

CONTEXT DOCUMENTS:
{context}

USER QUESTION:
{query}

YOUR ANSWER:
"""
        return prompt

    def _generate_fallback_response(self, query: str) -> Dict[str, Any]:
        """
        Generate fallback response when no documents are retrieved

        Args:
            query: User query

        Returns:
            Response dict with low confidence
        """
        logger.info("Generating fallback response (no documents retrieved)")

        fallback_prompt = f"""You are a helpful assistant. The user asked: "{query}"

Unfortunately, I don't have specific information about this in my knowledge base.
Please provide a brief, helpful response explaining that you don't have detailed
information about this specific topic, but provide any general knowledge you have
that might be relevant."""

        llm_response = self.llm.generate(fallback_prompt)

        return {
            "response": llm_response["text"],
            "confidence": 0.3,  # Low confidence for fallback
            "retrieved_documents": [],
            "citations": [],
            "metadata": {
                "model_version": llm_response["model_version"],
                "fallback": True,
                "tokens": llm_response["metadata"].get("tokens", 0)
            }
        }

    def _extract_citations(
        self,
        response_text: str,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Extract citations from response text

        Args:
            response_text: Generated response text
            documents: Retrieved documents

        Returns:
            List of citation dicts with source information
        """
        citations = []

        # Simple citation extraction - looks for [Document N] patterns
        import re
        citation_pattern = r'\[Document (\d+)\]'
        matches = re.finditer(citation_pattern, response_text)

        cited_indices = set()
        for match in matches:
            doc_num = int(match.group(1))
            cited_indices.add(doc_num)

        # Build citation list
        for idx in sorted(cited_indices):
            if idx <= len(documents):
                doc = documents[idx - 1]
                citations.append({
                    "document_number": idx,
                    "title": doc.get("title", ""),
                    "source_url": doc.get("source_url", ""),
                    "relevance_score": doc["score"]
                })

        logger.info(f"Extracted {len(citations)} citations from response")
        return citations

    def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Add documents to the knowledge base

        Args:
            documents: List of documents with 'content' and optional metadata

        Returns:
            Result dict with added document IDs
        """
        logger.info(f"Adding {len(documents)} documents to knowledge base")

        # Extract text content for embedding
        texts = [doc["content"] for doc in documents]

        # Generate embeddings in batch
        logger.debug("Generating embeddings for documents")
        embeddings = self.llm.batch_generate_embeddings(texts)

        # Add to vector store
        logger.debug("Adding documents to vector store")
        document_ids = self.vector_store.add_documents(documents, embeddings)

        logger.info(f"Successfully added {len(document_ids)} documents")

        return {
            "success": True,
            "document_count": len(document_ids),
            "document_ids": document_ids
        }

    def update_documents_zero_downtime(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update documents with zero downtime

        Args:
            documents: List of documents to update

        Returns:
            Result dict with update status
        """
        logger.info(f"Updating {len(documents)} documents with zero downtime")

        # Extract text content for embedding
        texts = [doc["content"] for doc in documents]

        # Generate embeddings
        embeddings = self.llm.batch_generate_embeddings(texts)

        # Perform zero-downtime update
        success = self.vector_store.update_documents_zero_downtime(
            documents,
            embeddings
        )

        return {
            "success": success,
            "document_count": len(documents),
            "message": "Documents updated successfully" if success else "Update failed"
        }

    def chunk_document(
        self,
        content: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> List[str]:
        """
        Split document into chunks for embedding

        Args:
            content: Document content
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.settings.rag_chunk_size
        chunk_overlap = chunk_overlap or self.settings.rag_chunk_overlap

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap

        logger.info(f"Split document into {len(chunks)} chunks")
        return chunks

    def health_check(self) -> Dict[str, bool]:
        """Check health of all RAG components"""
        return {
            "vector_store": self.vector_store.health_check(),
            "llm": self.llm.health_check(),
            "overall": (
                self.vector_store.health_check() and
                self.llm.health_check()
            )
        }
