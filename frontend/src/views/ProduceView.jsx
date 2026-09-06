import React, { useState } from "react";
import { api } from "../lib/api.js";
import { Panel, Field, TextInput, TextArea, Button, ErrorNote, EmptyState, Badge } from "../components/ui.jsx";

const DEFAULT_LINE_ITEMS = { actors: 2500000, locations: 800000, vfx: 1500000, crew: 1200000, shooting: 2000000, marketing: 3000000 };

export default function ProduceView({ projectId }) {
  const [lineItems, setLineItems] = useState(DEFAULT_LINE_ITEMS);
  const [change, setChange] = useState("Reduce the shooting schedule by 5 days.");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  function updateItem(key, value) {
    setLineItems((prev) => ({ ...prev, [key]: Number(value) || 0 }));
  }

  const total = Object.values(lineItems).reduce((a, b) => a + b, 0);

  async function run() {
    setLoading(true);
    setError("");
    try {
      setResult(await api.runBudget({ project_id: projectId, line_items: lineItems, change_request: change }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const r = result?.result;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
      <Panel eyebrow="Production Budget Simulator" title="Baseline line items (₹)">
        <div className="grid grid-cols-2 gap-3 mb-4">
          {Object.entries(lineItems).map(([key, value]) => (
            <Field key={key} label={key[0].toUpperCase() + key.slice(1)}>
              <TextInput type="number" value={value} onChange={(e) => updateItem(key, e.target.value)} />
            </Field>
          ))}
        </div>
        <p className="text-sm text-muted mb-4">
          Total baseline: <span className="font-mono text-parchment">₹{total.toLocaleString("en-IN")}</span>
        </p>
        <Field label="What if...">
          <TextArea rows={2} value={change} onChange={(e) => setChange(e.target.value)} />
        </Field>
        <Button onClick={run} loading={loading}>Recalculate</Button>
        <ErrorNote message={error} />
      </Panel>

      <Panel eyebrow="Result" title="Cost · risk · quality deltas">
        {r ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted">New total cost</span>
              <span className="font-mono text-lg text-brass">₹{Number(r.total_cost || 0).toLocaleString("en-IN")}</span>
            </div>
            {r.cost_delta_pct !== undefined && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Cost change</span>
                <span className="font-mono text-sm">{r.cost_delta_pct}%</span>
              </div>
            )}
            <DeltaRow label="Risk" value={r.risk_delta} />
            <DeltaRow label="Quality" value={r.quality_delta} />
            {r.audience_impact && (
              <div>
                <p className="text-sm text-muted mb-1">Audience impact</p>
                <p className="text-sm text-parchment">{r.audience_impact}</p>
              </div>
            )}
          </div>
        ) : (
          !loading && <EmptyState title="No simulation run yet" hint="Adjust line items and describe a change to see the impact." />
        )}
      </Panel>
    </div>
  );
}

function DeltaRow({ label, value }) {
  if (!value) return null;
  const text = typeof value === "string" ? value : JSON.stringify(value);
  const tone = /increase/i.test(text) ? "red" : /decrease/i.test(text) ? "teal" : "muted";
  return (
    <div>
      <p className="text-sm text-muted mb-1">{label}</p>
      <Badge tone={tone}>{text}</Badge>
    </div>
  );
}
