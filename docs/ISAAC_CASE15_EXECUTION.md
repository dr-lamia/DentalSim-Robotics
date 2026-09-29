# NVIDIA Isaac Case-15 executable engineering scene

This directory is the first executable Isaac layer for DentalSim-Robotics.

## What this stage proves

The goal is not autonomous tooth preparation yet. The goal is to prove that the real dental geometry can be imported into Isaac and that the safety loop can detect protected-anatomy contact.

### Engineering acceptance sequence

1. Convert the real Case-15 meshes to USD.
2. Build a 1-metre-unit USD stage.
3. Apply an explicit 0.001 scale to the dental source geometry because the dental coordinates are in millimetres.
4. Create a procedural cylindrical bur with:
   - radius: 0.8 mm
   - active length: 8 mm
5. Make the bur a kinematic rigid body.
6. Make the two neighboring dental ROIs collidable/protected.
7. Keep the prepared-stump candidate non-collidable and explicitly non-ground-truth.
8. Run a deliberate collision into ProtectedSideA.
9. Require non-zero contact records.
10. Reject that rollout.

## Current NVIDIA APIs used

- `from isaacsim import SimulationApp` for standalone Isaac execution.
- `omni.kit.asset_converter` for OBJ/STL/PLY -> USD conversion.
- OpenUSD (`pxr.Usd`, `UsdGeom`, `UsdPhysics`) for stage authoring.
- `isaacsim.sensors.experimental.physics.Contact/ContactSensor` for contact sensing.

The older `isaacsim.sensors.physics` contact sensor API is intentionally not used.

## Commands

From an Isaac Sim installation / Python environment:

```bash
./python.sh scripts/isaac/convert_case15_assets_to_usd.py \
  --input-dir assets/case15 \
  --output-dir assets/case15_usd

./python.sh scripts/isaac/build_case15_stage.py \
  --asset-dir assets/case15_usd \
  --output runs/case15_engineering.usda

./python.sh scripts/isaac/run_forced_contact_test.py \
  --stage runs/case15_engineering.usda \
  --result-json runs/forced_contact_result.json
```

Expected final result:

```text
"contact_detected": true
"safety_rollout_accepted": false
"pass": true
```

A test where the bur reaches protected anatomy and no contact is detected is a **failure**, not a pass.

## Scientific boundary

Case 15 is currently an engineering case. Its prepared-stump candidate did not pass the segmentation QA gate and is therefore not used for:

- preparation-surface reward
- accuracy endpoints
- autonomous clinical success
- manuscript accuracy claims

The forced-contact test is independent of that ground-truth limitation and can be completed now.
