# Pocket Observatory temporal-support gate result

**Overall: INCONCLUSIVE — transport failure on both preregistered calls.** The raw archive and criteria were committed and pushed as `f59f20b` before either call. Each input was attempted once; no retry or prompt change was made.

| Case | Result | Request input SHA-256 |
| --- | --- | --- |
| Full archive | Connection error; no model response or usage returned | `20a622d37e74fc7c61c02030c692217b18b7e43ec5582f84c4bf8ede0f1e3559` |
| Before-release ablation | Connection error; no model response or usage returned | `589d75a6ecd44e54fc3105196f459e7f5c83fbb59c484df79a888225ec01aeca` |

The preregistered criteria therefore cannot be scored. In particular, this is neither evidence that the temporal-support gate passes nor evidence that the model fails the task. Because the client returned no response, there are no response status, evidence-stage labels, citations, or token usage to report. The local usage ledger did not receive a completed-call record; actual provider billing for failed transport attempts is unknown and should be checked in the Meta dashboard.

The experiment remains a controlled synthetic check only. The input hashes above cover the exact raw-only prompt payloads; the repository cache keys additionally include the model, prompt version, reasoning effort, and output cap.
