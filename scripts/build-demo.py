"""Generate local narration and a deterministic HyperFrames composition."""

import json
import re
import subprocess
from html import escape
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "demo-video"
ASSETS = PROJECT / "assets"
ASSETS.mkdir(exist_ok=True)
STORY = json.loads((PROJECT / "story.json").read_text())


def ensure_font(family, query, filename):
    target = ASSETS / filename
    if target.exists():
        return
    response = httpx.get(
        "https://fonts.googleapis.com/css2?" + query,
        headers={"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36"},
        timeout=30,
    )
    response.raise_for_status()
    urls = re.findall(r"url\((https://[^)]+)\)", response.text)
    if not urls:
        raise ValueError("Could not resolve " + family)
    font = httpx.get(urls[-1], timeout=30)
    font.raise_for_status()
    target.write_bytes(font.content)


ensure_font(
    "Space Grotesk",
    "family=Space+Grotesk:wght@300..700&display=swap",
    "space-grotesk.woff2",
)
ensure_font(
    "IBM Plex Mono", "family=IBM+Plex+Mono:wght@400&display=swap", "ibm-plex-mono.woff2"
)

if not (ASSETS / "gsap.min.js").exists():
    response = httpx.get(
        "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js", timeout=30
    )
    response.raise_for_status()
    (ASSETS / "gsap.min.js").write_bytes(response.content)


def run(args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def duration(path):
    try:
        data = json.loads(
            run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration:stream=duration",
                    "-of",
                    "json",
                    str(path),
                ]
            )
        )
        if "format" in data and "duration" in data["format"]:
            return float(data["format"]["duration"])
        for s in data.get("streams", []):
            if "duration" in s:
                return float(s["duration"])
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0.0
    return 0.0


for scene in STORY:
    text = ASSETS / (scene["id"] + ".txt")
    text.write_text(scene["narration"])
    aiff = ASSETS / (scene["id"] + ".aiff")
    wav = ASSETS / (scene["id"] + ".wav")

    # Try synthesizing preview track; fall back gracefully to silence if sandboxed or unavailable
    try:
        run(
            [
                "say",
                "-v",
                "Samantha (English (US))",
                "-r",
                "155",
                "-f",
                str(text),
                "-o",
                str(aiff),
            ]
        )
        length = duration(aiff)
    except (OSError, subprocess.SubprocessError):
        length = 0.0

    target_dur = max(1.0, scene["duration"] - 1.8)
    if length <= 0.1:
        # Generate clean silent audio placeholder until builder provides authentic voiceover
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=mono",
                "-t",
                str(target_dur),
                str(wav),
            ]
        )
    else:
        factor = min(max(1.0, length / target_dur), 1.25)
        run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(aiff),
                "-af",
                f"atempo={factor},loudnorm=I=-16:TP=-1.5:LRA=11",
                "-ar",
                "48000",
                str(wav),
            ]
        )
    scene["audio_duration"] = round(duration(wav), 3)
    print(scene["id"], scene["audio_duration"], "seconds", flush=True)

style = """
@font-face{font-family:'Space Grotesk';src:url('assets/space-grotesk.woff2');font-weight:300 700;font-style:normal}@font-face{font-family:'IBM Plex Mono';src:url('assets/ibm-plex-mono.woff2');font-weight:400;font-style:normal}
*{box-sizing:border-box;margin:0}html,body{width:1920px;height:1080px;overflow:hidden;background:#111315;color:#e9e8e3;font-family:'Space Grotesk',sans-serif}#root{position:relative;width:1920px;height:1080px;overflow:hidden}header{position:absolute;left:72px;right:72px;top:42px;display:flex;align-items:center;justify-content:space-between;z-index:20;border-bottom:1px solid #3a4246;padding-bottom:20px}.logo{font-size:32px;font-weight:700;letter-spacing:-1.7px}.logo span{color:#e6a06c}.top-note{font-family:'IBM Plex Mono',monospace;font-size:18px;color:#b8c2c6;letter-spacing:2px}.scene{position:absolute;inset:0;background:#111315}.scene-content{width:100%;height:100%;padding:144px 72px 112px;display:flex;flex-direction:column;gap:24px}.layout{display:flex;align-items:center;gap:48px;width:100%;flex:1;min-height:0}.copy{width:370px;flex-shrink:0}.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:18px;line-height:1.6;color:#93bada;letter-spacing:1px;margin-bottom:26px}.title{font-size:65px;line-height:1.06;font-weight:700;letter-spacing:-2.8px}.summary{font-size:28px;line-height:1.5;font-weight:400;color:#b8c2c6;margin-top:30px}.screen{flex:1;min-width:0;position:relative;border:1px solid #47545c;border-radius:7px;overflow:hidden;background:#111315;aspect-ratio:1.6;max-height:100%}.screen video,.screen img{display:block;width:100%;height:100%;object-fit:contain}.scene-note{font-family:'IBM Plex Mono',monospace;font-size:17px;color:#e6a06c;letter-spacing:.5px;line-height:1.6}.intro .copy{width:510px}.intro .title{font-size:89px;letter-spacing:-4px}.intro .screen{transform:none}footer{position:absolute;bottom:28px;left:72px;right:72px;z-index:20;border-top:1px solid #3a4246;padding-top:16px;display:flex;justify-content:space-between;gap:36px;font-size:16px;color:#b8c2c6;line-height:1.5}.footer-brand{white-space:nowrap;color:#93bada}.outro-layout{display:flex;flex:1;gap:80px;align-items:center}.outro-title{font-size:110px;letter-spacing:-5px;line-height:1.05;max-width:800px}.outro-left{flex:1}.metrics{width:610px;display:flex;flex-direction:column;gap:22px}.metric{border-bottom:1px solid #47545c;padding-bottom:22px;display:flex;align-items:baseline;gap:25px}.metric strong{font-size:82px;font-weight:700;color:#e6a06c}.metric span{font-size:26px;color:#b8c2c6}.limit{font-size:22px;line-height:1.7;color:#b8c2c6}.rule{height:2px;background:#e6a06c;transform-origin:left center;width:100%}.outro .summary{max-width:730px}
"""
parts = [
    '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920,height=1080"><script src="assets/gsap.min.js"></script><style>'
    + style
    + '</style></head><body><div id="root" data-composition-id="context-demo" data-start="0" data-duration="180" data-width="1920" data-height="1080" data-fps="24"><header><div class="logo">CONTEXT<span>.</span></div><div class="top-note">SEE THE WHOLE STORY / WORKING PRODUCT DEMO</div></header>'
]
for i, scene in enumerate(STORY):
    sid = scene["id"]
    start = scene["start"]
    length = min(scene["duration"] + 0.5, 180 - start)
    is_last = i == len(STORY) - 1
    hold = " data-hold" if sid == "intro" or is_last else ""
    common = f'<div id="scene-{sid}" class="scene {sid}" style="z-index:{i + 1};opacity:{1 if i == 0 else 0}"><div class="scene-content"{hold}>'
    if is_last:
        body = f"""<div class="eyebrow">{escape(scene["eyebrow"])}</div><div class="outro-layout"><div class="outro-left"><h1 class="outro-title">{escape(scene["title"])}</h1><p class="summary">Inspect the evidence. Preserve the uncertainty.</p></div><div class="metrics"><div class="metric"><strong>100%</strong><span>eval recall</span></div><div class="metric"><strong>0.0s</strong><span>boundary error</span></div><div class="metric"><strong>132</strong><span>backend tests</span></div><p class="limit">30-edit benchmark, deterministic audio/visual aligner, SAM 3.1 crop detector, and bounded Meta Muse Spark review.</p></div></div><div class="rule"></div><div class="scene-note">CONTEXT / META GLOBAL AI DEVELOPER HACKATHON 2026</div>"""
    else:
        media = (
            f'<img id="media-{sid}" class="clip" src="assets/hero.png" data-start="{start}" data-duration="{length}" data-track-index="{i % 2}">'
            if sid == "intro"
            else f'<video id="media-{sid}" class="clip" src="assets/{sid}.mp4" muted playsinline data-start="{start}" data-duration="{length}" data-track-index="{i % 2}"></video>'
        )
        body = (
            f'<div class="layout"><aside class="copy"><div class="eyebrow">{escape(scene["eyebrow"])}</div><h1 class="title">{escape(scene["title"])}</h1><p class="summary">{escape(scene["summary"])}</p></aside><div class="screen">{media}</div></div><div class="rule"></div><div class="scene-note">'
            + (
                "ACTUAL APPLICATION CAPTURE / GROUNDED MULTIMODAL INTELLIGENCE"
                if sid != "intro"
                else "SINGLE-VIDEO WORKSTATION / EVIDENCE BEFORE INTERPRETATION"
            )
            + "</div>"
        )
    parts.append(common + body + "</div></div>")
    parts.append(
        f'<audio id="voice-{sid}" src="assets/{sid}.wav" data-start="{start + 0.8}" data-duration="{scene["audio_duration"]}" data-track-index="3" data-volume="1"></audio>'
    )
parts.append(
    '<footer><span class="footer-brand">CONTEXT · SEE THE WHOLE STORY</span><span>Meta Global AI Developer Hackathon 2026 · Multimodal Video Intelligence Studio · Push the Frontier</span></footer></div><script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});'
)
for i, scene in enumerate(STORY):
    sid = scene["id"]
    t = scene["start"]
    is_last = i == len(STORY) - 1
    if i > 0:
        parts.append(f'tl.set("#scene-{STORY[i - 1]["id"]}",{{opacity:0}},{t + 0.46});')
        parts.append(
            f'tl.to("#scene-{sid}",{{opacity:1,duration:.45,ease:"sine.inOut"}},{t});'
        )
    entries = [
        (".eyebrow", 0.2, "power2.out", "x"),
        (".outro-title" if is_last else ".title", 0.35, "power3.out", "y"),
        (".summary", 0.5, "sine.out", "y"),
        (".metrics" if is_last else ".screen", 0.45, "power1.out", "y"),
        (".scene-note", 0.65, "power2.out", "x"),
    ]
    for selector, offset, ease, axis in entries:
        parts.append(
            f'tl.from("#scene-{sid} {selector.replace(", ", ", #scene-" + sid + " ")}",{{opacity:0,{axis}:18,duration:.55,ease:"{ease}"}},{t + offset});'
        )
    parts.append(
        f'tl.from("#scene-{sid} .rule",{{scaleX:0,duration:.7,ease:"power3.out"}},{t + 0.4});'
    )
parts.append(
    f'tl.to("#scene-{STORY[-1]["id"]} .scene-content",{{opacity:0,duration:.65,ease:"sine.inOut"}},179.3);window.__timelines["context-demo"]=tl;</script></body></html>'
)
(PROJECT / "index.html").write_text("".join(parts))
(ASSETS / "narration-timing.json").write_text(json.dumps(STORY, indent=2))
print("Composition written: 180 seconds, 1920x1080, 24fps")
