"""Deterministic crop and visual reframe detection with SAM 3.1 integration."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .media import probe, run


@dataclass
class CropBox:
    x: int
    y: int
    width: int
    height: int


@dataclass
class MarginRegion:
    name: str
    x: int
    y: int
    width: int
    height: int


@dataclass
class CropDetectionResult:
    detected: bool
    confidence: float
    crop_box: CropBox | None
    source_resolution: tuple[int, int]
    edited_resolution: tuple[int, int]
    area_retained_fraction: float
    area_omitted_fraction: float
    omitted_margins: list[MarginRegion]
    explanation: str
    sam_segmentation: dict[str, Any] | None = None


def extract_frame(video_path: Path, timestamp: float = 2.0) -> np.ndarray:
    """Extract a single frame as RGB numpy array using ffmpeg."""
    raw = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            str(timestamp),
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "pipe:1",
        ]
    )
    info = probe(video_path)
    w, h = info["width"], info["height"]
    expected_len = w * h * 3
    if len(raw) < expected_len:
        raise ValueError(
            f"Extracted frame bytes ({len(raw)}) shorter than expected ({expected_len})"
        )
    return np.frombuffer(raw[:expected_len], dtype=np.uint8).reshape((h, w, 3))


def detect_crop_in_frames(
    source_rgb: np.ndarray,
    edited_rgb: np.ndarray,
    min_confidence: float = 0.80,
) -> CropDetectionResult:
    """Detect spatial sub-region crop/reframe from source to edited frame."""
    s_h, s_w = source_rgb.shape[:2]
    e_h, e_w = edited_rgb.shape[:2]

    source_gray = cv2.cvtColor(source_rgb, cv2.COLOR_RGB2GRAY)
    edited_gray = cv2.cvtColor(edited_rgb, cv2.COLOR_RGB2GRAY)

    best_score = -1.0
    best_box = None

    # Test exact scale first (unscaled crop)
    if e_w <= s_w and e_h <= s_h:
        res = cv2.matchTemplate(source_gray, edited_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val > best_score:
            best_score = float(max_val)
            best_box = CropBox(
                x=int(max_loc[0]), y=int(max_loc[1]), width=e_w, height=e_h
            )

    # Multi-scale search: test both source-aspect crops and edited-aspect crops
    scales = np.linspace(0.4, 1.0, 19)
    aspect_ratios = [s_h / max(1, s_w), e_h / max(1, e_w)]

    for aspect in aspect_ratios:
        for scale in scales:
            target_w = int(s_w * scale)
            target_h = int(target_w * aspect)
            if target_w >= s_w and target_h >= s_h:
                continue
            if target_w < 64 or target_h < 64 or target_w > s_w or target_h > s_h:
                continue

            resized_template = cv2.resize(
                edited_gray, (target_w, target_h), interpolation=cv2.INTER_AREA
            )
            res = cv2.matchTemplate(source_gray, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_score:
                best_score = float(max_val)
                best_box = CropBox(
                    x=int(max_loc[0]),
                    y=int(max_loc[1]),
                    width=target_w,
                    height=target_h,
                )

    total_source_area = s_w * s_h
    if best_box is not None and best_score >= min_confidence:
        box_area = best_box.width * best_box.height
        retained_frac = box_area / total_source_area
        is_crop = retained_frac < 0.96

        margins: list[MarginRegion] = []
        if is_crop:
            # Top margin
            if best_box.y > 5:
                margins.append(MarginRegion("top", 0, 0, s_w, best_box.y))
            # Bottom margin
            bottom_h = s_h - (best_box.y + best_box.height)
            if bottom_h > 5:
                margins.append(
                    MarginRegion(
                        "bottom", 0, best_box.y + best_box.height, s_w, bottom_h
                    )
                )
            # Left margin
            if best_box.x > 5:
                margins.append(
                    MarginRegion("left", 0, best_box.y, best_box.x, best_box.height)
                )
            # Right margin
            right_w = s_w - (best_box.x + best_box.width)
            if right_w > 5:
                margins.append(
                    MarginRegion(
                        "right",
                        best_box.x + best_box.width,
                        best_box.y,
                        right_w,
                        best_box.height,
                    )
                )

        explanation = (
            f"Detected spatial reframe/crop: retained {retained_frac:.1%} of source area "
            f"(box [{best_box.x}, {best_box.y}, {best_box.width}x{best_box.height}], confidence {best_score:.2f})."
            if is_crop
            else "No material spatial crop detected; full frame preserved."
        )

        return CropDetectionResult(
            detected=is_crop,
            confidence=best_score,
            crop_box=best_box if is_crop else None,
            source_resolution=(s_w, s_h),
            edited_resolution=(e_w, e_h),
            area_retained_fraction=round(retained_frac, 4),
            area_omitted_fraction=round(1.0 - retained_frac, 4) if is_crop else 0.0,
            omitted_margins=margins,
            explanation=explanation,
        )

    return CropDetectionResult(
        detected=False,
        confidence=float(max(0.0, best_score)),
        crop_box=None,
        source_resolution=(s_w, s_h),
        edited_resolution=(e_w, e_h),
        area_retained_fraction=1.0,
        area_omitted_fraction=0.0,
        omitted_margins=[],
        explanation="No reliable spatial alignment established between source and edited frames.",
    )


def detect_video_crop(
    source_path: Path,
    edited_path: Path,
    sample_time: float = 2.0,
    min_confidence: float = 0.80,
) -> dict[str, Any]:
    """Detect crop between two video files at a given timestamp."""
    s_frame = extract_frame(source_path, sample_time)
    e_frame = extract_frame(edited_path, sample_time)
    result = detect_crop_in_frames(s_frame, e_frame, min_confidence=min_confidence)
    res_dict = asdict(result)
    res_dict["sample_time"] = sample_time
    return res_dict
