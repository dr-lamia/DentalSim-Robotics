# Study execution state machine

DentalSim-Robotics now has one top-level status command.

## Command

```bash
python scripts/status/study_state.py
```

With real artifacts:

```bash
python scripts/status/study_state.py \
  --forced-contact-result results/isaac_runs/<run>/forced_contact_result.json \
  --validated-target-manifest assets/validated_targets/case25/validated_target_manifest.json \
  --teleop-session-manifest results/teleop_sessions/<session>/session_manifest.json \
  --bc-run-manifest results/bc_runs/<run>/bc_run_manifest.json
```

## States

### ENGINEERING_ONLY
No verified real Isaac safety run is available.

Allowed:
- code development
- static scene checks
- mock-data tests
- simulator-independent CI

Not allowed:
- claims of validated safety
- expert teleop collection
- RL execution

### SAFETY_VALIDATED
A real forced-contact negative test has passed.

Allowed:
- expert dentist teleoperation
- safety-only PPO

Still blocked:
- target-dependent geometric rewards
- preparation-accuracy claims

### BC_TRAINING_READY
A validated human dentist teleoperation session is available.

Allowed:
- behavior cloning training/evaluation
- teleoperation analysis

### HYBRID_SAFETY_READY
A valid BC run exists and the safety gate has passed.

Allowed:
- BC-initialized PPO with safety-only rewards

### ACCURACY_RL_READY
Safety is verified and the target is formally validated.

Allowed:
- preparation-accuracy PPO from random initialization
- geometric reward terms

### HYBRID_ACCURACY_READY
Safety is verified, target is validated, and an archived BC model exists.

Allowed:
- BC-initialized PPO with geometric preparation rewards
- full teleop vs BC vs PPO vs hybrid comparison

## Scientific principle

The state machine is deliberately monotonic in evidence. Software existence alone never advances the state. Only the corresponding validated runtime or expert-review artifacts do.
