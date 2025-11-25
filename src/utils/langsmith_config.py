"""
LangSmith Configuration and Setup
Provides LLM traceability and query tracking
"""

import os
from typing import Optional
from langsmith import Client
import structlog

logger = structlog.get_logger()


def setup_langsmith() -> Optional[Client]:
    """
    Initialize LangSmith for LLM tracing and monitoring

    Environment variables required:
    - LANGCHAIN_TRACING_V2: Set to "true" to enable tracing
    - LANGCHAIN_API_KEY: Your LangSmith API key
    - LANGCHAIN_PROJECT: Project name (default: "solar-pv-llm-ai")
    - LANGCHAIN_ENDPOINT: LangSmith endpoint (default: "https://api.smith.langchain.com")

    Returns:
        LangSmith client if configured, None otherwise
    """
    try:
        # Check if LangSmith is enabled
        tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

        if not tracing_enabled:
            logger.warning(
                "langsmith_disabled",
                message="LangSmith tracing is disabled. Set LANGCHAIN_TRACING_V2=true to enable."
            )
            return None

        # Get API key
        api_key = os.getenv("LANGCHAIN_API_KEY")
        if not api_key:
            logger.warning(
                "langsmith_no_api_key",
                message="LANGCHAIN_API_KEY not set. LangSmith tracing will not work."
            )
            return None

        # Set project name
        project_name = os.getenv("LANGCHAIN_PROJECT", "solar-pv-llm-ai")
        os.environ["LANGCHAIN_PROJECT"] = project_name

        # Set endpoint
        endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint

        # Initialize client
        client = Client(api_key=api_key, api_url=endpoint)

        logger.info(
            "langsmith_initialized",
            project=project_name,
            endpoint=endpoint,
            message="LangSmith tracing enabled successfully"
        )

        return client

    except Exception as e:
        logger.error(
            "langsmith_setup_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        return None


def get_trace_url(run_id: str) -> Optional[str]:
    """
    Generate a LangSmith trace URL for a specific run

    Args:
        run_id: The LangSmith run ID

    Returns:
        URL to view the trace in LangSmith
    """
    project_name = os.getenv("LANGCHAIN_PROJECT", "solar-pv-llm-ai")
    base_url = "https://smith.langchain.com"

    return f"{base_url}/o/{project_name}/runs/{run_id}"


def create_feedback(
    client: Client,
    run_id: str,
    score: float,
    comment: Optional[str] = None,
    feedback_key: str = "user_rating"
):
    """
    Submit feedback for a specific LangSmith run

    Args:
        client: LangSmith client
        run_id: The run ID to provide feedback for
        score: Feedback score (0-1)
        comment: Optional feedback comment
        feedback_key: Type of feedback (default: "user_rating")
    """
    try:
        client.create_feedback(
            run_id=run_id,
            key=feedback_key,
            score=score,
            comment=comment
        )

        logger.info(
            "langsmith_feedback_created",
            run_id=run_id,
            score=score,
            feedback_key=feedback_key
        )

    except Exception as e:
        logger.error(
            "langsmith_feedback_failed",
            run_id=run_id,
            error=str(e)
        )
