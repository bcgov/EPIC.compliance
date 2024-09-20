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

# Sleep to allow manual inspection of environment variables before starting gunicorn
# You can exec into the pod and inspect environment variables
sleep 10000  # You can remove this sleep later after verifying the environment

# Start the application
echo 'starting application'
exec gunicorn --bind 0.0.0.0:8080 --timeout 60 --workers 3 wsgi:application
