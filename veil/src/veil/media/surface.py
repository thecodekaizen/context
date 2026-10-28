"""Opt-in planar replacement with explicit per-frame geometry and opaque fallback.

Geometry is supplied evidence, not inferred by this renderer. One asset is loaded
once per track. No source texture is copied into the replacement interior.
"""
import hashlib
from pathlib import Path
from typing import Literal
import cv2
import numpy as np
from pydantic import Field
from veil.core.models import StrictModel, FiniteFloat


class SurfaceFrame(StrictModel):
    frame: int = Field(ge=0)
    corners: list[tuple[FiniteFloat, FiniteFloat]] | None = None
    status: Literal['visible', 'occluded', 'uncertain'] = 'visible'


class SurfaceReplacement(StrictModel):
    track_id: str
    asset_path: str
    geometry_source: str
    frames: list[SurfaceFrame]


def perspective(corners, asset_size, image_size):
    """Require cyclic TL/TR/BR/BL identity, convex clockwise image coordinates."""
    points = np.asarray(corners, dtype=np.float32)
    width, height = image_size
    if points.shape != (4, 2) or not np.isfinite(points).all():
        raise ValueError('Expected four finite ordered corners')
    if (points < 0).any() or (points[:, 0] >= width).any() or (points[:, 1] >= height).any():
        raise ValueError('Surface leaves image')
    if not cv2.isContourConvex(points) or cv2.contourArea(points, oriented=True) < 32:
        raise ValueError('Corners must be convex, clockwise and non-degenerate')
    if np.min(np.linalg.norm(np.roll(points, -1, axis=0)-points, axis=1)) < 3:
        raise ValueError('Surface is too narrow')
    aw, ah = asset_size
    if min(aw, ah) < 2:
        raise ValueError('Replacement asset is too small')
    source = np.float32([[0, 0], [aw-1, 0], [aw-1, ah-1], [0, ah-1]])
    matrix = cv2.getPerspectiveTransform(source, points)
    if not np.isfinite(matrix).all() or abs(np.linalg.det(matrix)) < 1e-9:
        raise ValueError('Invalid homography')
    # Reject poles crossing the texture, rather than warping through infinity.
    denominators = source @ matrix[2, :2] + matrix[2, 2]
    if np.min(denominators) <= 1e-6:
        raise ValueError('Unstable projective transform')
    return matrix


def composite_surface(frame, asset, corners, support_box):
    height, width = frame.shape[:2]
    matrix = perspective(corners, (asset.shape[1], asset.shape[0]), (width, height))
    points = np.asarray(corners, dtype=np.float32)
    x1, y1, x2, y2 = support_box
    if (points[:, 0] < x1).any() or (points[:, 0] > x2).any() or (points[:, 1] < y1).any() or (points[:, 1] > y2).any():
        raise ValueError('Corners outside protective support region')
    mask = np.zeros((height, width), np.uint8)
    cv2.fillConvexPoly(mask, np.rint(points).astype(np.int32), 255)
    # Only a scalar illumination adaptation: never copy identifying spatial detail.
    ring = cv2.dilate(mask, np.ones((5, 5), np.uint8))-mask
    brightness = float(np.median(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)[ring > 0])) if np.any(ring) else 150
    gain = np.clip(brightness/150, .75, 1.2)
    adjusted = np.clip(asset.astype(np.float32)*gain, 0, 255).astype(np.uint8)
    warped = cv2.warpPerspective(adjusted, matrix, (width, height), flags=cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_REPLICATE)
    # Interior is fully replaced. Feather only OUTSIDE the surface by one pixel.
    outer = cv2.dilate(mask, np.ones((3, 3), np.uint8))
    alpha = np.where(mask > 0, 1., np.where(outer > 0, .5, 0.)).astype(np.float32)
    frame[:] = np.rint(warped*alpha[..., None]+frame*(1-alpha[..., None])).astype(np.uint8)
    return {'edited_pixels': int(np.count_nonzero(outer)), 'illumination_gain': float(gain)}


class SurfaceRenderer:
    def __init__(self, plans, timeline):
        self.entries = {}
        self.decisions = []
        self.assets = {}
        tracks = {t.id: t for t in timeline.visual_tracks}
        if len(tracks) != len(timeline.visual_tracks):
            raise ValueError('Replacement requires unique protective track identities')
        seen = set()
        for plan in plans:
            if plan.track_id in seen or plan.track_id not in tracks:
                raise ValueError('Replacement must name one unique existing track')
            seen.add(plan.track_id)
            track = tracks[plan.track_id]
            if track.category not in ('license_plate', 'phone_number') or track.action != 'cover':
                raise ValueError('Only opaque-protected plate/text tracks support replacement')
            if len({r.frame for r in track.regions}) != len(track.regions):
                raise ValueError('Duplicate protection frame')
            if len({r.frame for r in plan.frames}) != len(plan.frames):
                raise ValueError('Duplicate surface frame')
            protected = {r.frame: r for r in track.regions}
            if any(f.frame not in protected for f in plan.frames):
                raise ValueError('Surface frame lacks protective fallback geometry')
            path = Path(plan.asset_path)
            asset = cv2.imread(str(path)) if path.is_file() else None
            error = None if asset is not None else 'Replacement asset unavailable'
            self.assets[plan.track_id] = {
                'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest() if asset is not None else None,
                'geometry_source': plan.geometry_source, 'category': track.category}
            geometry = {f.frame: f for f in plan.frames}
            for index, region in protected.items():
                self.entries.setdefault(index, []).append((plan.track_id, asset, geometry.get(index), region.box, error))

    def apply(self, frame, index):
        replaced = set()
        for ident, asset, geometry, box, error in self.entries.get(index, []):
            detail = {}
            reason = error
            if not reason:
                if geometry is None or geometry.corners is None:
                    reason = 'Missing surface geometry'
                elif geometry.status != 'visible':
                    reason = 'Surface is occluded or tracking is uncertain'
                else:
                    try:
                        detail = composite_surface(frame, asset, geometry.corners, box)
                    except (ValueError, cv2.error) as exc:
                        reason = str(exc)
            if reason is None:
                replaced.add(ident)
            self.decisions.append({'track_id': ident, 'frame': index,
                'proposed_strategy': 'natural_replacement',
                'applied_strategy': 'opaque_redaction' if reason else 'natural_replacement',
                'fallback_reason': reason, 'privacy_verification': 'not_run', **detail})
        return replaced

    def report(self):
        return {'assets': self.assets, 'decisions': self.decisions,
            'natural_frames': sum(d['applied_strategy']=='natural_replacement' for d in self.decisions),
            'fallback_frames': sum(d['applied_strategy']=='opaque_redaction' for d in self.decisions),
            'geometry_is_inferred_by_renderer': False, 'needs_human_review': True,
            'limitations': ['Geometry reliability is supplied, not independently established',
                'Occlusion uses opaque fallback; foreground reconstruction is not implemented',
                'Scalar lighting adaptation, no learned reflections or physical motion blur',
                'A rendered replacement is not evidence of privacy or visual quality']}
