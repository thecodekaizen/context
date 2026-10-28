import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const source = await readFile(new URL('../src/data/recorded-example.ts', import.meta.url), 'utf8');
const javascript = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
}).outputText;

const {
  RECORDED_MEDIA_PATHS,
  RECORDED_FINDINGS,
  RECORDED_VERIFICATION_HERO,
  RECORDED_RECEIPT,
} = await import(`data:text/javascript;base64,${Buffer.from(javascript).toString('base64')}`);

test('preserves all four MP4 progression stages with honest labels', () => {
  assert.equal(RECORDED_MEDIA_PATHS.source.url, '/artifacts/input.mp4');
  assert.equal(RECORDED_MEDIA_PATHS.redacted.url, '/artifacts/redacted.mp4');
  assert.equal(RECORDED_MEDIA_PATHS.repaired.url, '/artifacts/repaired.mp4');
  assert.equal(RECORDED_MEDIA_PATHS.protected.url, '/artifacts/protected.mp4');

  assert.match(RECORDED_MEDIA_PATHS.redacted.label, /omitted printed phone/i);
  assert.match(RECORDED_MEDIA_PATHS.repaired.label, /rejected/i);
  assert.match(RECORDED_MEDIA_PATHS.protected.label, /corrected export/i);
});

test('findings preserve null provider confidence and honest status labels', () => {
  for (const finding of RECORDED_FINDINGS) {
    // Providers did not return confidence scores; never invent percentages
    assert.equal(finding.confidence, null, `Finding ${finding.id} must have null confidence`);
    assert.ok(finding.start_ms >= 0);
    assert.ok(finding.end_ms > finding.start_ms);
  }

  const residual = RECORDED_FINDINGS.find((f) => f.id === 'phone-residual-01');
  assert.ok(residual, 'Phone residual finding must exist');
  assert.equal(residual.status, 'unprotected_residual');
  assert.equal(residual.start_ms, 7500);
});

test('hero verification preserves failed single-digit repair and stated 3-sample audit scope', () => {
  assert.equal(RECORDED_VERIFICATION_HERO.exposedTimestamp_ms, 7500);
  assert.equal(RECORDED_VERIFICATION_HERO.exposedTimestamp_label, '00:07.500');

  // Must not claim first-attempt success: failed single-digit repair must be present
  assert.ok(RECORDED_VERIFICATION_HERO.rejectedRepairImageUrl.includes('repaired-sample.jpg'));
  assert.match(RECORDED_VERIFICATION_HERO.rejectedRepairReason, /only segmented one digit/i);

  // Exactly 3 sampled frames
  assert.equal(RECORDED_VERIFICATION_HERO.sampledPasses.length, 3);
  assert.equal(RECORDED_VERIFICATION_HERO.sampledPasses[0].timestamp_s, 2.0);
  assert.equal(RECORDED_VERIFICATION_HERO.sampledPasses[1].timestamp_s, 7.5);
  assert.equal(RECORDED_VERIFICATION_HERO.sampledPasses[2].timestamp_s, 16.0);

  // Mandatory non-absolute scope disclaimer
  assert.match(
    RECORDED_VERIFICATION_HERO.scopeDisclaimer,
    /Other frames may contain missed exposures/i,
    'Must disclose that unsampled frames may contain exposures'
  );
  assert.doesNotMatch(RECORDED_VERIFICATION_HERO.scopeDisclaimer, /100%|zero leaks|certified/i);
});

test('audit receipt records limitations without claiming zero leaks', () => {
  assert.ok(RECORDED_RECEIPT.input_sha256);
  assert.ok(RECORDED_RECEIPT.output_sha256);
  assert.equal(RECORDED_RECEIPT.verified_samples_count, 3);
  assert.ok(RECORDED_RECEIPT.model_calls_estimated_cost_usd <= 0.25);

  const lims = RECORDED_RECEIPT.limitations.join(' ');
  assert.match(lims, /not a real-camera benchmark/i);
  assert.match(lims, /Voice transcription misread/i);
  assert.match(lims, /does not guarantee zero leaks/i);
});
