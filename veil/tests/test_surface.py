from pathlib import Path
import cv2
import numpy as np
import pytest
from veil.core.models import Timeline, VisualTrack, FrameRegion
from veil.media.surface import perspective, composite_surface, SurfaceReplacement, SurfaceRenderer


def timeline():
    return Timeline(duration_ms=200,fps=10,width=100,height=80,visual_tracks=[
        VisualTrack(id='plate',category='license_plate',source='unit',regions=[
            FrameRegion(frame=i,box=(10,10,90,70)) for i in range(2)])],audio_intervals=[])


def asset(tmp_path):
    path=tmp_path/'asset.png';cv2.imwrite(str(path),np.full((20,40,3),200,np.uint8));return str(path)


def plan(tmp_path, frames):
    return SurfaceReplacement(track_id='plate',asset_path=asset(tmp_path),geometry_source='unit-only',frames=frames)


def test_valid_homography_maps_corners():
    corners=[[15,10],[85,15],[80,65],[10,60]]
    matrix=perspective(corners,(40,20),(100,80))
    mapped=cv2.perspectiveTransform(np.float32([[[0,0],[39,0],[39,19],[0,19]]]),matrix)[0]
    np.testing.assert_allclose(mapped,corners,atol=1e-4)


@pytest.mark.parametrize('corners',[
    [[0,0],[0,0],[0,0],[0,0]],[[10,10],[90,70],[90,10],[10,70]],
    [[10,10],[10,70],[90,70],[90,10]],[[10,10],[110,10],[90,70],[10,70]],
    [[10,10],[90,10],[float('nan'),70],[10,70]],[[10,10],[90,10],[90,11],[10,11]]])
def test_invalid_geometry_rejected(corners):
    with pytest.raises(ValueError):perspective(corners,(40,20),(100,80))


def test_interior_has_no_original_signal_and_outside_unchanged():
    a=np.full((80,100,3),150,np.uint8);b=a.copy();b[20:60,20:80]=255
    texture=np.full((20,40,3),180,np.uint8)
    corners=[[15,15],[85,15],[85,65],[15,65]]
    composite_surface(a,texture,corners,[10,10,90,70]);composite_surface(b,texture,corners,[10,10,90,70])
    assert np.array_equal(a,b)
    assert np.all(a[:13]==150)
    assert np.all(a[:, :13]==150)


def test_missing_geometry_and_occlusion_leave_track_for_opaque_fallback(tmp_path):
    renderer=SurfaceRenderer([plan(tmp_path,[{'frame':0,'status':'occluded'}])],timeline())
    for i in (0,1):assert renderer.apply(np.full((80,100,3),150,np.uint8),i)==set()
    assert renderer.report()['fallback_frames']==2
    assert renderer.report()['natural_frames']==0


def test_invalid_quad_falls_back_without_mutating_original(tmp_path):
    renderer=SurfaceRenderer([plan(tmp_path,[{'frame':0,'corners':[[0,0]]*4}])],timeline())
    frame=np.full((80,100,3),150,np.uint8)
    assert renderer.apply(frame,0)==set()
    assert np.all(frame==150)
    assert renderer.report()['decisions'][0]['fallback_reason']


def test_texture_loaded_once_and_digest_stable(tmp_path):
    p=plan(tmp_path,[{'frame':i,'corners':[[15,15],[85,15],[85,65],[15,65]]} for i in (0,1)])
    renderer=SurfaceRenderer([p],timeline());Path(p.asset_path).unlink()
    outputs=[]
    for i in (0,1):
        f=np.full((80,100,3),150,np.uint8);assert renderer.apply(f,i)=={'plate'};outputs.append(f)
    assert np.array_equal(*outputs)
    assert len(renderer.report()['assets']['plate']['sha256'])==64


def test_unknown_track_duplicate_frame_and_frame_outside_lifetime_rejected(tmp_path):
    p=plan(tmp_path,[])
    with pytest.raises(ValueError):SurfaceRenderer([p,p],timeline())
    p.track_id='unknown'
    with pytest.raises(ValueError):SurfaceRenderer([p],timeline())
    for frames in ([{'frame':0},{'frame':0}],[{'frame':2}]):
        with pytest.raises(ValueError):SurfaceRenderer([plan(tmp_path,frames)],timeline())


def test_missing_asset_is_explicit_fallback(tmp_path):
    p=plan(tmp_path,[]);Path(p.asset_path).unlink();r=SurfaceRenderer([p],timeline())
    assert not r.apply(np.zeros((80,100,3),np.uint8),0)
    assert r.report()['decisions'][0]['fallback_reason']=='Replacement asset unavailable'


def test_original_identifier_checker_finds_partial_values_and_ignores_fictional_asset():
    from veil.verification.original_text import original_matches
    rows=[{'time_ms':0,'text':'202-555-0146'}, {'time_ms':100,'text':'DEMO'},
          {'time_ms':200,'text':'0146'}, {'time_ms':300,'text':'20'}]
    hits=original_matches(rows,['2025550146'])
    assert [r['time_ms'] for r in hits]==[0,200]
    assert hits[0]['full_identifier'] and not hits[1]['full_identifier']
    with pytest.raises(ValueError):original_matches(rows,['12'])


def test_real_renderer_exports_fallback_and_preserves_timing(tmp_path):
    from veil.media.redact import render
    from veil.media.inspect import decode_export
    root=Path(__file__).resolve().parents[1]/'artifacts/natural-surface-001'
    t=Timeline.model_validate_json((root/'timeline.json').read_text())
    p=SurfaceReplacement.model_validate_json((root/'surface-plan.json').read_text())
    p.asset_path=str(root/'replacement.png')
    p.frames=[f for f in p.frames if f.frame not in (24,25)]
    output=tmp_path/'test.mp4'
    result=render(root/'original.mp4',output,t,natural_replacements=[p])
    assert result['natural_replacement']['fallback_frames']==2
    assert result['natural_replacement']['natural_frames']==70
    meta=decode_export(output)
    assert meta['decoded_frames']==72 and meta['duration_ms']==6000 and meta['has_audio']
    assert meta['near_full_frame_black_frames']==[]
    cap=cv2.VideoCapture(str(output));cap.set(cv2.CAP_PROP_POS_FRAMES,24)
    ok,frame=cap.read();cap.release();assert ok
    region=t.visual_tracks[0].regions[24];x1,y1,x2,y2=map(int,region.box)
    assert frame[y1+2:y2-2,x1+2:x2-2].max()<10



def test_tracking_from_one_initialization_stops_on_texture_loss(tmp_path):
    from veil.media.surface_tracking import track_surface
    video=tmp_path/'blank.mp4';writer=cv2.VideoWriter(str(video),cv2.VideoWriter_fourcc(*'mp4v'),10,(100,80))
    for _ in range(4):writer.write(np.full((80,100,3),150,np.uint8))
    writer.release()
    frames,diagnostics=track_surface(video,[[15,15],[85,15],[85,65],[15,65]])
    assert frames[0].status=='visible'
    assert all(f.status=='uncertain' and f.corners is None for f in frames[1:])
    assert all(row.get('reason') for row in diagnostics['frames'][1:])


def test_local_tracking_uses_single_quad_on_development_fixture():
    from veil.media.surface_tracking import track_surface
    root=Path(__file__).resolve().parents[1]/'artifacts/natural-surface-001'
    import json
    seed=json.loads((root/'surface-plan.json').read_text())['frames'][0]['corners']
    frames,report=track_surface(root/'original.mp4',seed)
    assert len(frames)==72
    assert all(f.status=='visible' for f in frames)
    assert report['thresholds_are_heuristics'] is True
