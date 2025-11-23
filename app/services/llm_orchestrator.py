"""
LLM Orchestrator for managing language model interactions.
Supports OpenAI and Anthropic models.
"""
import time
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from anthropic import Anthropic
import tiktoken
from loguru import logger

from app.core.config import settings
from app.models.schemas import ChatMessage, Citation


class LLMOrchestrator:
    """
    LLM Orchestrator for managing interactions with language models.
    Supports multiple LLM providers and handles prompt engineering.
    """

    def __init__(self):
        """Initialize LLM clients."""
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize LLM API clients."""
        try:
            if settings.OPENAI_API_KEY:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            else:
                logger.warning("OpenAI API key not configured")

            if settings.ANTHROPIC_API_KEY:
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Anthropic client initialized")
            else:
                logger.warning("Anthropic API key not configured")

        except Exception as e:
            logger.error(f"Error initializing LLM clients: {e}")

    def count_tokens(self, text: str, model: str = None) -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Input text
            model: Model name for encoding

        Returns:
            Token count
        """
        try:
            if model is None:
                model = settings.OPENAI_MODEL

            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error counting tokens: {e}. Using approximation.")
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4

    def build_context_prompt(
        self,
        query: str,
        citations: List[Citation],
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """
        Build augmented prompt with retrieved context.

        Args:
            query: User query
            citations: Retrieved context citations
            conversation_history: Previous conversation messages

        Returns:
            Augmented prompt
        """
        # Build context from citations
        context_parts = []
        if citations:
            context_parts.append("# Relevant Context from Knowledge Base\n")
            for i, citation in enumerate(citations, 1):
                context_parts.append(
                    f"## Source {i}: {citation.source}\n"
                    f"{citation.text_snippet}\n"
                    f"(Relevance: {citation.relevance_score:.2f})\n"
                )

        # Build conversation history
        history_parts = []
        if conversation_history:
            history_parts.append("# Previous Conversation\n")
            for msg in conversation_history[-5:]:  # Last 5 messages
                history_parts.append(f"{msg.role.upper()}: {msg.content}\n")

        # Build final prompt
        prompt = f"""You are an expert Solar PV (Photovoltaic) AI assistant. Your role is to provide accurate, helpful information about solar energy systems, photovoltaic technology, defect detection, system calculations, and related topics.

{chr(10).join(context_parts)}

{chr(10).join(history_parts)}

# User Query
{query}

# Instructions
- Provide accurate, detailed responses based on the context provided
- If the context contains relevant information, cite it in your response
- If you're unsure or the information isn't in the context, clearly state that
- For technical calculations, show your work and explain assumptions
- Be helpful, professional, and precise

# Response
"""
        return prompt

    def generate_response(
        self,
        query: str,
        citations: List[Citation] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        use_rag: bool = True
    ) -> Tuple[str, int]:
        """
        Generate LLM response.

        Args:
            query: User query
            citations: Retrieved context citations
            conversation_history: Previous messages
            max_tokens: Maximum response tokens
            temperature: LLM temperature
            use_rag: Whether to use RAG context

        Returns:
            Tuple of (response text, tokens used)
        """
        try:
            # Build prompt
            if use_rag and citations:
                prompt = self.build_context_prompt(query, citations, conversation_history)
            else:
                prompt = query

            # Count input tokens
            input_tokens = self.count_tokens(prompt)

            # Generate response using OpenAI
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful Solar PV AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                response_text = response.choices[0].message.content
                total_tokens = response.usage.total_tokens

                logger.info(f"Generated response using {settings.OPENAI_MODEL}: {total_tokens} tokens")
                return response_text, total_tokens

            # Fallback to mock response if no LLM configured
            logger.warning("No LLM client available, returning mock response")
            mock_response = self._generate_mock_response(query, citations)
            return mock_response, self.count_tokens(mock_response)

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Return error response
            error_response = f"I apologize, but I encountered an error processing your request: {str(e)}"
            return error_response, self.count_tokens(error_response)

    def _generate_mock_response(
        self,
        query: str,
        citations: Optional[List[Citation]] = None
    ) -> str:
        """
        Generate mock response for testing when LLM is not available.

        Args:
            query: User query
            citations: Retrieved citations

        Returns:
            Mock response
        """
        response_parts = [
            f"Thank you for your question about: '{query}'\n\n"
        ]

        if citations and len(citations) > 0:
            response_parts.append(
                f"Based on {len(citations)} relevant documents from our knowledge base:\n\n"
            )
            for i, citation in enumerate(citations[:3], 1):
                response_parts.append(
                    f"{i}. From {citation.source} (relevance: {citation.relevance_score:.2f}):\n"
                    f"   {citation.text_snippet[:200]}...\n\n"
                )

        response_parts.append(
            "This is a mock response. To get actual AI-generated responses, "
            "please configure your OpenAI or Anthropic API key in the .env file."
        )

        return "".join(response_parts)


# Global LLM orchestrator instance
llm_orchestrator = LLMOrchestrator()
