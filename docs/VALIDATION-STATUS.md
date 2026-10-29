# CONTEXT validation status — 29 October 2026

Implementation resumed under Codex ownership at the user's explicit request. No publication, release, submission, or demo production is authorized by this handover.

## Delivered safeguards

- Reject invalid, out-of-range, boolean, or missing evidence timestamps instead of clamping or inventing them.
- Reject audio/speech evidence on silent input rather than relabeling it as visual evidence.
- Reject invented supplied-caption text; retain the actual input as a separately attributed claim.
- Remove unknown/duplicate claim findings; downgrade unsupported verdicts; derive the overview from retained findings.
- Revalidate saved dossiers from original provider receipts on read. Incomplete or invalid saved reports fail closed.
- Show validation exclusions and fix observation-to-video seeking when the player is initially unmounted.
- Analyze up to 180 seconds (previously 90).

## Actual media diagnostic

The runner sends actual reference/edit videos to Muse Spark 1.2. Filenames, edit recipes, labels, authored transcripts, context notes, and class counts are withheld from model requests. Full receipts and hashes are saved locally in ignored data/smoke_test.

| Inherited case | Blind model classification | All-boundary alignment |
| --- | --- | --- |
| Honest shortening 1 | Not misleading | Pass |
| Honest shortening 2 | Not misleading | Pass |
| Alleged deceptive omission | Not misleading | Pass |
| Reorder | Misleading | Fail: 2.75s unsupported gap at one boundary |
| Alleged reversed claim | Not misleading | Pass |

This is **not a passed gate**, nor a valid 3/5 semantic accuracy measurement. Official NASA captions contradict the authored rationale for the omission/reversal labels: the omitted section does not contain the alleged uncrewed qualification and the supposed reversal retains an ordinary introduction. Do not pivot products on a score against these invalid labels.

## Remaining gate

Prepare and preregister five defensible edits from a real talk with independently established wording and meaning. Include two harmless shortenings, an actual deceptive omission, meaningful reorder, and actual claim reversal. Check every piece's start/end against alignment, requiring supported matching within two seconds. Require at least four correct semantic decisions and neither harmless edit accused. Preserve receipts and report failures without changing labels after scores are known.

An alternative official NASA source, “To the Moon and Back: The Journey of Artemis I,” has explicit uncrewed/no-human wording at 02:15–02:21. Captions and catalog are saved in data/gate-source-review. It is only a candidate; it has not yet supplied a validated new five-edit dataset.

## Current product limits

The saved single-input NASA investigation demonstrates real Meta video analysis, live provider search receipts, fetched primary sources and a source-linked contradiction of a deliberately false supplied caption. It does not establish exact uploaded-footage origin, authenticity, general accuracy, open-web source-video retrieval performance, or superiority over EVID-Bench. Voice word timestamps and SAM are not integrated. Source retrieval is limited by the configured host allowlist.
