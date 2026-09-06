import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";
import { Panel, Field, TextArea, TextInput, Button, ErrorNote, EmptyState, Badge, ScoreBar } from "../components/ui.jsx";

const VERDICT_TONE = { greenlight: "teal", hold: "brass", pass: "red" };

export default function DecideView({ projectId }) {
  const [title, setTitle] = useState("Universe B — Twist Ending");
  const [summary, setSummary] = useState("A detective thriller with a twist ending revealing the sister staged her disappearance.");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [decisions, setDecisions] = useState([]);

  async function loadDecisions() {
    try {
      const res = await api.listDecisions(projectId);
      setDecisions(res.rows || []);
    } catch {
      /* non-fatal */
    }
  }

  useEffect(() => { loadDecisions(); /* eslint-disable-next-line */ }, [projectId]);

  async function runGreenlight() {
    setLoading(true);
    setError("");
    try {
      const res = await api.runGreenlight({ project_id: projectId, title, universe_summary: summary });
      setResult(res);
      await loadDecisions();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const verdict = result?.executive_decision?.result;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
      <Panel eyebrow="Greenlight Engine" title="Run the full studio board review">
        <Field label="Universe / cut title">
          <TextInput value={title} onChange={(e) => setTitle(e.target.value)} />
        </Field>
        <Field label="Universe summary">
          <TextArea rows={4} value={summary} onChange={(e) => setSummary(e.target.value)} />
        </Field>
        <p className="text-xs text-muted mb-3">
          Chains Audience → Budget → Red Team → Executive verdict in one call.
        </p>
        <Button onClick={runGreenlight} loading={loading}>Run studio board review</Button>
        <ErrorNote message={error} />

        {verdict && (
          <div className="mt-5 border border-hair rounded-md p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-display text-lg">Verdict</span>
              <Badge tone={VERDICT_TONE[verdict.verdict] || "muted"}>{verdict.verdict}</Badge>
            </div>
            <ScoreBar label="Confidence" value={verdict.overall_confidence} tone="brass" />
            <p className="text-sm text-muted mt-2">{verdict.reasoning}</p>
            {verdict.key_factors?.length > 0 && (
              <ul className="mt-3 space-y-1 text-xs text-muted list-disc list-inside">
                {verdict.key_factors.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            )}
          </div>
        )}
      </Panel>

      <Panel eyebrow="Decision Provenance" title="Greenlight decision log">
        {decisions.length ? (
          <div className="space-y-2 max-h-[32rem] overflow-auto scrollbar-thin">
            {decisions.map((d) => (
              <div key={d.decision_id} className="border border-hair rounded-md px-3 py-2">
                <div className="flex items-center justify-between mb-1">
                  <Badge tone={VERDICT_TONE[d.verdict] || "muted"}>{d.verdict}</Badge>
                  <span className="text-[11px] font-mono text-muted">{d.created_at}</span>
                </div>
                <p className="text-xs text-parchment/90">{d.reasoning}</p>
                <p className="text-[11px] font-mono text-muted/70 mt-1">sources: {d.source_run_ids}</p>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No decisions yet" hint="Every greenlight verdict is logged here with its full reasoning trace — explainable, not a black box." />
        )}
      </Panel>
    </div>
  );
}
