# First dentist teleoperation session

## Preconditions

Do not collect an expert demonstration until:
1. the Isaac Case-15 scene launches;
2. the forced protected-contact negative test has passed;
3. reset after the safety test is clean;
4. the HDF5 writer/validator contract is unchanged.

## Preflight

```bash
python scripts/teleop/preflight_expert_session.py \
  --operator-id EXPERT_A \
  --operator-role prosthodontist \
  --scene-id case15_engineering_validation \
  --tooth-id 15 \
  --forced-contact-result results/isaac_runs/<run_id>/forced_contact_result.json
```

The script must return `"ready": true`.

## Session rule

A human dentist/prosthodontist must control the bur.

A scripted controller, mock trajectory, replay, random policy, BC policy or RL policy is **not** an expert demonstration and must not be labelled as one.

## Recording target

For the first session, collect a small engineering dataset:
- 3–5 complete attempts
- same engineering case
- reset between attempts
- retain failures as failures
- never relabel a contact episode as successful

The goal of the first session is to validate the recording pipeline, not to claim learning performance.

## After recording

Validate and archive:

```bash
python scripts/teleop/ingest_expert_session.py \
  --hdf5 path/to/recorded.hdf5 \
  --operator-id EXPERT_A \
  --operator-role prosthodontist \
  --machine-label WORKSTATION_1 \
  --isaac-version ISAAC_VERSION \
  --repo-commit "$(git rev-parse HEAD)" \
  --scene-id case15_engineering_validation \
  --tooth-id 15
```

## Scientific boundary

Case 15 still has no validated preparation target.

Its real dentist trajectories can therefore support:
- motor-control pipeline validation
- safe action-distribution characterization
- behavior-cloning infrastructure
- collision-avoidance pretraining

They cannot establish:
- preparation accuracy
- finish-line accuracy
- taper accuracy
- expert-equivalent autonomous preparation
