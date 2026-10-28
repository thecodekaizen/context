# Score the correct-assembly photo control

After both inference batches, the user explicitly confirmed that all five supplied photos depict one correct, unchanged assembly from different angles. The private per-case answer key and scorecard are stored under ignored `.showme-runs/lego-still-joints-v2-20261028/`. They were not sent to the model.

| Measure | Joint v1 | Joint v2 |
| --- | --- | --- |
| Correct-control views | 5 | 5 |
| Reported matches | 3 | 0 |
| False difference reports | 0 | 0 |
| Unclear/abstentions | 2 | 5 |

These are five views of one assembly, not five independent task executions. Zero false alarms does not establish useful discrimination: v2 abstained on every correct view. v1 also contained a source-description error despite an overall matching verdict. Reported verdict agreement and explanation correctness are separate.

No deliberately incorrect assembly or correction appears in this set, so mistake-detection recall and recovery success cannot be measured. Do not present uncertainty on these photos as a missed deliberate error. Existing video removals/reattachments also need independent intent/correctness labels before serving as that benchmark.

Next capability requirement remains one independently labeled, visibly wrong state and its corrected state with the same task, process and prompt. Do not derive the private answer from model output or expose it during inference. No additional calls were made for scoring.
