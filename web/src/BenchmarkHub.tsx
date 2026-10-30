import { useEffect, useState } from "react";

interface BenchmarkCase {
  id: string;
  benign: boolean;
  expected: number;
  recovered: number;
  predicted: number;
  boundary_errors_seconds: number[];
}
interface BenchmarkReport {
  scope: string;
  interval_recall: number;
  boundary_error_seconds: number;
  benign_false_alarm_rate: number;
  passed: boolean;
  manifest_sha256?: string;
  cases: BenchmarkCase[];
}
type Filter = "all" | "omissions" | "audio_only" | "speed_1_25" | "benign";
const matches = (c: BenchmarkCase, filter: Filter) =>
  filter === "all" ||
  (filter === "benign"
    ? c.benign
    : filter === "omissions"
      ? !c.benign
      : c.id.endsWith(`-${filter}`));

export function BenchmarkHub({
  onLoadDemo,
}: {
  onLoadDemo: (kind: "benchmark" | "crop") => void;
}) {
  const [data, setData] = useState<BenchmarkReport | null>(null);
  const [filter, setFilter] = useState<Filter>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [expanded, setExpanded] = useState<string | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    setData(null);
    fetch("/api/benchmark/results", { signal: controller.signal })
      .then(async (r) => {
        if (!r.ok) throw new Error(`Evaluation unavailable (HTTP ${r.status})`);
        const d = await r.json();
        if (
          !Array.isArray(d.cases) ||
          ![
            d.interval_recall,
            d.boundary_error_seconds,
            d.benign_false_alarm_rate,
          ].every(Number.isFinite)
        )
          throw new Error("Evaluation response is incomplete");
        setData(d);
      })
      .catch((err) => {
        if (!controller.signal.aborted)
          setError(
            err instanceof Error
              ? err.message
              : "Evaluation could not be loaded",
          );
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [attempt]);
  const cases = data?.cases || [];
  const filters: [Filter, string][] = [
    ["all", "All cases"],
    ["omissions", "Omission cases"],
    ["speed_1_25", "Speed controls"],
    ["audio_only", "Audio-only cuts"],
    ["benign", "Benign controls"],
  ];
  const metrics = [
    {
      label: "Interval recall",
      value: data ? `${(data.interval_recall * 100).toFixed(0)}%` : "—",
      note: "Acceptance threshold ≥ 80%",
      tone: "blue",
    },
    {
      label: "Mean boundary delta",
      value: data ? `${data.boundary_error_seconds.toFixed(1)}s` : "—",
      note: "Error against frozen interval labels",
      tone: "",
    },
    {
      label: "Benign false alarms",
      value: data ? `${(data.benign_false_alarm_rate * 100).toFixed(1)}%` : "—",
      note: `${cases.filter((c) => c.benign).length} benign transformation controls`,
      tone: "green",
    },
    {
      label: "Recovered intervals",
      value: data
        ? `${cases.reduce((n, c) => n + c.recovered, 0)} / ${cases.reduce((n, c) => n + c.expected, 0)}`
        : "—",
      note: `${cases.filter((c) => !c.benign).length} positive cases · ${cases.length} total cases`,
      tone: "",
    },
  ];
  return (
    <section className="benchmark-hub-section">
      <div className="evaluation-heading">
        <div>
          <div className="eyebrow">VALIDATION / EXECUTION V1</div>
          <h1>Evidence under examination.</h1>
          <p>
            A frozen contract. Inspectable outcomes. Every interval accounted
            for.
          </p>
        </div>
        <span className={`validation-status ${data?.passed ? "passed" : ""}`}>
          {loading
            ? "◌ LOADING RESULTS"
            : error
              ? "RESULTS UNAVAILABLE"
              : data?.passed
                ? "● GATE PASSED"
                : "● GATE NOT PASSED"}
        </span>
      </div>
      {error && (
        <div className="error" role="alert">
          {error}{" "}
          <button className="quiet" onClick={() => setAttempt((n) => n + 1)}>
            Retry results
          </button>
        </div>
      )}
      <div className="benchmark-metrics-grid">
        {metrics.map((m) => (
          <article className={`benchmark-metric-card ${m.tone}`} key={m.label}>
            <span className="micro-label">{m.label}</span>
            <strong>{m.value}</strong>
            <span>{m.note}</span>
          </article>
        ))}
      </div>
      <div className="evaluation-contract">
        <div>
          <span className="precision-dot" />
          <strong>Frozen evaluation contract</strong>
          <span>
            Controlled CC0 benchmark recordings · not field performance
          </span>
        </div>
        <details>
          <summary>Inspect scope & provenance</summary>
          <p>
            {data?.scope ||
              "Scope will appear when the evaluation report is available."}
          </p>
          {data?.manifest_sha256 && (
            <p className="hash-line">
              MANIFEST SHA-256 / {data.manifest_sha256}
            </p>
          )}
          <p>
            SAM segmentation is a separate saved-response gate. This report
            measures deleted media, not deceptive intent or model accuracy.
          </p>
        </details>
      </div>
      <div className="matrix-heading">
        <div>
          <span className="eyebrow">VERIFICATION MATRIX</span>
          <h2>Every case, in the open.</h2>
        </div>
        <span className="micro-label">
          {cases.filter((c) => matches(c, filter)).length} / {cases.length}{" "}
          CASES
        </span>
      </div>
      <div className="benchmark-table-controls">
        <div className="filter-chips">
          {filters.map(([key, label]) => (
            <button
              key={key}
              aria-pressed={filter === key}
              className={filter === key ? "active" : ""}
              onClick={() => setFilter(key)}
            >
              {label}
              <span>{cases.filter((c) => matches(c, key)).length}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="benchmark-table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Case / source</th>
              <th>Transformation</th>
              <th>Expected</th>
              <th>Recovered</th>
              <th>Boundary delta</th>
              <th>Result</th>
              <th>Evidence</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="matrix-empty">
                  Loading frozen measurements…
                </td>
              </tr>
            )}
            {!loading && !cases.length && (
              <tr>
                <td colSpan={7} className="matrix-empty">
                  No measurements available. No pass status inferred.
                </td>
              </tr>
            )}
            {cases
              .filter((c) => matches(c, filter))
              .map((c) => {
                const passed = c.benign
                  ? c.predicted === 0
                  : c.recovered === c.expected && c.predicted === c.expected;
                const transform = c.id.slice(c.id.indexOf("-") + 1);
                const delta = c.boundary_errors_seconds.length
                  ? (
                      c.boundary_errors_seconds.reduce((a, b) => a + b, 0) /
                      c.boundary_errors_seconds.length
                    ).toFixed(3) + "s"
                  : "—";
                const replay =
                  c.id === "sort-omission"
                    ? "benchmark"
                    : c.id === "cache-crop_omission"
                      ? "crop"
                      : null;
                return (
                  <tr
                    key={c.id}
                    className={expanded === c.id ? "expanded" : ""}
                  >
                    <td>
                      <strong>{c.id}</strong>
                      <small>
                        {c.id.split("-")[0]}.mp4 ·{" "}
                        {c.benign ? "benign control" : "positive case"}
                      </small>
                    </td>
                    <td>{transform.replaceAll("_", " ")}</td>
                    <td>{c.expected}</td>
                    <td>{c.recovered}</td>
                    <td>{delta}</td>
                    <td>
                      <span
                        className={`result-pill ${passed ? "passed" : "failed"}`}
                      >
                        {passed ? "✓ PASS" : "× FAIL"}
                      </span>
                    </td>
                    <td>
                      {replay ? (
                        <button
                          className="quiet matrix-replay"
                          onClick={() => onLoadDemo(replay)}
                        >
                          Replay evidence ↗
                        </button>
                      ) : (
                        <button
                          className="quiet"
                          aria-expanded={expanded === c.id}
                          onClick={() =>
                            setExpanded(expanded === c.id ? null : c.id)
                          }
                        >
                          {expanded === c.id
                            ? "Close trace −"
                            : "Inspect trace +"}
                        </button>
                      )}
                      {expanded === c.id && (
                        <div className="case-trace">
                          Predicted: {c.predicted} · Expected: {c.expected} ·
                          Recovered: {c.recovered}
                          <br />
                          Boundary errors:{" "}
                          {c.boundary_errors_seconds.join(", ") ||
                            "not applicable"}
                          <br />
                          Media replay is not exposed for this case.
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
      <div className="evaluation-footer">
        <span>↳ Reproducible by design</span>
        <code>eval/execution-v1</code>
        <span>
          Results reflect the saved execution report, not a live test run.
        </span>
      </div>
    </section>
  );
}
