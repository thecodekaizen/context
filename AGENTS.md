# Repository working agreements

## Current direction

The user approved planning and implementing the Experimental Investigator on 28 October 2026, after explicitly abandoning SHOWME. Start with [docs/experimental-investigator/README.md](docs/experimental-investigator/README.md), then PRODUCT.md, PROTOCOL.md and IMPLEMENTATION.md in that folder.

The first application is budgeted identification of a two-heater thermal system. Establish prediction quality and comparison evidence before building a product interface. Current implementation includes numerical baselines and an offline-tested Meta decision adapter. Live Meta decisions and a demonstrated advantage remain unvalidated. Preserve hackathon credits: default local runs and pilot dry runs make no API requests; live runs must stay explicitly bounded.

SHOWME, THREAD, the remnant planner and the scientific-scene editor are historical directions. Their locked-product statements do not override the user's subsequent pivot. Previous agreements are preserved in docs/archive/AGENTS_SHOWME_2026-10-28.md for context.

## Engineering and evaluation

- Preserve useful existing code and other agents' uncommitted work. Scope new implementation to experiments/thermal-investigator and docs/experimental-investigator until integration is justified.
- Keep hidden lab configuration and challenge measurements out of agent context. Commit predictions before revealing challenge outputs.
- Compare against strong conventional methods and a direct Meta agent with equivalent tools, observations and budgets. Report failures, sample sizes, costs and uncertainty. Do not tune on sealed evaluation cases.
- Separate simulation, recorded-data replay and actual hardware experiments. No claims of hardware validation or industrial savings from simulation.
- Use Meta substantively; narrative explanations alone do not establish contribution. Models propose structures and decisions; numerical tools enforce constraints and evaluate predictions.
- Treat model output as untrusted data. Start with a bounded declarative grammar, not arbitrary generated code execution.
- Keep secrets and private media out of Git. No BrowserStack code, data, developer QA or employer-adjacent product direction.

## Working style

The user's explicit hackathon exception favors assistant implementation with concise explanations of significant engineering concepts. Do not introduce learning exercises or checkpoints that block authorized work. Explain consequential design choices and evidence as the work progresses.

## Delivery

The supplied hackathon guide requires a public repository by submission, a maximum three-minute demo and clear attribution of work built during the event. The user chose to defer making the repository public until submission; do not change visibility prematurely. Existing authorization to commit and push scoped work remains in effect.
