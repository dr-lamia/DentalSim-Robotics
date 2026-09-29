# Study protocol — Phase 1

## Design
Simulation-based technical validation study of an AI policy for autonomous full-coverage crown preparation.

## Index system
A robotic/simulated dental bur controlled by a learned policy in NVIDIA Isaac for Healthcare.

## Reference standard
Expert-designed target preparation mesh for each tooth.

## Experimental units
Independent tooth geometries, split at the tooth/case level. Augmented poses of the same tooth must never cross train/test partitions.

## Proposed data plan
- Development set: 70% of tooth geometries
- Validation set: 15%
- Locked test set: 15%
- Use morphology/pose randomization only inside the assigned split.

For a first feasibility paper, target at least 30 independent held-out tooth geometries and multiple repeated rollouts per tooth. Repeated rollouts improve precision of policy-performance estimates but do not replace independent tooth geometries.

## Intervention arms
Phase 1: autonomous policy only versus expert target geometry.
Phase 2: expert teleop, AI-assisted, and autonomous modes using the same test teeth and metrics.

## Primary outcome
Mean absolute 3D surface deviation (mm) between final and target preparation meshes on the locked test set.

## Secondary outcomes
P95 surface deviation, finish-line deviation, taper error, over-reduction, undercut frequency, minimum pulp distance, adjacent-tooth collisions, smoothness, task completion, and time/steps.

## Safety hierarchy
Safety gates are evaluated before geometric quality. A geometrically accurate preparation is not counted as successful if it collides with an adjacent tooth or breaches the pulp-distance safety threshold.

## Statistical analysis
- Report mean, SD, median, IQR and 95% CI for continuous error metrics.
- Report success rate with binomial 95% CI.
- For repeated rollouts per tooth, use mixed-effects models or cluster-robust inference with tooth as the clustering unit.
- For later paired human/AI comparisons, use paired analysis at tooth level rather than treating repeated rollouts as independent samples.
- Predefine all success thresholds before locked-test evaluation.

## Validation stages
1. Static task/scene contract validation.
2. Simulator launch validation.
3. Forced-contact negative safety test.
4. Expert teleoperation demonstrations.
5. RL dry-run and short smoke training.
6. Full training.
7. Independent randomized checkpoint evaluation.
8. Export and normal workflow policy validation.
9. Locked-test evaluation and statistical analysis.
