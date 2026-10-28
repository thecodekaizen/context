from veil.verification.fusion import merge_ocr


def base():
    return {'frames':[{'time_ms':917,'exposures':[]}],
            'status':'no_exposure_observed_in_samples','spoken_phone_intervals':[]}


def test_ocr_detects_between_model_samples_without_mutating_model_evidence():
    original=base()
    result=merge_ocr(original,{'status':'completed','findings':[
        {'time_ms':2000,'category':'phone_number','box':[10,20,100,40],
         'text':'202-555-0189','source':'macos-vision-ocr'}]})
    assert result['status']=='residual_observed'
    assert [f['time_ms'] for f in result['frames']]==[917,2000]
    assert result['frames'][1]['exposures'][0]['source']=='macos-vision-ocr'
    assert original==base()


def test_missing_independent_signal_is_not_a_pass():
    for status in ('unavailable','failed'):
        result=merge_ocr(base(),{'status':status,'findings':[]})
        assert result['status']=='review_incomplete'
        assert not result['checks_complete']


def test_known_residual_remains_flagged_even_if_ocr_fails():
    original=base();original['status']='residual_observed'
    result=merge_ocr(original,{'status':'failed','findings':[]})
    assert result['status']=='residual_observed'
    assert not result['checks_complete']
