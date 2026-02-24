#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="${NOTE_IMAGES_DIR:-./data/note_images}"
BACKUP_ROOT="${NOTE_IMAGES_BACKUP_DIR:-./data/backups/note_images}"
RETENTION_DAYS="${NOTE_IMAGES_BACKUP_RETENTION_DAYS:-14}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DEST_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p "${DEST_DIR}"

if [[ -d "${SRC_DIR}" ]]; then
  rsync -a --delete "${SRC_DIR}/" "${DEST_DIR}/"
  echo "Backup completed: ${DEST_DIR}"
else
  echo "Source directory does not exist: ${SRC_DIR}" >&2
  exit 1
fi

find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d -mtime +"${RETENTION_DAYS}" -print -exec rm -rf {} +
