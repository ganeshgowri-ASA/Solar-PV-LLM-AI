#!/bin/bash
# =============================================================================
# Load Testing Script using Apache Bench and Locust
# =============================================================================

set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
USERS="${USERS:-100}"
DURATION="${DURATION:-300}"

GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Simple load test with Apache Bench
run_ab_test() {
    log_info "Running Apache Bench test..."

    if ! command -v ab &> /dev/null; then
        log_info "Apache Bench not found, skipping..."
        return
    fi

    ab -n 1000 -c 10 "${API_URL}/health"
}

# Run Locust load test
run_locust_test() {
    log_info "Running Locust load test..."

    if ! command -v locust &> /dev/null; then
        log_info "Locust not found, installing..."
        pip install locust
    fi

    # Create locustfile
    cat > /tmp/locustfile.py << 'EOF'
from locust import HttpUser, task, between

class SolarPVUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(2)
    def ready_check(self):
        self.client.get("/ready")

    @task(1)
    def list_systems(self):
        self.client.get("/api/v1/solar-pv/systems")
EOF

    locust -f /tmp/locustfile.py \
        --host="$API_URL" \
        --users="$USERS" \
        --spawn-rate=10 \
        --run-time="${DURATION}s" \
        --headless \
        --html=/tmp/locust_report.html

    log_info "Load test report saved to /tmp/locust_report.html"
}

main() {
    log_info "Starting load tests against $API_URL"

    run_ab_test
    run_locust_test

    log_info "Load testing completed!"
}

main "$@"
