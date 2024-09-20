#!/bin/sh

# Vault secrets directory
VAULT_SECRETS_DIR=/vault/secrets

# Check if the Vault secrets directory exists
if [ -d "${VAULT_SECRETS_DIR}" ]; then
  echo "[entrypoint] Vault secrets directory found: ${VAULT_SECRETS_DIR}"
  echo "[entrypoint] Listing files in ${VAULT_SECRETS_DIR}:"
  ls -l ${VAULT_SECRETS_DIR}

  set -a  # Automatically export all variables
  for i in ${VAULT_SECRETS_DIR}/*.env; do
    if [ -f "${i}" ]; then
      echo "[entrypoint] Sourcing environment variables from ${i}"
      cat "${i}"  # Show the content of the file being sourced
      . "${i}"  # Source each file
    else
      echo "[entrypoint] File ${i} does not exist or is not a regular file"
    fi
  done
  set +a  # Stop automatically exporting variables

  echo "[entrypoint] Environment variables after sourcing:"
  env  # Print all environment variables to see what has been sourced
else
  echo "[entrypoint] Vault secrets directory (${VAULT_SECRETS_DIR}) does not exist. Proceeding without Vault secrets."
fi

# Start the application
echo '[entrypoint] Starting the application...'
exec gunicorn --bind 0.0.0.0:8080 --timeout 60 --workers 3 wsgi:application
