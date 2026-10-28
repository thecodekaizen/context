"""Conservative visual sequence alignment with explicit ambiguity rejection."""
from .media import RATE, probe, fingerprints, digest
import numpy as np

THRESHOLD = .075

def analyze(original, edited):
    source, published = probe(original), probe(edited)
    st, sf = fingerprints(original)
    et, ef = fingerprints(edited)
    indices, errors, ambiguous = [], [], []
    for frame in ef:
        distances = np.mean(np.abs(sf-frame), axis=1)
        best = int(np.argmin(distances))
        # Near temporal neighbors are expected to look similar; distant ties are ambiguous.
        alternatives = distances[np.abs(st-st[best]) > 1.0]
        tie = bool(len(alternatives) and alternatives.min() < distances[best] + .008)
        indices.append(best if distances[best] <= THRESHOLD and not tie else -1)
        errors.append(float(distances[best]))
        ambiguous.append(tie)
    segments = []
    start = 0
    def emit(a,b):
        valid = indices[a] >= 0
        if b-a < 2 and valid:
            valid = False
        segments.append(dict(id=f's{len(segments)}',kind='match' if valid else 'unmatched',edited_start=float(et[a]),edited_end=min(published['duration'],b/RATE),source_start=float(st[indices[a]]) if valid else None,source_end=min(source['duration'],float(st[indices[b-1]])+1/RATE) if valid else None,confidence=round(max(0,1-float(np.mean(errors[a:b]))/THRESHOLD),3) if valid else 0))
    for i in range(1,len(indices)):
        prev, curr = indices[i-1], indices[i]
        continuous = (prev<0 and curr<0) or (prev>=0 and curr>=0 and abs((curr-prev)-1)<=1 and abs((curr-indices[start])-(i-start))<=1)
        if not continuous:
            emit(start,i)
            start=i
    emit(start,len(indices))
    # Reject sub-second islands: isolated visual coincidences are not source evidence.
    for s in segments:
        if s['kind']=='match' and s['edited_end']-s['edited_start'] < .5:
            s.update(kind='unmatched',source_start=None,source_end=None,confidence=0)
    matches = [s for s in segments if s['kind']=='match']
    coverage = sum(s['edited_end']-s['edited_start'] for s in matches)/published['duration']
    findings=[]
    def finding(kind,a,b,**extra):
        findings.append(dict(id=f'f{len(findings)}',kind=kind,source_start=a,source_end=b,**extra))
    covered = sorted((s['source_start'],s['source_end']) for s in matches)
    cursor=0
    if coverage >= .5:
        for a,b in covered:
            if a-cursor >= .5:
                finding('omission',cursor,a)
            cursor=max(cursor,b)
        if source['duration']-cursor >= .5:
            finding('omission',cursor,source['duration'])
        for prev,curr in zip(matches,matches[1:]):
            if curr['source_start'] < prev['source_start']-.25:
                finding('reordering',curr['source_start'],curr['source_end'],edited_start=curr['edited_start'])
        for i,s in enumerate(matches):
            if any(min(s['source_end'],p['source_end'])-max(s['source_start'],p['source_start'])>=.5 for p in matches[:i]):
                finding('repetition',s['source_start'],s['source_end'],edited_start=s['edited_start'])
    return dict(schema_version='1.0',method=dict(name='spatial-color-sequence-v1',sample_rate=RATE,threshold=THRESHOLD,timestamp_tolerance_seconds=.5),source={**source,'sha256':digest(original)},edited={**published,'sha256':digest(edited)},status='matched' if coverage>=.5 else 'insufficient_evidence',coverage=round(coverage,3),segments=segments,findings=findings,limitations=['Visual matching only; audio and speaker intent are not analyzed.','Repeated/static scenes may be rejected as ambiguous.','Cropping, overlays, speed changes and large color changes are not reliably supported.','Omissions include source material before and after the edited clip; an edit alone does not establish misleading intent.'])
