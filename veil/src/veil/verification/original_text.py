"""Check original identifiers in independently decoded export OCR, not edit metadata."""
import hashlib
from pathlib import Path
from veil.verification.ocr import inspect_text


def normalized_text(value):
    return ''.join(c for c in value if c.isalnum()).upper()


def original_matches(rows, identifiers, minimum_fragment=4):
    if minimum_fragment < 4:
        raise ValueError('Fragments below four characters are not meaningful privacy tests')
    values=[normalized_text(v) for v in identifiers]
    if not values or any(len(v)<minimum_fragment for v in values):
        raise ValueError('Supply original identifiers with at least four characters')
    hits=[]
    for row in rows:
        observed=normalized_text(row['text'])
        for index,value in enumerate(values):
            fragments=sorted({value[i:i+minimum_fragment] for i in range(len(value)-minimum_fragment+1)} &
                             {observed[i:i+minimum_fragment] for i in range(max(0,len(observed)-minimum_fragment+1))})
            if fragments:
                hits.append({'time_ms':row['time_ms'],'original_identifier_index':index,
                    'full_identifier':value in observed,'matching_fragments':fragments,'observed_text':row['text']})
    return hits


def audit_original_text(export: Path, frames, identifiers, width, height, cache: Path):
    # Caller supplies separately decoded exported frames; no masks or renderer decisions.
    ocr=inspect_text(frames,width,height,cache,include_text_rows=True)
    hits=original_matches(ocr.get('text_rows',[]),identifiers)
    report={'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),
        'status':'review_incomplete' if ocr['status']!='completed' else
                 ('residual_observed' if hits else 'no_original_identifier_observed_in_checked_frames'),
        'frames_checked':len(frames),'full_identifier_recovered_frames':len({r['time_ms'] for r in hits if r['full_identifier']}),
        'residual_findings':hits,'needs_manual_review':True,
        'scope':'Local independent OCR on supplied exported frames, normalized planted values and contiguous four-character fragments. Not proof against all recovery methods.'}
    return report,ocr
