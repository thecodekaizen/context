import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const source = await readFile(new URL('../src/data/api-client.ts', import.meta.url), 'utf8');
const javascript = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
}).outputText;

const {
  ApiError,
  createJob,
  getExportUrl,
} = await import(`data:text/javascript;base64,${Buffer.from(javascript).toString('base64')}`);

test('enforces 100 MiB client-side upload guardrail', async () => {
  const fakeLargeFile = {
    name: 'giant.mp4',
    size: 105 * 1024 * 1024, // 105 MiB
  };

  await assert.rejects(
    async () => {
      await createJob(fakeLargeFile);
    },
    (err) => {
      assert.ok(err instanceof ApiError);
      assert.equal(err.status, 422);
      assert.match(err.detail, /100 MiB limit/);
      return true;
    }
  );
});

test('generates correct relative export download URL', () => {
  const url = getExportUrl('job-xyz-123');
  assert.equal(url, '/v1/jobs/job-xyz-123/export');
});
