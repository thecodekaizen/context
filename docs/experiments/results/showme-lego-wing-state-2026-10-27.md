# LEGO wing-state exploration — 2026-10-27

## Result and boundary

One browser run reported a detached wing at 14 seconds and a later assembled state at 22 seconds, returning `recovered`. Local frame inspection supports the detachment and reattachment. This is an exploratory state-change signal, **not a passed mistake/orientation benchmark**: removing a component may be intentional disassembly, and the model did not identify a backwards attached wing.

The expert process was already saved in Teach, with 18 instruction-linked steps for LEGO 30727. Observation used Muse Spark 1.3 on separate, silently compressed learner recordings. Raw media remains private and is not committed. No independent answer key, matched correct control, or repeated inference was completed for these runs. Browser output was inspected; this note is a human summary, not a raw provider response or quantitative evaluation.

## Observations

| Recording | Model report | What it supports |
|---|---|---|
| IMG_7668, full clip | No divergence observed; wing attachment around 12 seconds and later reattachment described as consistent | Some assembly actions described; no confirmed orientation judgment |
| IMG_7668, focused segment | No divergence observed; small cockpit piece interpreted as a dome matching step 10; wing round-tile placement unclear | The initial suggestion that this was the wing tile on the cockpit was not confirmed. Object identity remains a model interpretation. |
| IMG_7670, 34 seconds | Assembled at 3 seconds; wing detached at 14 seconds (`divergent`); attached again at 22 seconds (`consistent`); overall `recovered` | Detects coarse attachment-state change and restoration in this one run; does not establish wrong-facing orientation detection or intent |

The IMG_7670 report marks the early construction steps as not shown. This clip does not validate guidance through the entire 68-piece assembly. It also does not demonstrate live intervention: inference ran after clip upload.

## Procedural simulation check

Moving final wing attachment before wing-panel construction stops the alternative sequence at an unobserved transition from the state after step 16. This is a limitation of evidence from one trace. It is not a learned physical impossibility, inferred force, or verified prerequisite. The existing simulator preserves this distinction.

## Representation gap found

Inspection of the saved process shows four object groups: instruction leaflet, loose bricks, cockpit core, and wing assembly. Both wings share one object ID. The last transition has only `completed TIE model as shown` as its postcondition. No state fact explicitly describes inward/outward facing; the one mirrored-wing description has only a parts-presence fact. This representation supports coarse attachment changes but does not provide an explicit orientation target.

Teach’s extraction prompt now asks for supported attachment/relative-facing facts in the existing observable-fact/postcondition fields, distinguishable repeated parts where task-relevant, and uncertainty for unreadable relationships. It uses no LEGO-specific expected mistake. Future learning calls carry `showme-video-analysis-v4`. The saved baseline process is unchanged; no improved extraction or orientation capability is claimed until a fresh source-grounded run is reviewed.

## Engineering follow-up implemented

Recovery validation previously accepted any known consistent event after the **first** difference. That could accept unrelated-object progress or a recovery followed by another divergence. Backend and UI now require evidence covering every reported issue's known affected objects after the **last** reported divergence (including divergent timeline events). Independent recovery events may cover different issues; the UI links to the last required matching event. Reports whose affected object is entirely unknown cannot be marked recovered. Older imported reports without this evidence are labeled unverified in the UI.

This checks chronology and object references, not visual truth or whether the exact relation was repaired. A model can still misidentify a part or claim a consistent state incorrectly. Those claims need independent frame review.

The generic observation prompt now requests visible attachment/orientation/spatial relations only where the process describes them, flags missing orientation rules as a limitation, and distinguishes detachment from intent. It contains no LEGO-specific expected error or timestamps. New observation responses use prompt version `showme-observe-v4`; the baseline runs above predate that prompt and must not be described as validating it.

Do’s reference checklist also stops showing completion ticks derived from simulated state; hypothetical progress must never masquerade as observed learner progress.

A local JSON export preserves the observation and matching process for inspection without another inference. Private exports belong outside Git.

## Remaining gate

Compare held, attached states with a genuinely different orientation against a reviewed model that actually describes the required relationship. Have the human establish the expected distinction before inference; keep labels out of prompts. Run a correct control with the same process/prompt and inspect whether the reported issue and recovery concern the same relationship. Repeat only after preserving these baseline artifacts. No further recording is required to finish the software hardening above.

## Software verification

- 57 SHOWME backend tests pass, including HTTP acceptance of relevant recovery evidence and rejection of unrelated progress using a controlled provider response.
- 21 web tests pass; TypeScript checking passes.
- The browser exported the existing report as local JSON. Local backend validation accepts its 14-second difference and 22-second matching event under the stricter rule.
- A temporary altered local copy that substituted an unrelated object for later consistent events displayed `Recovery unverified` and removed the recovery link. Reimporting the untouched report restored the 22-second recovery link. This tests UI handling, not model perception.
- Browser inspection confirms Do no longer shows a simulated completion tick on its reference steps. No additional Meta inference was used for these checks.
