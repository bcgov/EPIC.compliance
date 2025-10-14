#!/bin/sh

# Vault secrets directory
VAULT_SECRETS_DIR=/vault/secrets

# Check if the Vault secrets directory exists
if [ -d "${VAULT_SECRETS_DIR}" ]; then
  echo "[entrypoint] Vault secrets directory found: ${VAULT_SECRETS_DIR}"

  # List files in the Vault secrets directory for debugging
  echo "[entrypoint] Listing files in ${VAULT_SECRETS_DIR}:"
  ls -l ${VAULT_SECRETS_DIR}

  set -a  # Automatically export all variables
  for i in ${VAULT_SECRETS_DIR}/*.env; do
    if [ -f "${i}" ]; then
      echo "[entrypoint] Sourcing environment variables from ${i}"
      . "${i}"  # Source each file
    fi
  done
  set +a  # Stop automatically exporting variables

  # Print the environment variables for debugging
  echo "[entrypoint] Environment variables after sourcing:"
  env | grep 'app_name\|secret_key'

else
  echo "[entrypoint] Vault secrets directory (${VAULT_SECRETS_DIR}) does not exist. Proceeding without Vault secrets."
fi

# Get worker configuration from environment variables with defaults
GUNICORN_WORKERS=${GUNICORN_WORKERS:-2}
GUNICORN_WORKER_THREADS=${GUNICORN_WORKER_THREADS:-2}
GUNICORN_WORKER_CONNECTIONS=${GUNICORN_WORKER_CONNECTIONS:-250}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-60}

echo "[entrypoint] Starting application with:"
echo "  - Workers: $GUNICORN_WORKERS"
echo "  - Worker Connections: $GUNICORN_WORKER_CONNECTIONS"
echo "  - Timeout: $GUNICORN_TIMEOUT"
echo "  - Worker Threads: $GUNICORN_WORKER_THREADS"

gunicorn --bind 0.0.0.0:8080 \
  --timeout $GUNICORN_TIMEOUT \
  --workers $GUNICORN_WORKERS \
  --threads $GUNICORN_WORKER_THREADS \
  --worker-connections=$GUNICORN_WORKER_CONNECTIONS \
  wsgi:application
