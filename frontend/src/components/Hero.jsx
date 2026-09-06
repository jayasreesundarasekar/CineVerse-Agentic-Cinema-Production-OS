/**
 * Home hero. The right panel starts as tasteful generative-gradient art
 * (no fabricated stock photo); "Generate scene art" swaps in a real
 * Gemini-generated frame from the Visual Universe agent so the hero
 * image is an actual product artifact rather than a placeholder photo.
 */
import React, { useState } from "react";
import { Play, Sparkles } from "lucide-react";
import { api } from "../lib/api.js";
import { Button } from "./ui.jsx";

export default function Hero({ projectId, onStartProject }) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // { mock: bool } | null

  async function generateHeroArt() {
    setLoading(true);
    try {
      const res = await api.generateVisuals({
        project_id: projectId,
        prompt: "A director's chair facing an open ocean at golden hour, film lights framing the shot, cinematic widescreen mood",
        generate_type: "world",
        count: 1,
      });
      setStatus({ mock: res.images?.[0]?.mock ?? true });
    } catch {
      setStatus({ mock: true, error: true });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative overflow-hidden rounded-xl border border-hair bg-surface grid grid-cols-1 md:grid-cols-5">
      <div className="md:col-span-3 px-8 py-10 md:px-10 md:py-12 relative z-10">
        <p className="text-xs tracking-[0.2em] text-skyglow mb-3">WELCOME TO</p>
        <h1 className="font-display text-5xl md:text-6xl bg-clip-text text-transparent bg-cine-gradient mb-3 leading-none">
          Cineverse
        </h1>
        <p className="text-parchment text-lg mb-3">From imagination to the big screen.</p>
        <p className="text-muted text-sm mb-7 max-w-md leading-relaxed">
          AI-powered tools to help you write, visualize, analyze, and bring your
          stories to life — every action here runs a real agent, not a mockup.
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={onStartProject}>
            <Play size={15} /> Start a new project
          </Button>
          <Button variant="ghost" onClick={generateHeroArt} loading={loading}>
            <Sparkles size={15} /> {loading ? "Generating..." : "Generate scene art"}
          </Button>
        </div>
        {status && (
          <p className="text-xs text-muted mt-3">
            {status.error
              ? "Couldn't reach the backend — is it running?"
              : status.mock
              ? "Generated a mock frame — add GEMINI_API_KEY for real art (check Create → Visual Universe)."
              : "Frame generated — open Create → Visual Universe to view it."}
          </p>
        )}
      </div>

      <div className="md:col-span-2 relative min-h-[220px] overflow-hidden">
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(circle at 30% 30%, rgba(124,92,252,0.55), transparent 55%), " +
              "radial-gradient(circle at 75% 60%, rgba(233,75,176,0.5), transparent 55%), " +
              "radial-gradient(circle at 50% 90%, rgba(76,201,240,0.4), transparent 50%), #0B0D17",
          }}
        />
        <div className="absolute inset-0 opacity-[0.08]" style={{
          backgroundImage: "repeating-linear-gradient(0deg, #fff 0px, transparent 1px, transparent 2px)",
        }} />
        <p className="font-script text-2xl md:text-3xl text-parchment/90 absolute bottom-6 right-6 text-right leading-tight -rotate-2">
          Same story.<br />Infinite possibilities.
        </p>
      </div>
    </div>
  );
}
