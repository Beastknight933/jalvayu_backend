#!/bin/bash

# ==============================================================================
# Climate Digital Twin - Database & Asset Backup Utility
# ==============================================================================
# This script dumps the PostGIS database and backs up the ML models / NetCDF
# datasets to an archive, maintaining a 7-day retention policy.
# ==============================================================================

set -e

# Configuration (Overrides from ENV if available)
DB_USER=${POSTGRES_USER:-postgres}
DB_PASS=${POSTGRES_PASSWORD:-postgres}
DB_NAME=${POSTGRES_DB:-climate_twin}
DB_HOST=${POSTGRES_SERVER:-localhost}
BACKUP_DIR=${BACKUP_DIR:-"/app/data/backups"}
DATA_DIR=${DATA_DIR:-"/app/data"}
RETENTION_DAYS=7

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"
ASSET_BACKUP_FILE="${BACKUP_DIR}/assets_backup_${TIMESTAMP}.tar.gz"

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Starting Backup Process..."

# 1. Database Backup
echo "[$(date)] Dumping database ${DB_NAME} from ${DB_HOST}..."
export PGPASSWORD="${DB_PASS}"
pg_dump -U "${DB_USER}" -h "${DB_HOST}" -d "${DB_NAME}" -F c | gzip > "${DB_BACKUP_FILE}"
echo "[$(date)] Database backup completed: ${DB_BACKUP_FILE}"

# 2. Asset Backup (Models & Processed Data)
# Exclude raw uploads to save space in daily backups
echo "[$(date)] Archiving assets from ${DATA_DIR}..."
tar -czf "${ASSET_BACKUP_FILE}" \
    --exclude="${DATA_DIR}/raw" \
    --exclude="${DATA_DIR}/backups" \
    "${DATA_DIR}/models" "${DATA_DIR}/processed" 2>/dev/null || true
echo "[$(date)] Asset backup completed: ${ASSET_BACKUP_FILE}"

# 3. Retention Policy Cleanup
echo "[$(date)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -name "*.gz" -mtime +${RETENTION_DAYS} -exec rm {} \;
echo "[$(date)] Cleanup finished."

echo "[$(date)] All backup operations completed successfully."
