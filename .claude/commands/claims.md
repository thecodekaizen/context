---
description: Check every claim in README, demo script and story.json against committed results
---
Read README.md, docs/demo-script.md, demo-video/story.json and the results file only.
List each numeric or capability claim with a verdict: SUPPORTED (cite file+line) / UNSUPPORTED / OVERCLAIM.
Flag: "proof", "verdict", "no existing tool", cut-length mismatches (e.g. 4s vs 5s), SAM described as core,
open-weight prize claims if only closed Spark is used. Output a fix list; apply nothing.
