import React, { useEffect, useState } from "react";
import { api } from "../lib/api.js";
import { Panel, Field, TextArea, TextInput, Button, ErrorNote, ScoreBar, EmptyState } from "../components/ui.jsx";
import MultiverseTree from "../components/MultiverseTree.jsx";

export default function SimulateView({ projectId }) {
  const [baseline, setBaseline] = useState("A detective thriller set in a coastal town, protagonist Maya returns after 15 years.");
  const [whatIf, setWhatIf] = useState("What if the ending changes to a twist reveal that Maya's sister staged her own disappearance?");
  const [title, setTitle] = useState("Universe B — Twist Ending");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tree, setTree] = useState({ roots: [], universe_count: 0 });
  const [selected, setSelected] = useState(null);

  async function loadTree() {
    try {
      const data = await api.multiverseTree(projectId);
      setTree(data);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { loadTree(); /* eslint-disable-next-line */ }, [projectId]);

  async function handleSimulate() {
    setLoading(true);
    setError("");
    try {
      await api.runScenarioLab({
        project_id: projectId,
        baseline_summary: baseline,
        what_if: whatIf,
        title,
        register_as_universe: true,
      });
      await loadTree();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
      <Panel eyebrow="Scenario Lab" title="WHAT IF...?" className="xl:col-span-1">
        <Field label="Baseline summary">
          <TextArea rows={3} value={baseline} onChange={(e) => setBaseline(e.target.value)} />
        </Field>
        <Field label="What if...">
          <TextArea rows={3} value={whatIf} onChange={(e) => setWhatIf(e.target.value)} />
        </Field>
        <Field label="Universe title">
          <TextInput value={title} onChange={(e) => setTitle(e.target.value)} />
        </Field>
        <Button onClick={handleSimulate} loading={loading}>Simulate consequences</Button>
        <ErrorNote message={error} />
      </Panel>

      <Panel eyebrow="Cinema Multiverse" title={`Branching universes (${tree.universe_count || 0})`} className="xl:col-span-2">
        {tree.roots?.length ? (
          <MultiverseTree roots={tree.roots} onSelect={setSelected} selectedId={selected?.universe_id} />
        ) : (
          <EmptyState title="No universes yet" hint="Run a scenario above to branch the first alternate universe." />
        )}
        {selected && (
          <div className="mt-4 border border-hair rounded-md p-4">
            <p className="font-display text-base mb-1">{selected.title}</p>
            <p className="text-xs text-muted mb-3">{selected.summary}</p>
            <ScoreBar label="Story" value={selected.story_score} tone="brass" />
            <ScoreBar label="Audience" value={selected.audience_score} tone="teal" />
            <ScoreBar label="Continuity" value={selected.continuity_score} tone="brass" />
            <ScoreBar label="Budget feasibility" value={selected.budget_score} tone="teal" />
          </div>
        )}
      </Panel>
    </div>
  );
}
