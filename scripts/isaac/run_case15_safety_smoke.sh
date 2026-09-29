#!/usr/bin/env bash
set -euo pipefail

# One-command Isaac safety smoke test for DentalSim-Robotics.
#
# Run from the repository root with Isaac Sim's Python launcher:
#   bash scripts/isaac/run_case15_safety_smoke.sh /path/to/isaac/python.sh assets/case15 runs/case15_smoke
#
# The script refuses to claim success unless the forced-contact JSON records
# both contact_detected=true and pass=true.

ISAAC_PYTHON="${1:-}"
ASSET_DIR="${2:-assets/case15}"
RUN_DIR="${3:-runs/case15_smoke}"

if [[ -z "$ISAAC_PYTHON" ]]; then
  echo "ERROR: path to Isaac Sim python.sh is required" >&2
  exit 2
fi

if [[ ! -x "$ISAAC_PYTHON" ]]; then
  echo "ERROR: Isaac Python launcher is not executable: $ISAAC_PYTHON" >&2
  exit 2
fi

required=(
  "fdi15_anatomical_start_aligned.stl"
  "prepared_stump_candidate_NOT_GROUND_TRUTH.stl"
  "protected_side_A_roi.ply"
  "protected_side_B_roi.ply"
  "fdi15_design_scan_frame.stl"
)

for name in "${required[@]}"; do
  if [[ ! -f "$ASSET_DIR/$name" ]]; then
    echo "ERROR: missing asset: $ASSET_DIR/$name" >&2
    exit 3
  fi
done

mkdir -p "$RUN_DIR/usd"

echo "[1/4] Convert dental meshes to USD"
"$ISAAC_PYTHON" scripts/isaac/convert_case15_assets_to_usd.py   --input-dir "$ASSET_DIR"   --output-dir "$RUN_DIR/usd"

echo "[2/4] Build Case-15 engineering scene"
"$ISAAC_PYTHON" scripts/isaac/build_case15_stage.py   --asset-dir "$RUN_DIR/usd"   --output "$RUN_DIR/case15_engineering.usda"

echo "[3/4] Run forced protected-contact negative test"
"$ISAAC_PYTHON" scripts/isaac/run_forced_contact_test.py   --stage "$RUN_DIR/case15_engineering.usda"   --result-json "$RUN_DIR/forced_contact_result.json"

echo "[4/4] Verify safety result"
python scripts/isaac/verify_forced_contact_result.py   "$RUN_DIR/forced_contact_result.json"

echo
echo "STATUS: ISAAC SAFETY SMOKE TEST PASSED"
echo
echo "Next:"
echo "python scripts/status/check_readiness.py \\"
echo "  --forced-contact-result $RUN_DIR/forced_contact_result.json"
