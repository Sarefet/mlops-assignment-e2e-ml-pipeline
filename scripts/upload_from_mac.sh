#!/usr/bin/env bash
# Run on YOUR MAC before the Nebius slot.
set -euo pipefail

BUNDLE="/Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline.tar.gz"

if [[ ! -f "$BUNDLE" ]]; then
  echo "Bundle missing. Creating..."
  "$(dirname "$0")/make_transfer_bundle.sh"
fi

echo ""
echo "=============================================="
echo "  UPLOAD E2E PIPELINE HOMEWORK — run on MAC"
echo "=============================================="
echo ""
read -r -p "Nebius username (e.g. ubuntu): " USER
read -r -p "Nebius IP address: " IP

if [[ -z "$USER" || -z "$IP" ]]; then
  echo "Need username and IP."
  exit 1
fi

scp "$BUNDLE" "${USER}@${IP}:~/"

echo ""
echo "On Nebius (Cursor SSH terminal), paste:"
echo ""
cat <<'PASTE'

cd ~
tar xzf e2e-ml-pipeline.tar.gz
cd e2e-ml-pipeline
chmod +x scripts/*.sh run-airflow-standalone.sh
./scripts/nebius_setup.sh
# Edit .env → set NEBIUS_API_KEY
./scripts/start_mlflow.sh
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
bash run-airflow-standalone.sh

PASTE
echo ""
echo "Port-forward from laptop: 8080 (Airflow), 5000 (MLflow)"
echo ""
