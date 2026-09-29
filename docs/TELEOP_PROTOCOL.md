# Expert teleoperation protocol

## Purpose
Collect dentist-generated demonstrations for later imitation learning and policy comparison.

## Current stage
Teleoperation should begin only after:
1. Case-15 Isaac stage launches successfully.
2. Forced protected-contact negative test detects contact and rejects the rollout.
3. Clean reset after contact is verified.
4. All recorded channels pass the HDF5 validator.

## Operator
A real dentist/prosthodontist must perform the trajectory. Automated scripted trajectories are allowed only as engineering controls and must not be labelled expert demonstrations.

## Demonstration unit
One episode = one complete operator attempt from reset to termination.

## Minimum metadata per episode
- episode ID
- tooth/case ID
- operator pseudonym
- mode = teleop
- success flag
- termination reason
- timestamps
- observations
- actions

## Required observations
- bur 7D pose
- bur 6D twist
- target-relative 7D pose
- minimum adjacent-anatomy distance
- protected-contact flag
- previous action

## Required actions
6D relative pose increments:
- dx, dy, dz in metres
- droll, dpitch, dyaw in radians

## Action bounds
- translation: <= 0.25 mm/step
- rotation: <= 2 deg/step

## Safety rule
Any episode containing protected-anatomy contact cannot be labelled successful.

## Engineering Case 15 limitation
Because the exact preparation target has not yet passed segmentation QA:
- Case 15 may be used for motor-control and safety demonstrations.
- It must not be used to train a surface-accuracy objective.
- It must not contribute to manuscript preparation-accuracy endpoints.

## Later validated-tooth collection
Once a validated target mesh is available, demonstrations can additionally include:
- target surface distance
- reduction error
- finish-line error
- taper error
- over-reduction state
