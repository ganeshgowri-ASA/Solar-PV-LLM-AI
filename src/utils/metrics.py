"""
Prometheus Metrics Collector
Centralized metrics for monitoring the Solar PV LLM AI system
"""

from prometheus_client import Counter, Histogram, Gauge, Info


class MetricsCollector:
    """Centralized metrics collector for the application"""

    def __init__(self):
        # Request metrics
        self.requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint']
        )

        self.request_latency = Histogram(
            'http_request_duration_seconds',
            'HTTP request latency in seconds',
            ['method', 'endpoint'],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        )

        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'endpoint']
        )

        # LLM-specific metrics
        self.llm_queries_total = Counter(
            'llm_queries_total',
            'Total LLM queries processed'
        )

        self.llm_latency = Histogram(
            'llm_query_duration_seconds',
            'LLM query latency in seconds',
            buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 30.0, 60.0]
        )

        self.llm_tokens_used = Counter(
            'llm_tokens_total',
            'Total tokens used by LLM'
        )

        # Hallucination detection metrics
        self.hallucination_score = Gauge(
            'llm_hallucination_score',
            'Current hallucination risk score (0-1)'
        )

        self.hallucinations_detected = Counter(
            'llm_hallucinations_detected_total',
            'Total number of potential hallucinations detected'
        )

        # RAG metrics
        self.rag_retrievals_total = Counter(
            'rag_retrievals_total',
            'Total RAG document retrievals'
        )

        self.rag_retrieval_latency = Histogram(
            'rag_retrieval_duration_seconds',
            'RAG retrieval latency in seconds',
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )

        self.rag_documents_retrieved = Histogram(
            'rag_documents_retrieved',
            'Number of documents retrieved per query',
            buckets=[1, 2, 3, 5, 10, 20, 50, 100]
        )

        # Citation metrics
        self.citations_generated = Counter(
            'citations_generated_total',
            'Total citations generated'
        )

        # Confidence metrics
        self.response_confidence = Histogram(
            'llm_response_confidence',
            'LLM response confidence scores',
            buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )

        # System health metrics
        self.system_health = Gauge(
            'system_health_status',
            'System health status (1=healthy, 0=unhealthy)'
        )

        # Application info
        self.app_info = Info(
            'solar_pv_llm_ai_app',
            'Application information'
        )
        self.app_info.info({
            'version': '1.0.0',
            'name': 'Solar PV LLM AI'
        })

    def record_query_metrics(
        self,
        latency_seconds: float,
        token_count: int,
        confidence: float,
        hallucination_score: float,
        num_citations: int = 0,
        num_documents: int = 0
    ):
        """Convenience method to record all query-related metrics"""
        self.llm_queries_total.inc()
        self.llm_latency.observe(latency_seconds)
        self.llm_tokens_used.inc(token_count)
        self.response_confidence.observe(confidence)
        self.hallucination_score.set(hallucination_score)

        if hallucination_score > 0.5:
            self.hallucinations_detected.inc()

        if num_citations > 0:
            self.citations_generated.inc(num_citations)

        if num_documents > 0:
            self.rag_documents_retrieved.observe(num_documents)
