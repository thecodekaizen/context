# CONTEXT — See the whole story

## Short description

CONTEXT traces a published video back to a provided original recording, shows
what was omitted or reordered, and lets the viewer inspect the missing footage
alongside a timestamped Meta AI interpretation.

## The problem

Authentic footage can lose meaning through selective editing. A clip can contain
real frames yet omit the event, qualification, or sequence needed to understand
what happened. Frame authenticity alone does not answer the context question.

## What we built

A local investigative workstation with two entry points: compare a known pair,
or upload an edit and search a collection of up to 20 indexed recordings.
FFmpeg probes and decodes the media. A deterministic visual alignment engine
reconstructs source intervals, detects supported omissions/reordering/repetition,
and preserves unresolved spans rather than inventing missing footage.

Two linked video players and source/published timelines make the evidence
inspectable. Clicking an omission plays the original interval. Reports include
source hashes, method, timestamps, confidence scores and limitations. Cases and
valid model interpretations survive a browser reload.

## Meaningful Meta integration

Muse Spark 1.2 receives two bounded video excerpts: original context around a
finding and published context around its edit boundary. Embedded audio is
retained where present. We selected 1.2 because the current Meta video/audio
guide cautions about audio quality on 1.3.

The model returns observations, possible effect on interpretation, and
uncertainty. Observations require citations to supplied clip IDs and local time
ranges; the server validates bounds and maps them back to full media timestamps.
Clicking a citation seeks the original or published player. Model claims remain
separate from measured edits and are not presented as verified facts.

A credentialed request has succeeded using the documented Meta API. Reviews are
cached against evidence hashes, finding, method, model and prompt version.

## Validation

The automated suite covers synthetic edits, a licensed animated production
excerpt, local source retrieval, ambiguous candidates, invalid media, video byte
ranges, model citation validation, audio retention and persistence. Browser tests
exercise the real upload/search/reveal/download/reload flows; provider error and
model presentation tests use explicitly mocked responses. A separate walkthrough
uses a real Meta request, not mocked interpretation.

The production evaluation uses a 24-second *Big Buck Bunny* excerpt with controlled
edits. Supported copy/edit/compression cases produce expected finding types; all
accepted sampled correspondences in those cases are within 0.5 seconds of recipe
ground truth. This small regression set is not a general accuracy claim. Detailed
measurements and reproducible commands are in `docs/evaluation.md`.

## Current limitations

Search is limited to supplied recordings. The current visual matcher does not
reliably support large crops, color changes or speed changes; tested speed changes
remain unresolved. Semantic interpretations may be wrong even with valid citation
bounds. The app is a local prototype, with no public hosting or account system.

## Stack

Python, FastAPI, FFmpeg/FFprobe, NumPy, React, TypeScript, Vite, native HTML video,
Meta Model API, pytest, Playwright.

## Submission assets

- README: reproducible installation, commands and limitations.
- `docs/evaluation.md` and `docs/evaluation.json`: measured evaluation.
- `docs/demo-script.md`: three-minute demonstration plan.
- `docs/film-workstation.png` and `docs/film-review.png`: actual application captures.
- `scripts/record-walkthrough.mjs`: real browser walkthrough recording.
- Local recordings are under ignored `data/walkthrough/`.

Repository publication, hosting, final narrated demo and submission upload have
not been performed. This document is a factual submission draft, not confirmation
of eligibility or submission acceptance.

## Demo source attribution

Film excerpts: *Big Buck Bunny* (2008), (c) copyright 2008, Blender Foundation /
www.bigbuckbunny.org. CC BY 3.0. Trimmed, transcoded, and edited for controlled
evaluation. https://peach.blender.org/about/
