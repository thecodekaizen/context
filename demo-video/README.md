# CONTEXT narrated demo

A three-minute, 1920×1080, 24 fps video built from actual CONTEXT browser captures.
Eight chapters: problem, local retrieval, alignment, omission reveal, Meta review,
citation inspection, saved evidence and evaluated limits.

## Rebuild on this Mac

Start CONTEXT and prepare a licensed film case with a real saved Meta review.
Pass the case ID from its URL. No provider response or finding is mocked.

```sh
node scripts/capture-demo-chapters.mjs CASE_ID
.venv/bin/python scripts/build-demo.py
cd demo-video
npm run check
npm run render -- --output renders/context-demo-3min.mp4 --fps 24 --quality high --workers 4 --video-frame-format png
```

Run the first two commands from the repository root. The capture script reuses
completed captures; do not mix assets from different cases. To capture a different
case, use a fresh assets directory. The narration builder uses the macOS Samantha
voice locally, normalizes speech loudness and measures every clip's duration.
On another OS, replace the `say` invocation with local speech generation while
preserving the story and per-chapter timing limits.

The composition uses local GSAP and exact font files, downloaded during build.
There are no runtime network dependencies in the rendered composition. The app
capture itself uses local APIs; the Meta chapter opens a saved real response,
clearly labeled as cached rather than fresh inference.

## Verification

`npm run check` checks lint, runtime, layout, motion, contrast and audio. Chapter
review frames are generated with `hyperframes snapshot`. Narrated intro/outro
holds are intentional (`data-hold`). Auxiliary credit/data labels use 16–18 px
at full HD, below the tool's conservative 28 px phone-reading recommendation;
main headlines and narrative copy use 65–110 px and 28 px respectively.

Generated captures, fonts, narration, reports and output MP4 are ignored under
`assets/` and `renders/`. Source, story and scripts are tracked. The final video
uses synthesized narration; no claim is made that it is the creator's own voice.

## Credit

Fonts: Space Grotesk and IBM Plex Mono, downloaded from Google Fonts.
Animation: GSAP 3.14.2. Video authoring/rendering: HyperFrames 0.8.214.
