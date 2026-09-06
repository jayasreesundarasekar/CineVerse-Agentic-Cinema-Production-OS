import React, { useEffect, useRef, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../lib/api.js";
import { Panel, Field, TextArea, TextInput, Button, ErrorNote, EmptyState, Badge, JsonBlock } from "../components/ui.jsx";

const SEVERITY_TONE = { critical: "red", moderate: "brass", minor: "muted" };

export default function AnalyzeView({ projectId, anchor }) {
  const refs = { audience: useRef(null), "red-team": useRef(null), characters: useRef(null) };

  useEffect(() => {
    if (anchor && refs[anchor]?.current) {
      refs[anchor].current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [anchor]);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
      <div ref={refs.audience}><AudienceSection projectId={projectId} /></div>
      <div ref={refs["red-team"]}><RedTeamSection projectId={projectId} /></div>
      <div ref={refs.characters} className="xl:col-span-2"><CharacterTwinSection projectId={projectId} /></div>
    </div>
  );
}

function AudienceSection({ projectId }) {
  const [summary, setSummary] = useState("A detective thriller set in a coastal town, protagonist Maya returns after 15 years.");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [projections, setProjections] = useState([]);

  async function run() {
    setLoading(true);
    setError("");
    try {
      const res = await api.runAudience({ project_id: projectId, story_summary: summary });
      setProjections(res.result?.projections || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Panel eyebrow="Audience Simulator · AI projection, not market research" title="Segment appeal">
      <Field label="Story / universe summary">
        <TextArea rows={3} value={summary} onChange={(e) => setSummary(e.target.value)} />
      </Field>
      <Button onClick={run} loading={loading}>Project audience appeal</Button>
      <ErrorNote message={error} />
      {projections.length > 0 ? (
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={projections} margin={{ left: -20 }}>
              <CartesianGrid stroke="#2A2F52" vertical={false} />
              <XAxis dataKey="segment" tick={{ fill: "#8B8FA3", fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fill: "#8B8FA3", fontSize: 11 }} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "#141833", border: "1px solid #2A2F52", fontSize: 12 }} />
              <Bar dataKey="appeal_score" fill="#2E9E97" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        !loading && <EmptyState title="No projection yet" hint="Simulated audience segments, clearly labeled as AI projections." />
      )}
    </Panel>
  );
}

function RedTeamSection({ projectId }) {
  const [context, setContext] = useState("Screenplay: coastal thriller. Budget: baseline. Audience: mixed appeal for 18-24 segment.");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function run() {
    setLoading(true);
    setError("");
    try {
      setResult(await api.runRedTeam({ project_id: projectId, context_bundle: context }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const findings = result?.result?.findings || [];
  const verdict = result?.result?.verdict;

  return (
    <Panel eyebrow="Red Team · adversarial critic" title="Try to kill this project">
      <Field label="Project context bundle">
        <TextArea rows={3} value={context} onChange={(e) => setContext(e.target.value)} />
      </Field>
      <Button variant="danger" onClick={run} loading={loading}>Run red team review</Button>
      <ErrorNote message={error} />

      {result && (
        <div className="mt-4">
          <div className="mb-3">
            <Badge tone={verdict === "greenlight" ? "teal" : verdict === "kill" ? "red" : "brass"}>
              verdict: {verdict}
            </Badge>
          </div>
          {findings.length ? (
            <div className="space-y-2">
              {findings.map((f, i) => (
                <div key={i} className="border border-hair rounded-md px-3 py-2">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge tone={SEVERITY_TONE[f.severity] || "muted"}>{f.severity}</Badge>
                    <span className="text-sm text-parchment">{f.issue}</span>
                  </div>
                  <p className="text-xs text-muted">{f.recommendation}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="No issues found" hint="The red team found nothing worth flagging in this bundle." />
          )}
        </div>
      )}
    </Panel>
  );
}

function useAsync() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  async function run(fn) {
    setLoading(true);
    setError("");
    try {
      setResult(await fn());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }
  return { loading, error, result, run };
}

function CharacterTwinSection({ projectId }) {
  const [name, setName] = useState("Maya");
  const [context, setContext] = useState("Maya is a detective returning to her hometown after 15 years to confront her sister's disappearance.");
  const [decision, setDecision] = useState("Maya abandons the case without explanation.");
  const create = useAsync();
  const check = useAsync();

  return (
    <Panel eyebrow="Character Digital Twin" title="Depth & arcs">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Field label="Character name">
            <TextInput value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <Field label="Context from script">
            <TextArea rows={3} value={context} onChange={(e) => setContext(e.target.value)} />
          </Field>
          <Button variant="ghost" onClick={() => create.run(() => api.createCharacterTwin({ project_id: projectId, name, context_text: context }))} loading={create.loading}>
            Build / update profile
          </Button>
          <ErrorNote message={create.error} />
          {create.result && <div className="mt-3"><JsonBlock data={create.result.profile} /></div>}
        </div>
        <div>
          <Field label="Proposed decision to check">
            <TextArea rows={3} value={decision} onChange={(e) => setDecision(e.target.value)} />
          </Field>
          <Button onClick={() => check.run(() => api.checkCharacterTwin({ project_id: projectId, name, decision_context: decision }))} loading={check.loading}>
            Would {name} really do this?
          </Button>
          <ErrorNote message={check.error} />
          {check.result && <div className="mt-3"><JsonBlock data={check.result.result} /></div>}
        </div>
      </div>
    </Panel>
  );
}
