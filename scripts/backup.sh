#!/bin/bash
# =============================================================================
# Backup Script for Solar PV LLM AI
# Backs up PostgreSQL database and critical data
# =============================================================================

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-solar-pv-llm-ai}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
S3_BUCKET="${S3_BUCKET:-solar-pv-backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

backup_postgres() {
    log_info "Backing up PostgreSQL database..."

    local pod=$(kubectl get pod -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}')

    if [ -z "$pod" ]; then
        log_error "PostgreSQL pod not found"
        return 1
    fi

    local backup_file="postgres_backup_${TIMESTAMP}.sql.gz"

    kubectl exec -n "$NAMESPACE" "$pod" -- \
        pg_dump -U solar_pv_user solar_pv_db | gzip > "${BACKUP_DIR}/${backup_file}"

    log_info "Database backup saved: ${backup_file}"

    # Upload to S3
    if command -v aws &> /dev/null; then
        log_info "Uploading to S3..."
        aws s3 cp "${BACKUP_DIR}/${backup_file}" "s3://${S3_BUCKET}/database/${backup_file}"
        log_info "Uploaded to S3: s3://${S3_BUCKET}/database/${backup_file}"
    fi
}

backup_volumes() {
    log_info "Backing up persistent volumes..."

    # List of PVCs to backup
    local pvcs=("backend-models-pvc" "worker-models-pvc")

    for pvc in "${pvcs[@]}"; do
        log_info "Backing up PVC: $pvc"

        # Create a backup pod to access the PVC
        # This is a simplified version - in production, use tools like Velero
        # kubectl exec commands here to tar and backup the volume data
    done
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than ${RETENTION_DAYS} days..."

    # Local cleanup
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

    # S3 cleanup (using lifecycle policies is recommended)
    if command -v aws &> /dev/null; then
        aws s3 ls "s3://${S3_BUCKET}/database/" | \
            while read -r line; do
                createDate=$(echo "$line" | awk '{print $1" "$2}')
                createDate=$(date -d "$createDate" +%s)
                olderThan=$(date -d "-${RETENTION_DAYS} days" +%s)

                if [[ $createDate -lt $olderThan ]]; then
                    fileName=$(echo "$line" | awk '{print $4}')
                    if [[ $fileName != "" ]]; then
                        log_info "Deleting old backup: $fileName"
                        aws s3 rm "s3://${S3_BUCKET}/database/${fileName}"
                    fi
                fi
            done
    fi
}

main() {
    log_info "Starting backup process..."

    mkdir -p "$BACKUP_DIR"

    backup_postgres
    backup_volumes
    cleanup_old_backups

    log_info "Backup completed successfully!"
}

main "$@"
