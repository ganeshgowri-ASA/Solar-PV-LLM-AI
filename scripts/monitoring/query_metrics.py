#!/usr/bin/env python3
"""
Solar PV LLM AI - Metrics Query Script
Query and display key metrics from Prometheus
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional


class PrometheusClient:
    """Simple Prometheus client for querying metrics"""

    def __init__(self, url: str = "http://localhost:9090"):
        self.url = url.rstrip('/')
        self.api_url = f"{self.url}/api/v1"

    def query(self, query: str) -> Optional[Dict[str, Any]]:
        """Execute a PromQL query"""
        try:
            response = requests.get(
                f"{self.api_url}/query",
                params={'query': query},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'success':
                return data['data']
            else:
                print(f"Query failed: {data}")
                return None

        except Exception as e:
            print(f"Error querying Prometheus: {e}")
            return None

    def query_range(self, query: str, start: str, end: str, step: str = '15s') -> Optional[Dict[str, Any]]:
        """Execute a PromQL range query"""
        try:
            response = requests.get(
                f"{self.api_url}/query_range",
                params={
                    'query': query,
                    'start': start,
                    'end': end,
                    'step': step
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'success':
                return data['data']
            else:
                print(f"Query failed: {data}")
                return None

        except Exception as e:
            print(f"Error querying Prometheus: {e}")
            return None


def format_value(value: float, metric_type: str) -> str:
    """Format metric value based on type"""
    if metric_type == 'percentage':
        return f"{value * 100:.2f}%"
    elif metric_type == 'seconds':
        return f"{value:.3f}s"
    elif metric_type == 'count':
        return f"{int(value)}"
    elif metric_type == 'rate':
        return f"{value:.2f}/sec"
    else:
        return f"{value:.4f}"


def print_metric(name: str, value: Optional[float], metric_type: str = 'float', threshold: Optional[float] = None):
    """Print a metric with formatting and color"""
    if value is None:
        print(f"  {name}: No data")
        return

    formatted_value = format_value(value, metric_type)

    # Color coding based on thresholds
    status = "✓"
    if threshold is not None:
        if metric_type == 'percentage' and value > threshold:
            status = "✗"
        elif metric_type == 'seconds' and value > threshold:
            status = "⚠"

    print(f"  {status} {name}: {formatted_value}")


def main():
    """Main function to query and display metrics"""
    print("=" * 60)
    print("Solar PV LLM AI - Metrics Report")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Initialize Prometheus client
    prom = PrometheusClient()

    # System Health
    print("=== System Health ===")
    result = prom.query('up{job="solar-pv-llm-app"}')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        status = "✓ UP" if value == 1 else "✗ DOWN"
        print(f"  Application Status: {status}")
    else:
        print("  Application Status: Unknown")
    print()

    # Request Metrics
    print("=== Request Metrics (Last 5 minutes) ===")

    # Total request rate
    result = prom.query('sum(rate(http_requests_total[5m]))')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Request Rate", value, 'rate')

    # Error rate
    result = prom.query('rate(errors_total[5m])')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Error Rate", value, 'rate', threshold=0.05)
    else:
        print_metric("Error Rate", None, 'rate')

    # Error percentage
    result = prom.query('rate(errors_total[5m]) / rate(http_requests_total[5m])')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Error Percentage", value, 'percentage', threshold=0.05)
    else:
        print_metric("Error Percentage", None, 'percentage')

    print()

    # Latency Metrics
    print("=== Latency Metrics (Last 5 minutes) ===")

    # API latency percentiles
    for percentile in [50, 95, 99]:
        query = f'histogram_quantile(0.{percentile}, rate(http_request_duration_seconds_bucket[5m]))'
        result = prom.query(query)
        if result and result['result']:
            value = float(result['result'][0]['value'][1])
            threshold = 2.0 if percentile == 95 else 5.0
            print_metric(f"API P{percentile} Latency", value, 'seconds', threshold=threshold)

    # LLM latency percentiles
    for percentile in [50, 95, 99]:
        query = f'histogram_quantile(0.{percentile}, rate(llm_query_duration_seconds_bucket[5m]))'
        result = prom.query(query)
        if result and result['result']:
            value = float(result['result'][0]['value'][1])
            threshold = 5.0 if percentile == 95 else 10.0
            print_metric(f"LLM P{percentile} Latency", value, 'seconds', threshold=threshold)

    print()

    # LLM Quality Metrics
    print("=== LLM Quality Metrics ===")

    # Hallucination score
    result = prom.query('llm_hallucination_score')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Hallucination Score", value, 'float', threshold=0.5)
    else:
        print_metric("Hallucination Score", None, 'float')

    # Hallucination rate
    result = prom.query('rate(llm_hallucinations_detected_total[10m])')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Hallucination Rate", value, 'rate', threshold=0.1)
    else:
        print_metric("Hallucination Rate", None, 'rate')

    # Median confidence
    result = prom.query('histogram_quantile(0.50, rate(llm_response_confidence_bucket[10m]))')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Median Confidence", value, 'float')

    print()

    # LLM Operations
    print("=== LLM Operations (Last 5 minutes) ===")

    # Query rate
    result = prom.query('rate(llm_queries_total[5m])')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("LLM Query Rate", value, 'rate')

    # Token usage rate
    result = prom.query('rate(llm_tokens_total[5m])')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Token Usage Rate", value, 'rate')

    # RAG retrieval rate
    result = prom.query('rate(rag_retrievals_total[5m])')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("RAG Retrieval Rate", value, 'rate')

    print()

    # System Resources
    print("=== System Resources ===")

    # CPU usage
    result = prom.query('100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)')
    if result and result['result']:
        value = float(result['result'][0]['value'][1]) / 100
        print_metric("CPU Usage", value, 'percentage', threshold=0.80)

    # Memory usage
    result = prom.query('(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes')
    if result and result['result']:
        value = float(result['result'][0]['value'][1])
        print_metric("Memory Usage", value, 'percentage', threshold=0.85)

    print()

    # Active Alerts
    print("=== Active Alerts ===")
    result = prom.query('ALERTS{alertstate="firing"}')
    if result and result['result']:
        print(f"  Active alerts: {len(result['result'])}")
        for alert in result['result']:
            alert_name = alert['metric'].get('alertname', 'Unknown')
            severity = alert['metric'].get('severity', 'unknown')
            component = alert['metric'].get('component', 'unknown')
            print(f"    - {alert_name} ({severity}) [{component}]")
    else:
        print("  ✓ No active alerts")

    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
