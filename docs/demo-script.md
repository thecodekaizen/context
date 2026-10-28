# Three-minute demo script

Use actual analysis and a real or valid cached Meta review. Keep the network
wait visible or clearly disclose a jump cut. Do not substitute authored model
answers. The film example is controlled editing of licensed production footage,
not a claim of discovering real misinformation.

| Time | Show | Narration |
| --- | --- | --- |
| 0:00–0:20 | CONTEXT workspace and two videos | “A video can contain authentic frames and still leave out part of the story. CONTEXT helps us inspect what was removed and how the sequence changed.” |
| 0:20–0:45 | Add an original to the local collection; search using its edited clip | “We start with a collection of provided source recordings. CONTEXT indexes them once and compares the published clip against their visual sequences. It makes no claim to search the whole internet.” |
| 0:45–1:10 | Selected source, coverage, original/published tracks | “The alignment maps the edit back to the original. Blue spans are supported correspondences. The highlighted source interval sits outside the published sequence. Unresolved frames remain uncertain.” |
| 1:10–1:35 | Click an omission and let its full interval play | “One click reveals the actual missing footage. The source player starts at the detected timestamp, while the published clip stays available for comparison. The visual evidence comes first.” |
| 1:35–2:05 | Review with Meta AI; observations and citations | “Muse Spark reviews bounded excerpts from both versions, including available audio. Its interpretation is separate from deterministic edit detection. Every observation must reference a supplied clip and an in-range timestamp.” |
| 2:05–2:25 | Click a model citation; inspect uncertainty | “Clicking a citation takes us back to the footage. These timestamps are checked, but that does not make the model’s interpretation automatically true. Uncertainty remains visible.” |
| 2:25–2:45 | Download evidence JSON; reload the saved case | “The report records source hashes, intervals, method and limitations. Investigations persist, and model reviews are reused only when their evidence identity still matches.” |
| 2:45–3:00 | Evaluation results, final workspace | “Controlled tests found and fixed false omissions from ambiguous scenes and false one-speed mappings. CONTEXT helps people inspect an edit’s evidence before deciding what it means. See the whole story.” |

## Preparation

1. Run the README setup and start the local server with `.env` loaded.
2. Run the optional Blender evaluation download so the film example is available.
3. Index `data/evaluation/source.mp4` once, then search with
   `data/evaluation/omission.mp4`. These are a controlled six-second omission.
4. For visible source attribution, also open **Explore licensed film case**.
   Its provenance panel includes title, license, modifications and credit.
5. Generate a real Meta review. Confirm citations and uncertainty. Cached review
   reuse is acceptable when clearly explained; never label it a fresh inference.
6. Record at 1440×1000 or similar. Keep the cursor and relevant controls visible.
7. Include the film attribution in the final video credits and description.

## Publication credit

Film excerpts from *Big Buck Bunny* (2008), (c) copyright 2008, Blender Foundation /
www.bigbuckbunny.org. Licensed CC BY 3.0. Excerpts trimmed, transcoded and edited
for this controlled demonstration. Source: https://peach.blender.org/about/

The raw QA walkthrough is silent and is not the final narrated submission video.
