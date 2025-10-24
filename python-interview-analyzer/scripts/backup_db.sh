#!/bin/bash

# Database Backup Script for Interview Analyzer

set -e

# Configuration
BACKUP_DIR="/var/backups/interview-analyzer"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="interview_db_backup_${TIMESTAMP}.sql"
CONTAINER_NAME="interview-analyzer-postgres"
DB_USER="interview_user"
DB_NAME="interview_db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting database backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}Error: Container $CONTAINER_NAME is not running${NC}"
    exit 1
fi

# Create backup
echo -e "${YELLOW}Creating backup: $BACKUP_FILE${NC}"
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
echo -e "${YELLOW}Compressing backup...${NC}"
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Calculate size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE.gz" | cut -f1)
echo -e "${GREEN}✓ Backup created: $BACKUP_FILE.gz ($BACKUP_SIZE)${NC}"

# Delete backups older than 30 days
echo -e "${YELLOW}Cleaning old backups (older than 30 days)...${NC}"
find "$BACKUP_DIR" -name "interview_db_backup_*.sql.gz" -mtime +30 -delete

# Show remaining backups
echo -e "${GREEN}Backups in $BACKUP_DIR:${NC}"
ls -lh "$BACKUP_DIR"/interview_db_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo -e "${GREEN}✓ Backup completed successfully!${NC}"
