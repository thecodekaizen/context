"""Turn-level transcription adapter. Numeric transcription is not trusted as exact."""
import json
import wave
import httpx2
from veil.providers.common import save


def transcribe(client, ledger, root, name, audio):
    with wave.open(str(audio)) as wav:
        seconds = wav.getnframes() / wav.getframerate()
    start = ledger.begin(name, 'muse-voice-transcribe-1.0', '/v1/asr/transcribe',
                         'Mono 24 kHz PCM audio extracted from authorized job media')
    try:
        with audio.open('rb') as stream:
            response = httpx2.post('https://api.meta.ai/v1/asr/transcribe',
                headers={'Authorization': 'Bearer ' + client.api_key},
                files={'request': (None, json.dumps({'model': 'muse-voice-transcribe-1.0',
                       'mode': 'ENDPOINTING', 'audioEncoding': 'WAV', 'languageBias': ['English']}), 'application/json'),
                       'audio': ('audio.wav', stream, 'audio/wav')}, timeout=90)
        response.raise_for_status()
        result = response.json()
        if not isinstance(result.get('transcript'), str):
            raise ValueError('Voice returned no transcript')
        save(root / f'{name}.json', result)
        ledger.finish(name, start, estimated_usd=int(seconds)*.18/3600, audio_seconds=seconds)
        return result
    except Exception as exc:
        ledger.fail(name, start, exc)
        raise
