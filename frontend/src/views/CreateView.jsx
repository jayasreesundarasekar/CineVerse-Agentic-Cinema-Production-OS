import React, { useEffect, useRef, useState } from "react";
import { api } from "../lib/api.js";
import { Panel, Field, TextArea, TextInput, Select, Button, ErrorNote, JsonBlock, EmptyState, Badge } from "../components/ui.jsx";

const VISUAL_TYPES = [
  { value: "location", label: "📍 Location" },
  { value: "character", label: "🎭 Character" },
  { value: "scene", label: "🎬 Scene" },
  { value: "moodboard", label: "🎨 Moodboard" },
  { value: "world", label: "🏙️ World" },
  { value: "shot", label: "🎞️ Shot" },
];

export default function CreateView({ projectId, onDnaExtracted, anchor }) {
  const refs = { screenplay: useRef(null), "visual-universe": useRef(null), "shot-designer": useRef(null) };

  useEffect(() => {
    if (anchor && refs[anchor]?.current) {
      refs[anchor].current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [anchor]);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
      <div ref={refs.screenplay}><ScreenplaySection projectId={projectId} /></div>
      <div ref={refs["visual-universe"]}><VisualUniverseSection projectId={projectId} onDnaExtracted={onDnaExtracted} /></div>
      <div ref={refs["shot-designer"]}><ShotDesignerSection projectId={projectId} /></div>
    </div>
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
  return { loading, error, result, run, setResult };
}

function ScreenplaySection({ projectId }) {
  const [scriptText, setScriptText] = useState(
    "FADE IN: A mysterious coastal town where the protagonist returns after 15 years..."
  );
  const { loading, error, result, run } = useAsync();

  return (
    <Panel eyebrow="Screenplay Agent" title="Structural analysis">
      <Field label="Screenplay text">
        <TextArea rows={6} value={scriptText} onChange={(e) => setScriptText(e.target.value)} />
      </Field>
      <Button onClick={() => run(() => api.analyzeScreenplay({ project_id: projectId, script_text: scriptText }))} loading={loading}>
        Analyze structure
      </Button>
      <ErrorNote message={error} />
      {result && (
        <div className="mt-4">
          <JsonBlock data={result.analysis} />
        </div>
      )}
    </Panel>
  );
}

function VisualUniverseSection({ projectId, onDnaExtracted }) {
  const [scriptText, setScriptText] = useState(
    "A mysterious coastal town where the protagonist returns after 15 years, abandoned colonial buildings, monsoon clouds, wet streets, cinematic thriller atmosphere."
  );
  const [prompt, setPrompt] = useState("");
  const [genType, setGenType] = useState("location");
  const [count, setCount] = useState(4);
  const dna = useAsync();
  const visuals = useAsync();

  async function handleExtract() {
    await dna.run(async () => {
      const res = await api.extractVisualDna({ project_id: projectId, script_text: scriptText });
      if (res.visual_dna?.suggested_prompt) setPrompt(res.visual_dna.suggested_prompt);
      if (onDnaExtracted) onDnaExtracted(res.visual_dna);
      return res;
    });
  }

  return (
    <Panel eyebrow="Visual Universe Generator" title="Extract DNA & generate visuals">
      <Field label="Screenplay excerpt">
        <TextArea rows={3} value={scriptText} onChange={(e) => setScriptText(e.target.value)} />
      </Field>
      <Button variant="ghost" onClick={handleExtract} loading={dna.loading}>Extract visual DNA</Button>
      <ErrorNote message={dna.error} />
      {dna.result && (
        <div className="mt-3 mb-4 grid grid-cols-2 gap-2 text-xs text-muted">
          {Object.entries(dna.result.visual_dna || {}).filter(([k]) => k !== "suggested_prompt").map(([k, v]) => (
            <div key={k} className="bg-void border border-hair rounded px-2 py-1.5">
              <span className="block text-parchment/70 mb-0.5">{k.replace(/_/g, " ")}</span>
              <span className="text-parchment">{Array.isArray(v) ? v.join(", ") : String(v)}</span>
            </div>
          ))}
        </div>
      )}

      <hr className="border-hair my-4" />

      <Field label="Image prompt">
        <TextArea rows={2} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Describe the shot you want generated..." />
      </Field>
      <div className="grid grid-cols-2 gap-3 mb-4">
        <Field label="Category">
          <Select options={VISUAL_TYPES} value={genType} onChange={(e) => setGenType(e.target.value)} />
        </Field>
        <Field label="Variants (1-4)">
          <TextInput type="number" min={1} max={4} value={count} onChange={(e) => setCount(Number(e.target.value))} />
        </Field>
      </div>
      <Button
        onClick={() => visuals.run(() => api.generateVisuals({ project_id: projectId, prompt, generate_type: genType, count }))}
        loading={visuals.loading}
        disabled={!prompt}
      >
        Generate visuals
      </Button>
      <ErrorNote message={visuals.error} />

      {visuals.result ? (
        <div className="grid grid-cols-2 gap-3 mt-4">
          {visuals.result.images.map((img, i) => (
            <ImageCard key={i} img={img} />
          ))}
        </div>
      ) : (
        !visuals.loading && <EmptyState title="No visuals generated yet" hint="Generate 1-4 reference frames for this scene's world." />
      )}
    </Panel>
  );
}

function ImageCard({ img }) {
  const isSvgArtifact = img.storage_uri?.endsWith(".svg");
  return (
    <div className="border border-hair rounded-md overflow-hidden bg-void">
      <div className="aspect-video flex items-center justify-center bg-surface2 text-muted text-xs px-3 text-center">
        {isSvgArtifact ? "mock frame — open artifact to view" : "generated frame"}
      </div>
      <div className="p-2 flex items-center justify-between">
        <span className="text-xs text-parchment">{img.variant}</span>
        <Badge tone={img.mock ? "muted" : "teal"}>{img.mock ? "mock" : "live"}</Badge>
      </div>
    </div>
  );
}

function ShotDesignerSection({ projectId }) {
  const [sceneText, setSceneText] = useState("EXT. TRAIN PLATFORM - DAY. Maya looks toward the departing train, suitcase in hand.");
  const { loading, error, result, run } = useAsync();

  return (
    <Panel eyebrow="AI Shot Designer" title="Scene → shot list">
      <Field label="Scene text">
        <TextArea rows={4} value={sceneText} onChange={(e) => setSceneText(e.target.value)} />
      </Field>
      <Button onClick={() => run(() => api.createStoryboard({ project_id: projectId, scene_text: sceneText }))} loading={loading}>
        Design shots
      </Button>
      <ErrorNote message={error} />
      {result?.shot_plan?.shots ? (
        <div className="mt-4 space-y-2 max-h-80 overflow-auto scrollbar-thin">
          {result.shot_plan.shots.map((shot, i) => (
            <div key={i} className="border border-hair rounded-md px-3 py-2 text-sm">
              <div className="flex justify-between text-parchment font-medium">
                <span>{shot.shot_id || `Shot ${i + 1}`} — {shot.shot_type}</span>
                <span className="font-mono text-xs text-muted">{shot.duration_seconds}s</span>
              </div>
              <p className="text-muted text-xs mt-1">{shot.description}</p>
              <p className="text-xs text-teal mt-1 font-mono">{shot.lens_mm ? `${shot.lens_mm}mm` : ""} {shot.camera_movement}</p>
            </div>
          ))}
        </div>
      ) : (
        result && <JsonBlock data={result} />
      )}
    </Panel>
  );
}
