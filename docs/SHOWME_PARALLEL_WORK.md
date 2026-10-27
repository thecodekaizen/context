# SHOWME parallel work — October 28

## Objective

Finish the Teach → Do → Simulate product alongside the perception experiment. Product completeness and capability validation are separate gates; neither substitutes for the other.

## Ownership

| Workstream | Owns | Deliverable |
| --- | --- | --- |
| Validation agent | backend/showme, backend/tests, docs/experiments | Evidence-based comparison improvements, local checks, preserved failures, exact next experiment |
| Product agent | apps/web | Working task interactions using the existing Skill Model and API contracts, verification |
| Integration lead | Shared plans, review, Git | Reconcile changes, verify contracts, commit and push |

Agents must coordinate a contract change before editing another workstream's files. No parallel Git commits. The integration lead stages explicit files after review.

## Shared contract

- Teach creates one reviewed Skill Model; Do and Simulate consume that model.
- Raw observations, inferred state, simulation output, and human evaluation labels remain separate.
- An unsupported relationship stays unknown. A model response is not validation evidence merely because its format is valid.
- No fake detection, invented geometry, or scripted recovery presented as learned behavior.
- Existing private clips and run artifacts stay out of Git.
- New paid calls follow the applicable payload approval requirements; local product work continues independently.

## Completion gates

1. Product: the task session can move through Teach, Do, recovery inspection, and Simulate without losing the reviewed skill or confusing simulated progress with actual observations.
2. Capability: the same process and comparison setup accepts correct execution, identifies a real visible mistake, and recognizes its correction, with independently reviewed evidence and repeatability.
3. Submission: reproducible setup, truthful claims, accessible public repository and three-minute demo, submitted before November 4 at 9 PM ET.

## Current status

Both workstreams dispatched. The latest orientation experiment remains unsuccessful; no new capability claim is established by starting parallel work.
