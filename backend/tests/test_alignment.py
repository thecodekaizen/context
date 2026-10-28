import pytest
from context_core.fixtures import generate
from context_core.alignment import analyze
from context_core.media import probe

@pytest.mark.parametrize('name,kinds',[('copy',set()),('trim',{'omission'}),('omission',{'omission'}),('reorder',{'reordering'}),('repeat',{'omission','repetition'}),('recompressed',set())])
def test_edits(clips,name,kinds):
    result=analyze(clips/'original.mp4',clips/f'{name}.mp4')
    assert result['status']=='matched'
    assert result['coverage']>.9
    assert {f['kind'] for f in result['findings']}==kinds
    for s in result['segments']:
        assert 0<=s['edited_start']<s['edited_end']<=result['edited']['duration']
    if name=='omission':
        gap=result['findings'][0]
        assert abs(gap['source_start']-4)<=.5
        assert abs(gap['source_end']-8)<=.5
    if name in {'copy','recompressed'}:
        for s in result['segments']:
            assert abs(s['edited_start']-s['source_start'])<=.5

def test_unknown(clips):
    result=analyze(clips/'original.mp4',clips/'unknown.mp4')
    assert result['status']=='insufficient_evidence'
    assert not result['findings']

def test_invalid(tmp_path):
    p=tmp_path/'bad.mp4'; p.write_text('not video')
    with pytest.raises(ValueError): probe(p)

def test_ambiguous_static_scene(clips):
    result=analyze(clips/'unknown.mp4',clips/'unknown.mp4')
    assert result['status']=='insufficient_evidence'
    assert result['coverage']==0
