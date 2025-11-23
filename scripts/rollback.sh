#!/bin/bash
# =============================================================================
# Rollback Script for Solar PV LLM AI
# Rolls back Kubernetes deployments to previous version
# =============================================================================

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-solar-pv-llm-ai}"
DEPLOYMENTS=("backend" "frontend" "celery-worker")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
}

check_namespace() {
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace $NAMESPACE not found."
        exit 1
    fi
}

show_rollout_history() {
    local deployment=$1
    log_info "Rollout history for $deployment:"
    kubectl rollout history deployment/"$deployment" -n "$NAMESPACE"
}

rollback_deployment() {
    local deployment=$1
    local revision=${2:-0}  # 0 means previous revision

    log_info "Rolling back $deployment..."

    if [ "$revision" -eq 0 ]; then
        kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE"
    else
        kubectl rollout undo deployment/"$deployment" --to-revision="$revision" -n "$NAMESPACE"
    fi

    # Wait for rollout to complete
    log_info "Waiting for $deployment rollout to complete..."
    if kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=5m; then
        log_info "$deployment rolled back successfully!"
    else
        log_error "$deployment rollback failed!"
        return 1
    fi
}

verify_deployment() {
    local deployment=$1

    log_info "Verifying $deployment..."

    # Check pod status
    local ready_pods=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
    local desired_pods=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')

    if [ "$ready_pods" = "$desired_pods" ]; then
        log_info "$deployment: $ready_pods/$desired_pods pods ready ✓"
        return 0
    else
        log_error "$deployment: $ready_pods/$desired_pods pods ready ✗"
        return 1
    fi
}

# Main script
main() {
    log_info "Solar PV LLM AI Rollback Script"
    echo "=================================="

    check_kubectl
    check_namespace

    # Parse arguments
    REVISION="${1:-0}"
    SPECIFIC_DEPLOYMENT="${2:-}"

    if [ -n "$SPECIFIC_DEPLOYMENT" ]; then
        DEPLOYMENTS=("$SPECIFIC_DEPLOYMENT")
    fi

    # Show current state
    log_info "Current deployment status:"
    kubectl get deployments -n "$NAMESPACE"
    echo

    # Confirm rollback
    read -p "Do you want to proceed with rollback? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_warn "Rollback cancelled."
        exit 0
    fi

    # Perform rollback
    for deployment in "${DEPLOYMENTS[@]}"; do
        echo
        log_info "Processing $deployment..."

        # Show history
        show_rollout_history "$deployment"
        echo

        # Rollback
        if rollback_deployment "$deployment" "$REVISION"; then
            verify_deployment "$deployment"
        else
            log_error "Failed to rollback $deployment"
            exit 1
        fi
    done

    echo
    log_info "Rollback completed successfully!"
    echo
    log_info "Current deployment status:"
    kubectl get deployments -n "$NAMESPACE"
}

# Run main function
main "$@"
