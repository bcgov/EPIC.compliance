#!/bin/sh

# Vault secrets directory
VAULT_SECRETS_DIR=/vault/secrets

# Check if the Vault secrets directory exists
if [ -d "${VAULT_SECRETS_DIR}" ]; then
  echo "[entrypoint] Vault secrets directory found. Sourcing all files for environment variables."

  set -a  # Automatically export all variables
  for i in ${VAULT_SECRETS_DIR}/*.env; do
    if [ -f "${i}" ]; then
      echo "[entrypoint] Adding environment variables from ${i}"
      . "${i}"  # Source each file
    fi
  done
  set +a  # Stop automatically exporting variables
else
  echo "[entrypoint] Vault secrets directory (${VAULT_SECRETS_DIR}) does not exist. Proceeding without Vault secrets."
fi

# Start the application
echo 'starting application'
exec gunicorn --bind 0.0.0.0:8080 --timeout 60 --workers 3 wsgi:application
