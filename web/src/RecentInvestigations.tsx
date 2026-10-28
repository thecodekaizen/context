import { useEffect, useState } from "react";
import type { Evidence, Review } from "./types";
type Case = {
  id: string;
  source_name: string;
  coverage: number;
  finding_count: number;
};
type Props = {
  currentId?: string;
  disabled: boolean;
  onRestore: (e: Evidence, r: Review | null) => void;
  onBusy: (busy: boolean) => void;
};

export function RecentInvestigations({
  currentId,
  disabled,
  onRestore,
  onBusy,
}: Props) {
  const [cases, setCases] = useState<Case[]>([]),
    [loading, setLoading] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/investigations", { signal: controller.signal })
      .then(async (r) => {
        if (!r.ok) throw Error("Could not load saved investigations.");
        const data = await r.json();
        setCases(data.investigations);
      })
      .catch((err) => {
        if (!controller.signal.aborted)
          setError(err instanceof Error ? err.message : "History unavailable");
      });
    return () => controller.abort();
  }, [currentId]);
  async function restore(id: string) {
    if (disabled || loading) return;
    setLoading(true);
    onBusy(true);
    setError("");
    try {
      const r = await fetch(`/api/investigations/${id}`);
      const data = await r.json();
      if (!r.ok)
        throw Error(
          typeof data.detail === "string"
            ? data.detail
            : "Investigation unavailable",
        );
      onRestore(data.evidence, data.reviews[0] || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Restore failed");
    } finally {
      setLoading(false);
      onBusy(false);
    }
  }
  if (cases.length === 0 && !error) return null;
  return (
    <section className="recent" aria-label="Saved investigations">
      <details>
        <summary>
          Saved investigations <span>{cases.length}</span>
        </summary>
        <div className="recent-list">
          {cases.map((c) => (
            <button
              className="quiet recent-case"
              key={c.id}
              disabled={disabled || loading}
              onClick={() => restore(c.id)}
              aria-current={currentId === c.id ? "true" : undefined}
            >
              <span>
                {c.source_name}
                <small>
                  {c.id === "demo" ? "Generated demo" : c.id.slice(0, 8)}
                </small>
              </span>
              <span>
                {Math.round(c.coverage * 100)}% aligned · {c.finding_count}{" "}
                findings
              </span>
            </button>
          ))}
        </div>
      </details>
      {error && (
        <p role="alert" className="review-error">
          {error}
        </p>
      )}
    </section>
  );
}
