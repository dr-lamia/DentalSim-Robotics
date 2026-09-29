# Batch geometry intake — expert-supervised preparation library

Seven expert-supervised preparation STL sources were processed through the same geometry-only intake.

## What is established

For each file, the repository now records:
- exact SHA-256
- file size
- vertex count
- face count
- connected-component count
- watertight status
- XYZ extents
- surface area

## What is not established

The batch intake does **not** certify that any STL is:
- an isolated single tooth
- a complete preparation target
- free from surrounding scan anatomy
- immediately suitable for preparation-accuracy reward

Those decisions require extraction/inspection.

## Component observations

The two full-coverage sources are each one connected mesh.

Several partial-coverage sources contain a dominant main component plus very small secondary components. For example:
- pin-modified three-quarter: 255,880 of 255,887 faces in the largest component
- seven-eighth: 420,578 of 420,585
- maxillary premolar three-quarter: 351,232 of 351,238

The maxillary molar and anterior three-quarter files also have a dominant primary component, but more small components.

This supports using connected-component cleanup as an engineering preprocessing step, while still requiring visual review afterward.

## Study organization

For the first autonomous preparation benchmark:
- prioritize **full-coverage crown** cases
- use partial-coverage cases as a separate later generalization family

This avoids mixing fundamentally different preparation tasks in the initial BC/PPO comparison.
