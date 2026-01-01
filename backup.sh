#!/bin/bash
# OratorHub Backup Script
# Backs up database and uploaded files

# Configuration
BACKUP_DIR="/var/backups/oratorhub"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP_FILE="${BACKUP_DIR}/db_${TIMESTAMP}.sql"
FILES_BACKUP_FILE="${BACKUP_DIR}/files_${TIMESTAMP}.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

echo "OratorHub Backup Started: $(date)"

# Backup PostgreSQL database
if [ "$DATABASE_TYPE" = "postgresql" ]; then
    echo "Backing up PostgreSQL database..."
    docker exec oratorhub-db pg_dump -U oratorhub oratorhub > ${DB_BACKUP_FILE}
    
    if [ $? -eq 0 ]; then
        echo "Database backup successful: ${DB_BACKUP_FILE}"
        gzip ${DB_BACKUP_FILE}
    else
        echo "Database backup failed!"
        exit 1
    fi
fi

# Backup SQLite database
if [ "$DATABASE_TYPE" = "sqlite" ]; then
    echo "Backing up SQLite database..."
    cp oratorhub.db ${BACKUP_DIR}/db_${TIMESTAMP}.db
    
    if [ $? -eq 0 ]; then
        echo "Database backup successful: ${BACKUP_DIR}/db_${TIMESTAMP}.db"
        gzip ${BACKUP_DIR}/db_${TIMESTAMP}.db
    else
        echo "Database backup failed!"
        exit 1
    fi
fi

# Backup uploaded files
echo "Backing up uploaded files..."
tar -czf ${FILES_BACKUP_FILE} uploads/

if [ $? -eq 0 ]; then
    echo "Files backup successful: ${FILES_BACKUP_FILE}"
else
    echo "Files backup failed!"
    exit 1
fi

# Remove old backups
echo "Removing backups older than ${RETENTION_DAYS} days..."
find ${BACKUP_DIR} -type f -mtime +${RETENTION_DAYS} -delete

echo "Backup completed successfully: $(date)"

# Optional: Upload to S3 or other cloud storage
# aws s3 cp ${BACKUP_DIR} s3://your-bucket/oratorhub-backups/ --recursive

exit 0
