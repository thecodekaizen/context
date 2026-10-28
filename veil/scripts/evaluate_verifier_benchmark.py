"""Evaluation only. Loads answer keys after inference; never makes model calls."""
import json,hashlib,argparse
from pathlib import Path
from veil.verification.fusion import merge_ocr

parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('artifacts/verifier-benchmark-001'))
root=parser.parse_args().root
truth=json.loads((root/'evaluation-only/truth.json').read_text())
manifest=json.loads((root/'baseline-started.json').read_text())
for item in manifest['cases']:
 assert hashlib.sha256((root/item['id']/'export.mp4').read_bytes()).hexdigest()==item['sha256']


def score(expected,report):
    predictions=[(exposure['category'],frame['time_ms'],frame['time_ms'])
                 for frame in report['frames'] for exposure in frame['exposures']]
    predictions.extend(('spoken_phone',i['start_ms'],i['end_ms']) for i in report['spoken_phone_intervals'])
    def matches(event,prediction):
        category,start,end=prediction
        return category==event['category'] and (event['start_ms']<=start<event['end_ms'] if start==end else start<event['end_ms'] and end>event['start_ms'])
    hits=[any(matches(event,prediction) for prediction in predictions) for event in expected['events']]
    unexpected=[prediction for prediction in predictions if not any(matches(event,prediction) for event in expected['events'])]
    return {'positive_category_events':len(hits),'detected_category_events':sum(hits),
            'missed_categories':[event['category'] for event,hit in zip(expected['events'],hits) if not hit],
            'unexpected_observation_count':len(unexpected),'negative_clip_false_alarm':not expected['events'] and bool(predictions)}

cases=[]
for name,expected in truth.items():
    folder=root/name
    baseline=json.loads((folder/'audit-0-report.json').read_text())
    dense=json.loads((folder/'dense-ocr.json').read_text())
    # Replace sparse OCR with dense observations; leave Spark and Voice results unchanged.
    without_sparse={**baseline,'frames':[{**frame,'exposures':[e for e in frame['exposures'] if e.get('source')!='macos-vision-ocr']} for frame in baseline['frames']]}
    augmented=merge_ocr(without_sparse,dense)
    (folder/'dense-combined-report.json').write_text(json.dumps(augmented,indent=2)+'\n')
    cases.append({'case':name,'kind':expected['kind'],'baseline':score(expected,baseline),
                  'dense_ocr_augmented':score(expected,augmented),'ocr_status':dense['status']})
records=json.loads((root/'baseline-results.json').read_text())
result={'positive_events':sum(len(t['events']) for t in truth.values()),'negative_clips':sum(not t['events'] for t in truth.values()),
        'baseline_hits':sum(c['baseline']['detected_category_events'] for c in cases),
        'dense_ocr_augmented_hits':sum(c['dense_ocr_augmented']['detected_category_events'] for c in cases),
        'baseline_negative_false_alarms':sum(c['baseline']['negative_clip_false_alarm'] for c in cases),
        'dense_negative_false_alarms':sum(c['dense_ocr_augmented']['negative_clip_false_alarm'] for c in cases),
        'model_requests':sum(r['model_requests'] for r in records),'estimated_usd':sum(r['estimated_usd'] for r in records),
        'comparison_additional_model_calls':0,'cases':cases,'input_hashes_verified':True,
        'limitations':['three synthetic clips, five category-events, one negative clip','same fictional portrait and voice assets as original smoke','anticipated sampling blind spot, not held-out model validation','category/time matching, not localization or pixel accuracy','250ms OCR cadence can miss shorter exposures; text pattern false positives possible','not a general recall estimate or zero-leak guarantee']}
(root/'evaluation-only/results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
