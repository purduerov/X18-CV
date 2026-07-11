

set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

# --- config ------------------------------------------------------------------
PY="${PYTHON:-python3}"
VENV="$ROOT/venv"
WHEELHOUSE="$ROOT/offline_packages/wheelhouse"

# CPU-only PyTorch index (works for both Linux and Windows x86-64).
TORCH_CPU_INDEX="https://download.pytorch.org/whl/cpu"

# torch/torchvision come from the CPU index above; everything else from PyPI.
TORCH_PKGS=(torch torchvision)
PY_PKGS=(numpy opencv-python pillow boto3 requests ultralytics)

# Node apps that need their dependencies installed.
NODE_APPS=(realityCapture model_viewer)

MODE="${1:-offline}"

# --- helpers -----------------------------------------------------------------
activate_venv() {
  if [ -d "$VENV/bin" ]; then
    source "$VENV/bin/activate"        # Linux / macOS
  else
    source "$VENV/Scripts/activate"    # Windows (Git Bash)
  fi
}

# =============================================================================
# PHASE 1: download (ONLINE) — run on a machine matching the competition box
# =============================================================================
if [ "$MODE" = "download" ]; then
  echo ">>> PREP MODE (needs internet). Run this on the x86-64 competition machine."
  mkdir -p "$WHEELHOUSE"

  echo ">>> Creating venv for the download..."
  "$PY" -m venv "$VENV"
  activate_venv

  echo ">>> Upgrading pip tooling..."
  python -m pip install --upgrade pip wheel setuptools

  echo ">>> Caching pip/wheel/setuptools so even bootstrap works offline..."
  python -m pip download pip wheel setuptools -d "$WHEELHOUSE"

  echo ">>> Downloading CPU-only torch + torchvision..."
  python -m pip download "${TORCH_PKGS[@]}" \
    --index-url "$TORCH_CPU_INDEX" -d "$WHEELHOUSE"

  echo ">>> Downloading remaining Python packages (deps auto-resolved)..."
  python -m pip download "${PY_PKGS[@]}" \
    --extra-index-url "$TORCH_CPU_INDEX" -d "$WHEELHOUSE"

  echo ">>> Installing Node dependencies for: ${NODE_APPS[*]}"
  for app in "${NODE_APPS[@]}"; do
    if [ -f "$ROOT/$app/package.json" ]; then
      echo "    npm install in $app ..."
      ( cd "$ROOT/$app" && npm install )
    fi
  done

  echo ""
  echo ">>> PREP COMPLETE."
  echo "    Python wheels cached in: $WHEELHOUSE"
  echo "    node_modules built in:   ${NODE_APPS[*]}"
  echo "    Do NOT delete venv/, offline_packages/, or */node_modules before the competition."
  echo "    On competition day (no internet) just run:  ./start-cv.sh"
  exit 0
fi

echo ">>> OFFLINE INSTALL MODE."

if [ ! -d "$WHEELHOUSE" ] || [ -z "$(ls -A "$WHEELHOUSE" 2>/dev/null)" ]; then
  echo "!!! No wheels found in $WHEELHOUSE"
  echo "!!! You must run './start-cv.sh download' first (WITH internet, on this machine)."
  exit 1
fi

echo ">>> Creating venv..."
"$PY" -m venv "$VENV"
activate_venv

echo ">>> Upgrading pip tooling from local wheelhouse (no network)..."
python -m pip install --no-index --find-links "$WHEELHOUSE" --upgrade pip wheel setuptools

echo ">>> Installing Python dependencies from local wheelhouse (no network)..."
python -m pip install --no-index --find-links "$WHEELHOUSE" \
  "${TORCH_PKGS[@]}" "${PY_PKGS[@]}"

echo ">>> Setting up Node dependencies (offline)..."
for app in "${NODE_APPS[@]}"; do
  if [ -f "$ROOT/$app/package.json" ]; then
    if [ -d "$ROOT/$app/node_modules" ] && [ -n "$(ls -A "$ROOT/$app/node_modules" 2>/dev/null)" ]; then
      echo "    $app: node_modules already present — OK."
    else
      echo "    $app: node_modules missing — trying offline install from npm cache..."
      ( cd "$ROOT/$app" && npm ci --offline --prefer-offline ) || {
        echo "!!! $app has no node_modules and npm cache is empty."
        echo "!!! Re-run './start-cv.sh download' with internet to build node_modules."
        exit 1
      }
    fi
  fi
done

echo ""
echo ">>> SETUP COMPLETE (offline)."
echo "    Activate with:  source venv/bin/activate   (or venv/Scripts/activate on Windows)"
echo "    Node apps run from their existing node_modules (e.g. cd realityCapture && npm start)."
