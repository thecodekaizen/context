import pytest
from veil.core.models import FrameRegion,AudioInterval,Timeline
from veil.media.redact import covered_bounds

def test_box_validation_and_padding():
 assert covered_bounds((5,5,30,30),40,40)==(0,0,40,40)
 for box in ((10,10,5,20),(0,0,float('nan'),10),(-1,0,10,10)):
  with pytest.raises(ValueError):FrameRegion(frame=0,box=box)

def test_intervals_and_confidence_do_not_fake_precision():
 assert FrameRegion(frame=0,box=(1,1,10,10)).confidence is None
 with pytest.raises(ValueError):AudioInterval(start_ms=100,end_ms=100)
 with pytest.raises(ValueError):FrameRegion(frame=0,box=(1,1,10,10),confidence=1.5)

def test_unknown_provider_fields_rejected():
 with pytest.raises(ValueError):FrameRegion(frame=0,box=(1,1,10,10),provider_secret='unexpected')


def test_field_tracking_fails_closed_without_features(tmp_path):
 import cv2
 import numpy as np
 from veil.media.track import track_field
 path=tmp_path/'blank.mp4'
 writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'mp4v'),10,(80,60))
 for _ in range(5):writer.write(np.zeros((60,80,3),dtype=np.uint8))
 writer.release()
 regions,uncertain=track_field(path,2,[10,10,30,30])
 assert len(regions)==5
 assert uncertain==[0,1,3,4]
 assert regions[2].box==(10,10,30,30)
 assert all(r.box==(0,0,80,60) for r in regions if r.frame!=2)
