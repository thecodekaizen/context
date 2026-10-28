from veil.media.lifetimes import phone_tracklets

MEDIA={'fps':12,'width':360,'height':640,'duration_ms':8000}

def obs(t,phone='202-555-0189',box=(30,40,180,75)):
    return {'category':'phone_number','time_ms':t,'text':phone,'box':box,'source':'macos-vision-ocr'}


def test_transient_observation_never_masks_entire_video():
    tracks,diagnostics=phone_tracklets([obs(2000)],MEDIA)
    frames=[r.frame for r in tracks[0].regions]
    assert min(frames)==21 and max(frames)==27
    assert 0 not in frames and 95 not in frames
    assert diagnostics['tracks'][0]['planned_start_ms']==1750


def test_distinct_numbers_and_long_gaps_remain_separate():
    tracks,_=phone_tracklets([obs(1250),obs(1500),obs(6250,'202-555-0128')],MEDIA)
    assert len(tracks)==2
    tracks,_=phone_tracklets([obs(1250),obs(1500),obs(6250)],MEDIA)
    assert len(tracks)==2


def test_neighbor_envelope_and_velocity_are_derived_from_observations():
    tracks,diagnostics=phone_tracklets([obs(2000),obs(2250,box=(40,45,190,80))],MEDIA)
    middle=next(r for r in tracks[0].regions if r.frame==25)
    assert middle.box==(30,40,190,80)
    assert diagnostics['tracks'][0]['velocity_box_pixels_per_second']==[40,20,40,20]


def test_ocr_geometry_wins_duplicate_contextual_box():
    spark={**obs(2000,box=(0,0,300,100)),'source':'muse-spark-1.3'}
    tracks,_=phone_tracklets([spark,obs(2000)],MEDIA)
    assert len(tracks)==1
    assert tracks[0].regions[0].box==(30,40,180,75)
