#!/usr/bin/env python3
"""
Solar PV LLM AI - Alert Simulation Script
Simulate various scenarios to trigger alerts for testing
"""

import requests
import time
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
import random


class AlertSimulator:
    """Simulate various alert conditions"""

    def __init__(self, app_url: str = "http://localhost:8000"):
        self.app_url = app_url.rstrip('/')

    def simulate_high_error_rate(self, duration: int = 60, error_rate: float = 0.2):
        """
        Simulate high error rate by making requests that will fail

        Args:
            duration: How long to simulate in seconds
            error_rate: Percentage of requests that should error (0-1)
        """
        print(f"🔥 Simulating high error rate ({error_rate*100}%) for {duration}s...")
        start_time = time.time()
        request_count = 0
        error_count = 0

        while time.time() - start_time < duration:
            # Mix of good and bad requests
            if random.random() < error_rate:
                # Make a request that will fail
                try:
                    requests.post(
                        f"{self.app_url}/api/v1/query",
                        json={"query": ""},  # Empty query should cause error
                        timeout=5
                    )
                except Exception:
                    pass
                error_count += 1
            else:
                # Make a normal request
                try:
                    requests.post(
                        f"{self.app_url}/api/v1/query",
                        json={"query": "What is the efficiency of solar panels?"},
                        timeout=5
                    )
                except Exception:
                    pass

            request_count += 1
            time.sleep(0.1)

        print(f"  Sent {request_count} requests ({error_count} errors)")
        print(f"  Alert 'HighErrorRate' should trigger if error rate exceeds 0.05/sec for 3min")

    def simulate_high_latency(self, duration: int = 60):
        """
        Simulate high latency by making many concurrent requests

        Args:
            duration: How long to simulate in seconds
        """
        print(f"🐌 Simulating high latency for {duration}s...")
        start_time = time.time()
        request_count = 0

        def make_request():
            try:
                requests.post(
                    f"{self.app_url}/api/v1/query",
                    json={
                        "query": "Explain in detail how solar panels work, including the physics behind photovoltaic cells and their efficiency factors.",
                        "temperature": 0.9
                    },
                    timeout=30
                )
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            while time.time() - start_time < duration:
                # Submit multiple requests concurrently
                futures = [executor.submit(make_request) for _ in range(5)]
                request_count += 5
                time.sleep(1)

        print(f"  Sent {request_count} concurrent requests")
        print(f"  Alert 'HighAPILatency' should trigger if P95 latency exceeds 2s for 3min")

    def simulate_high_hallucination(self, duration: int = 60):
        """
        Simulate queries that might trigger high hallucination scores

        Args:
            duration: How long to simulate in seconds
        """
        print(f"🤖 Simulating potential hallucinations for {duration}s...")

        # Queries designed to be ambiguous or ask about things not in context
        tricky_queries = [
            "What is the price of solar panels on Mars?",
            "How do solar panels work underwater?",
            "What happens when you combine solar panels with quantum computing?",
            "Tell me about the secret government solar technology.",
            "What will solar panel efficiency be in year 3000?",
        ]

        start_time = time.time()
        request_count = 0

        while time.time() - start_time < duration:
            query = random.choice(tricky_queries)
            try:
                requests.post(
                    f"{self.app_url}/api/v1/query",
                    json={
                        "query": query,
                        "temperature": 1.0  # Higher temperature increases hallucination risk
                    },
                    timeout=10
                )
            except Exception:
                pass

            request_count += 1
            time.sleep(2)

        print(f"  Sent {request_count} potentially tricky queries")
        print(f"  Alert 'HighHallucinationScore' should trigger if score exceeds 0.5 for 2min")

    def simulate_high_request_rate(self, duration: int = 60, rate: int = 200):
        """
        Simulate high request rate (potential DDoS)

        Args:
            duration: How long to simulate in seconds
            rate: Requests per second to generate
        """
        print(f"📈 Simulating high request rate ({rate} req/sec) for {duration}s...")
        start_time = time.time()
        request_count = 0

        def make_request():
            try:
                requests.get(f"{self.app_url}/health", timeout=5)
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=50) as executor:
            while time.time() - start_time < duration:
                # Submit requests to match desired rate
                batch_size = max(1, rate // 10)  # Batch requests for efficiency
                futures = [executor.submit(make_request) for _ in range(batch_size)]
                request_count += batch_size
                time.sleep(0.1)

        print(f"  Sent approximately {request_count} requests")
        print(f"  Alert 'HighRequestRate' should trigger if rate exceeds 100 req/sec for 5min")

    def simulate_memory_pressure(self):
        """
        Simulate memory pressure (Note: This is limited as it runs client-side)
        """
        print(f"💾 Simulating memory pressure...")
        print(f"  NOTE: This simulation has limited effect as it runs client-side")
        print(f"  To truly test memory alerts, use: stress-ng --vm 4 --vm-bytes 80%")

    def check_alerts(self):
        """Check current firing alerts"""
        try:
            print("\n📋 Checking current alerts...")
            # Query Prometheus for active alerts
            response = requests.get(
                "http://localhost:9090/api/v1/alerts",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                firing_alerts = [
                    alert for alert in data.get('data', {}).get('alerts', [])
                    if alert.get('state') == 'firing'
                ]

                if firing_alerts:
                    print(f"  🚨 {len(firing_alerts)} active alert(s):")
                    for alert in firing_alerts:
                        alert_name = alert.get('labels', {}).get('alertname', 'Unknown')
                        severity = alert.get('labels', {}).get('severity', 'unknown')
                        summary = alert.get('annotations', {}).get('summary', 'No summary')
                        print(f"    - [{severity.upper()}] {alert_name}: {summary}")
                else:
                    print("  ✓ No active alerts")
            else:
                print(f"  ✗ Failed to query Prometheus: HTTP {response.status_code}")

        except Exception as e:
            print(f"  ✗ Error checking alerts: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Simulate alert conditions for testing monitoring system'
    )
    parser.add_argument(
        '--scenario',
        choices=['error-rate', 'latency', 'hallucination', 'request-rate', 'all', 'check'],
        required=True,
        help='Alert scenario to simulate'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=180,
        help='Duration in seconds (default: 180)'
    )
    parser.add_argument(
        '--app-url',
        default='http://localhost:8000',
        help='Application URL (default: http://localhost:8000)'
    )

    args = parser.parse_args()

    simulator = AlertSimulator(app_url=args.app_url)

    print("=" * 60)
    print("Solar PV LLM AI - Alert Simulation")
    print("=" * 60)
    print()

    if args.scenario == 'check':
        simulator.check_alerts()
    elif args.scenario == 'error-rate':
        simulator.simulate_high_error_rate(duration=args.duration)
        time.sleep(5)
        simulator.check_alerts()
    elif args.scenario == 'latency':
        simulator.simulate_high_latency(duration=args.duration)
        time.sleep(5)
        simulator.check_alerts()
    elif args.scenario == 'hallucination':
        simulator.simulate_high_hallucination(duration=args.duration)
        time.sleep(5)
        simulator.check_alerts()
    elif args.scenario == 'request-rate':
        simulator.simulate_high_request_rate(duration=args.duration)
        time.sleep(5)
        simulator.check_alerts()
    elif args.scenario == 'all':
        print("Running all scenarios sequentially...")
        print()
        simulator.simulate_high_error_rate(duration=args.duration // 4)
        time.sleep(10)
        simulator.simulate_high_latency(duration=args.duration // 4)
        time.sleep(10)
        simulator.simulate_high_hallucination(duration=args.duration // 4)
        time.sleep(10)
        simulator.simulate_high_request_rate(duration=args.duration // 4)
        time.sleep(5)
        simulator.check_alerts()

    print()
    print("=" * 60)
    print("Simulation complete!")
    print()
    print("Next steps:")
    print("  1. Check Grafana dashboard: http://localhost:3000")
    print("  2. Check Prometheus alerts: http://localhost:9090/alerts")
    print("  3. Check AlertManager: http://localhost:9093")
    print("  4. Verify alert notifications were sent")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
