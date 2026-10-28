"""Combine independently observed export pixels; never infer hidden intervals."""
from copy import deepcopy


def merge_ocr(report, ocr):
    result=deepcopy(report)
    result['independent_ocr']=ocr
    by_time={frame['time_ms']:frame for frame in result['frames']}
    for finding in ocr.get('findings',[]):
        timestamp=finding['time_ms']
        frame=by_time.setdefault(timestamp,{'time_ms':timestamp,'exposures':[]})
        frame['exposures'].insert(0,{key:value for key,value in finding.items() if key!='time_ms'})
    result['frames']=sorted(by_time.values(),key=lambda frame:frame['time_ms'])
    if ocr.get('findings'):result['status']='residual_observed'
    result['check_status']={
        'spark':'completed',
        'voice':'completed',
        'independent_ocr':ocr['status'],
    }
    # Missing independent checks remain explicit even when other samples look clear.
    result['checks_complete']=ocr['status']=='completed'
    if not result['checks_complete'] and result['status']!='residual_observed':
        result['status']='review_incomplete'
    return result
