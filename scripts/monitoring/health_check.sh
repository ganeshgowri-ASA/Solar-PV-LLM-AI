#!/bin/bash

# Solar PV LLM AI - Health Check Script
# This script performs comprehensive health checks on all system components

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_URL="${APP_URL:-http://localhost:8000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
ALERTMANAGER_URL="${ALERTMANAGER_URL:-http://localhost:9093}"

echo "========================================"
echo "Solar PV LLM AI - System Health Check"
echo "========================================"
echo ""

# Function to check HTTP endpoint
check_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}

    echo -n "Checking $name... "

    if response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_status" ]; then
            echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
            return 0
        else
            echo -e "${YELLOW}⚠ WARNING${NC} (HTTP $response, expected $expected_status)"
            return 1
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Connection failed)"
        return 1
    fi
}

# Function to check JSON endpoint
check_json_endpoint() {
    local name=$1
    local url=$2
    local jq_filter=$3
    local expected_value=$4

    echo -n "Checking $name... "

    if response=$(curl -s --max-time 10 "$url" 2>/dev/null); then
        if [ -n "$jq_filter" ]; then
            actual_value=$(echo "$response" | jq -r "$jq_filter" 2>/dev/null)
            if [ "$actual_value" = "$expected_value" ]; then
                echo -e "${GREEN}✓ OK${NC} ($actual_value)"
                return 0
            else
                echo -e "${YELLOW}⚠ WARNING${NC} (Got: $actual_value, Expected: $expected_value)"
                return 1
            fi
        else
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        fi
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

health_issues=0

# Check Main Application
echo "=== Main Application ==="
check_endpoint "Application" "$APP_URL/health" || ((health_issues++))
check_json_endpoint "Application Status" "$APP_URL/health" ".status" "healthy" || ((health_issues++))
check_json_endpoint "LLM Status" "$APP_URL/health" ".llm_status" "ready" || ((health_issues++))
echo ""

# Check Prometheus
echo "=== Prometheus ==="
check_endpoint "Prometheus" "$PROMETHEUS_URL/-/healthy" || ((health_issues++))
check_endpoint "Prometheus Ready" "$PROMETHEUS_URL/-/ready" || ((health_issues++))
echo ""

# Check Grafana
echo "=== Grafana ==="
check_endpoint "Grafana" "$GRAFANA_URL/api/health" || ((health_issues++))
echo ""

# Check AlertManager
echo "=== AlertManager ==="
check_endpoint "AlertManager" "$ALERTMANAGER_URL/-/healthy" || ((health_issues++))
check_endpoint "AlertManager Ready" "$ALERTMANAGER_URL/-/ready" || ((health_issues++))
echo ""

# Check for active alerts
echo "=== Active Alerts ==="
if alerts=$(curl -s "$PROMETHEUS_URL/api/v1/alerts" | jq '.data.alerts | map(select(.state == "firing"))' 2>/dev/null); then
    alert_count=$(echo "$alerts" | jq 'length')

    if [ "$alert_count" -eq 0 ]; then
        echo -e "${GREEN}✓ No active alerts${NC}"
    else
        echo -e "${YELLOW}⚠ $alert_count active alert(s)${NC}"
        echo "$alerts" | jq -r '.[] | "  - \(.labels.alertname): \(.annotations.summary)"' 2>/dev/null
        ((health_issues++))
    fi
else
    echo -e "${RED}✗ Could not fetch alerts${NC}"
    ((health_issues++))
fi
echo ""

# Check key metrics
echo "=== Key Metrics ==="

# Error rate
if error_rate=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=rate(errors_total[5m])" | jq -r '.data.result[0].value[1]' 2>/dev/null); then
    if [ "$error_rate" != "null" ] && [ -n "$error_rate" ]; then
        if (( $(echo "$error_rate < 0.05" | bc -l) )); then
            echo -e "Error Rate: ${GREEN}✓ ${error_rate}/sec${NC}"
        else
            echo -e "Error Rate: ${RED}✗ ${error_rate}/sec (threshold: 0.05/sec)${NC}"
            ((health_issues++))
        fi
    else
        echo "Error Rate: No data"
    fi
else
    echo -e "Error Rate: ${RED}✗ Could not fetch${NC}"
fi

# Hallucination score
if hall_score=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=llm_hallucination_score" | jq -r '.data.result[0].value[1]' 2>/dev/null); then
    if [ "$hall_score" != "null" ] && [ -n "$hall_score" ]; then
        if (( $(echo "$hall_score < 0.5" | bc -l) )); then
            echo -e "Hallucination Score: ${GREEN}✓ ${hall_score}${NC}"
        else
            echo -e "Hallucination Score: ${RED}✗ ${hall_score} (threshold: 0.5)${NC}"
            ((health_issues++))
        fi
    else
        echo "Hallucination Score: No data"
    fi
else
    echo -e "Hallucination Score: ${RED}✗ Could not fetch${NC}"
fi

# API latency
if latency=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=histogram_quantile(0.95,%20rate(http_request_duration_seconds_bucket[5m]))" | jq -r '.data.result[0].value[1]' 2>/dev/null); then
    if [ "$latency" != "null" ] && [ -n "$latency" ]; then
        if (( $(echo "$latency < 2.0" | bc -l) )); then
            echo -e "API P95 Latency: ${GREEN}✓ ${latency}s${NC}"
        else
            echo -e "API P95 Latency: ${YELLOW}⚠ ${latency}s (threshold: 2s)${NC}"
            ((health_issues++))
        fi
    else
        echo "API P95 Latency: No data"
    fi
else
    echo -e "API P95 Latency: ${RED}✗ Could not fetch${NC}"
fi

echo ""
echo "========================================"

# Summary
if [ $health_issues -eq 0 ]; then
    echo -e "${GREEN}✓ All health checks passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $health_issues health issue(s)${NC}"
    exit 1
fi
