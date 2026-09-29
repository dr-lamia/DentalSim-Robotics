# First real Isaac execution — operator checklist

This is the first external execution gate. Do not mark it complete from screenshots alone.

## Before running

Record:
- operator pseudonym
- machine label
- Isaac Sim version
- current Git commit SHA
- SHA-256 of the Case-15 asset package
- exact command used

Confirm:
- the repository checkout is clean or any local changes are documented;
- the five Case-15 engineering assets are present;
- no file named "validated target" is being used for Case 15;
- the candidate preparation mesh remains engineering-only.

## Execute

From the repository root:

```bash
bash scripts/isaac/run_case15_safety_smoke.sh \
  /path/to/isaac-sim/python.sh \
  assets/case15 \
  runs/case15_smoke
```

## Do not interpret manually

The run is only considered a pass if:

```bash
python scripts/isaac/verify_forced_contact_result.py \
  runs/case15_smoke/forced_contact_result.json
```

returns exit code 0.

## Ingest the run

```bash
python scripts/isaac/ingest_forced_contact_run.py \
  --result-json runs/case15_smoke/forced_contact_result.json \
  --operator-id OPERATOR_PSEUDONYM \
  --machine-label MACHINE_LABEL \
  --isaac-version ISAAC_VERSION \
  --repo-commit "$(git rev-parse HEAD)" \
  --asset-package /path/to/DentalSim_case15_Isaac_engineering_package.zip \
  --command "bash scripts/isaac/run_case15_safety_smoke.sh ..." 
```

The ingest command independently re-runs the verifier. It refuses to archive a failed result as a pass.

## Archived output

A passing run creates:

`results/isaac_runs/<run_id>/run_manifest.json`

and:

`results/isaac_runs/<run_id>/forced_contact_result.json`

plus:

`results/isaac_runs/latest_pass.json`

## Scientific meaning

A passing run proves:
- the real dental scene can execute in Isaac;
- the protected-contact path is detectable;
- the negative safety rollout is rejected.

It does **not** prove:
- autonomous crown preparation;
- preparation accuracy;
- clinical equivalence;
- target-surface validity.
