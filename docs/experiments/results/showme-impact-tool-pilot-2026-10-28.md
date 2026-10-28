# Test a visible wrong-tool selection and retain transient observations

October 28. Public IMPACT v1.1, same downloaded frontal executions as the first pilot. Targeted diagnostic, not an official benchmark or a winning-capability claim.

## Fixed evidence and withheld labels

Example: ER07AD15_Disassembly_A_001 at 62.5–72.5 seconds. Both hands are annotation-normal; tool changes and screw loosening are visible. Control: A_004 at 66.5–71.2 seconds, annotation-normal. Separate attempt: A_004 at 63–71.2 seconds, with an annotated right-hand wrong-tool/temporal event at source 64.5667–66.4667 seconds. The same rectangular tabletop crop was applied to all three inputs (1040x400 at x120/y300, scaled to 1280px width, 10fps, silent). Original videos remain unchanged. Selection/cropping are disclosed preparation, not learned localization.

Official labels were converted to private crop-relative intervals. Neither labels nor tool-error descriptions were sent to either method. There is no explicit recovery label for the later normal screwdriver use; do not score it as annotated recovery. Same participant, different executions; no cross-person generalization claim.

## Initial direct-versus-SHOWME comparison

Same direct baseline prompt as the first pilot; same Muse Spark 1.3 minimal reasoning. A new process was learned only from the selected normal example. The baseline received example plus attempt videos. SHOWME received the distilled process and attempt. The learned process called a tool a red-handled pry tool and grouped other screwdrivers/wrench together; these names and action semantics are hypotheses and conflict with parts of the publisher's action description.

| Output | Direct baseline | SHOWME Observe v5 |
| --- | --- | --- |
| Control issue reports | 0 | 0 |
| Annotated wrong-tool issue reports | 0 | 0 |
| Wrench interaction mentioned | Yes, in uncertainties | No, omitted from event trace |
| Control elapsed | 9.20 s | 12.54 s |
| Attempt elapsed | 11.03 s | 13.20 s |

The direct model described the brief wrench contact but could not distinguish intent to use from repositioning. SHOWME reported only the later red-tool actions. Thus the initial structured process lost a real visible interaction. No advantage over the direct baseline was demonstrated.

One local argument error occurred after the example inference had completed and been saved. It was corrected by reusing that exact saved extraction; no learning inference was repeated. Four comparisons then completed, with time bounds and no retries.

## Narrow engineering fix and follow-up

Observe v6 now explicitly retains transient tool/part interactions, even if absent from the modeled trace or followed by a normal state. Uncertain intent becomes an unclear event with unknown state, rather than a fabricated divergence or omitted observation. This is a generic instruction, not a wrench-specific expected answer.

Held the exact learned process and crops fixed and reran only control/attempt with v6. Both reports passed structural validation. Control still reports no divergence. Attempt now records a silver-wrench contact at crop-relative 2.3 seconds, inside the withheld 1.5667–3.4667-second annotation window, plus a separate tool touch at 3.3 seconds. Both are unclear observations. No divergence or recovery is claimed.

| Follow-up measure | Result |
| --- | --- |
| Retained relevant transient event | Yes, in this one run |
| Diagnosed annotated mistake | No |
| False issue reports on normal control | 0 |
| Control / attempt elapsed | 10.38 / 10.07 seconds |

Temporal overlap of an unclear observation is not a correct mistake diagnosis. This fix restores event recall, not demonstrated intervention usefulness. The single new run cannot establish repeatability or attribute all differences to the prompt rather than sampling variation. The initial direct model already noticed the interaction; SHOWME has not surpassed it.

## Evidence and next gate

Private process, prompts, raw results, labels and hashes are under ignored `.showme-runs/impact-tool-pilot-20261028/` and `.showme-runs/impact-tool-transient-v6-20261028/`. Prepared public research clips are in `/private/tmp/showme-dataset-screen-20261028/tool-neutral-inputs/`. Keep media and answer keys outside Git.

125 local backend checks pass after the prompt-contract regression. Actual procedure correctness remains separate. For a useful intervention, an explicit source requirement or visibly failed use must establish why selecting that tool is wrong; guessing intent from a touch is insufficient. Evaluate whether a clarification at that point would help a learner, and whether it can arrive before the learner has already corrected the selection. Current multi-second analysis does not establish timely live intervention for a sub-two-second event.
