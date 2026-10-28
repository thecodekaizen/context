import { useEffect, useRef, useState } from "react";
import type { Evidence } from "./types";

type Source = { id: string; name: string; duration: number };
type Candidate = { id: string; name: string; coverage: number; score: number };
type Search = {
  status: "matched" | "ambiguous" | "no_match";
  candidates: Candidate[];
};
type Props = {
  disabled: boolean;
  onBusy: (busy: boolean) => void;
  onReset: () => void;
  onEvidence: (e: Evidence) => void;
};

export function SourceCollection({
  disabled,
  onBusy,
  onReset,
  onEvidence,
}: Props) {
  const [sources, setSources] = useState<Source[]>([]);
  const [original, setOriginal] = useState<File | null>(null);
  const [edited, setEdited] = useState<File | null>(null);
  const [operation, setOperation] = useState<"index" | "search" | null>(null);
  const [error, setError] = useState("");
  const [search, setSearch] = useState<Search | null>(null);
  const [notice, setNotice] = useState("");
  const sourceInput = useRef<HTMLInputElement>(null);
  const locked = disabled || operation !== null;

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/library", { signal: controller.signal })
      .then(async (r) => {
        if (!r.ok) throw Error("Could not load the local collection.");
        const data = await r.json();
        setSources(data.sources);
      })
      .catch((err) => {
        if (!controller.signal.aborted)
          setError(
            err instanceof Error ? err.message : "Collection unavailable",
          );
      });
    return () => controller.abort();
  }, []);

  async function submit(kind: "index" | "search") {
    const file = kind === "index" ? original : edited;
    if (!file || locked) return;
    setOperation(kind);
    onBusy(true);
    setError("");
    setNotice("");
    setSearch(null);
    if (kind === "search") onReset();
    try {
      const body = new FormData();
      body.append(kind === "index" ? "original" : "edited", file);
      const response = await fetch(
        kind === "index" ? "/api/library" : "/api/library/search",
        { method: "POST", body },
      );
      const data = await response.json();
      if (!response.ok)
        throw Error(
          typeof data.detail === "string"
            ? data.detail
            : "Collection request failed.",
        );
      if (kind === "index") {
        setSources((current) =>
          current.some((s) => s.id === data.id) ? current : [...current, data],
        );
        setNotice(`Indexed ${data.name}. Ready to search.`);
        setOriginal(null);
        if (sourceInput.current) sourceInput.current.value = "";
      } else {
        setSearch(data.search);
        if (data.evidence) onEvidence(data.evidence);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Collection request failed.",
      );
    } finally {
      setOperation(null);
      onBusy(false);
    }
  }

  return (
    <section className="collection" aria-label="Local source collection">
      <div className="collection-heading">
        <div>
          <div className="eyebrow">
            SOURCE DISCOVERY / YOUR LOCAL COLLECTION
          </div>
          <h2>One edit. Find its source.</h2>
          <p>
            Add original recordings once. Search them with a published clip.
          </p>
        </div>
        <span className="chip">{sources.length} / 20 SOURCES</span>
      </div>
      <div className="collection-forms">
        <div>
          <label htmlFor="library-original">Add an original recording</label>
          <div className="collection-action">
            <input
              id="library-original"
              ref={sourceInput}
              type="file"
              accept="video/*"
              disabled={locked}
              onChange={(e) => setOriginal(e.target.files?.[0] || null)}
            />
            <button
              className="quiet"
              disabled={locked || !original}
              onClick={() => submit("index")}
            >
              {operation === "index" ? "Indexing…" : "Add to collection"}
            </button>
          </div>
        </div>
        <div>
          <label htmlFor="library-edit">Find the source of an edit</label>
          <div className="collection-action">
            <input
              id="library-edit"
              type="file"
              accept="video/*"
              disabled={locked}
              onChange={(e) => setEdited(e.target.files?.[0] || null)}
            />
            <button
              disabled={locked || !edited || sources.length === 0}
              onClick={() => submit("search")}
            >
              {operation === "search"
                ? "Matching sources…"
                : "Search collection ↗"}
            </button>
          </div>
        </div>
      </div>
      {sources.length > 0 && (
        <details>
          <summary>Indexed recordings</summary>
          <ul className="source-list">
            {sources.map((s) => (
              <li key={s.id}>
                <span>{s.name}</span>
                <small>{s.duration.toFixed(1)}s</small>
              </li>
            ))}
          </ul>
        </details>
      )}
      {operation && (
        <p role="status">
          {operation === "index"
            ? "Extracting and caching source fingerprints…"
            : "Comparing the edit against indexed source sequences…"}
        </p>
      )}
      {notice && (
        <p role="status" className="blue">
          {notice}
        </p>
      )}
      {error && (
        <p role="alert" className="review-error">
          {error}
        </p>
      )}
      {search && (
        <div className="search-result" role="status">
          <h3>
            {search.status === "matched"
              ? "Source selected from your collection"
              : search.status === "ambiguous"
                ? "More than one source fits this edit"
                : "No supported source match"}
          </h3>
          <p>
            {search.status === "matched"
              ? "Explore the reconstructed sequence below."
              : search.status === "ambiguous"
                ? "These recordings are too similar to choose automatically. Compare a known original using the upload controls above."
                : "Try a different original recording. Low coverage is not evidence that the video is fabricated."}
          </p>
          <ol>
            {search.candidates.slice(0, 5).map((c) => (
              <li key={c.id}>
                <span>{c.name}</span>
                <span>{Math.round(c.coverage * 100)}% aligned</span>
              </li>
            ))}
          </ol>
        </div>
      )}
      <small className="collection-note">
        Search covers your provided recordings. It does not search the internet.
        Similar candidates remain unresolved.
      </small>
    </section>
  );
}
